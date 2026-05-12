"""Shared scraping primitives for competitor public-board scrapers.

Phase 1A reads from competitor careers pages hosted on Greenhouse
infrastructure (Stripe, Brex, Ramp, Block). Phases 1B and 1C will add
Lever-hosted and Workday-hosted competitor boards. The level + function
classifiers in this module are designed to be reused across all three.

Important: these scrapers read each competitor's PUBLIC-FACING careers
page only. The "Greenhouse" in the URL refers to Greenhouse-the-company
running a SaaS that hosts those public boards. None of this involves
Affirm's internal Greenhouse ATS or candidate data.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

# Canonical level strings written to the Sheet. BUILD_SPEC originally
# locked the scope to SD/VP/SVP, but Phase 1A discovery showed that
# competitor public boards (Stripe, Brex, Block) almost never post those
# titles — senior leadership at fintechs hires through retained search.
# To produce useful data, the scope expanded to also include Director
# and Head of [Function]. SD/VP/SVP remain in the matcher so the scraper
# automatically captures them if competitors ever start publishing them.
# Sourcers triage every row in Pending Review before promoting to Postings.
LEVEL_DIRECTOR = "Director"
LEVEL_SENIOR_DIRECTOR = "Senior Director"
LEVEL_HEAD_OF = "Head of"
LEVEL_VICE_PRESIDENT = "Vice President"
LEVEL_SENIOR_VICE_PRESIDENT = "Senior Vice President"

# Order matters: longer/more-specific patterns must be checked first so
# "Senior Vice President" doesn't get misclassified as "Vice President"
# and "Senior Director" doesn't get misclassified as "Director". Each
# level lists multiple alias regexes — companies use whatever form they
# prefer ("VP" vs "Vice President" vs "Vice-President", etc.).
_LEVEL_PATTERNS = [
    (LEVEL_SENIOR_VICE_PRESIDENT, [
        r"\bSenior\s+Vice[\s-]?President\b",
        r"\bSr\.?\s+Vice[\s-]?President\b",
        r"\bSVP\b",
    ]),
    (LEVEL_VICE_PRESIDENT, [
        r"\bVice[\s-]?President\b",
        r"\bVP\b",
    ]),
    (LEVEL_SENIOR_DIRECTOR, [
        r"\bSenior\s+Director\b",
        r"\bSr\.?\s+Director\b",
    ]),
    (LEVEL_HEAD_OF, [
        # Match "Head of <something>" — the "of" guards against false
        # positives on titles like "Head Chef" or "Head Coach".
        r"\bHead\s+of\b",
        # "Global Head of" / "Regional Head of" — same pattern, just
        # prefixed. Already covered by the above; included for clarity.
        r"\b(?:Global|Regional|Country|US|EU|APAC)\s+Head\s+of\b",
    ]),
    (LEVEL_DIRECTOR, [
        r"\bDirector\b",
    ]),
]

# Function classification keyword map. First match wins, with the ordering
# below acting as the tiebreaker for ambiguous titles (e.g., "VP of Product
# Engineering" hits Product before Engineering). Sourcers can override any
# classification in the Pending Review tab before promoting to Postings.
#
# Order rationale (most-specific first):
#   1. Technical Programs — very specific, low collision risk
#   2. Finance — distinct vocabulary
#   3. Revenue — distinct vocabulary
#   4. Operations — moderately specific
#   5. Product — common word, but rarely misleading in a senior title
#   6. Growth — placed AFTER the established functions so "Head of Sales,
#      Growth" stays Revenue and "Director of Product, Growth/AI" stays
#      Product. Only pure Growth titles (Head of Growth Marketing,
#      Director of Organic Growth) fall through to here.
#   7. Engineering — broadest, catches everything else
#
# Growth note: NOT in the 6 BUILD_SPEC functions today. It's a scraper-only
# extension so Section 1 can surface Growth roles competitors are hiring.
# Sections 2-4 will continue to show only the 6 BUILD_SPEC functions until
# BUILD_SPEC is formally expanded with comp + talent-pool data for Growth.
_FUNCTION_PATTERNS = [
    ("Technical Programs", [
        r"\bTechnical Program(?:s|me)?\b",
        r"\bTPM\b",
        r"\bProgram Management\b",
    ]),
    ("Finance", [
        r"\bFinance\b",
        r"\bFinancial\b",
        r"\bTreasury\b",
        r"\bAccounting\b",
        r"\bFP&A\b",
        r"\bFinancial Planning\b",
        r"\bTax\b",
        r"\bAudit\b",
        r"\bController\b",
    ]),
    ("Revenue", [
        r"\bRevenue\b",
        r"\bSales\b",
        r"\bPartnerships?\b",
        r"\bBusiness Development\b",
        r"\bGo[\s-]?to[\s-]?Market\b",
        r"\bGTM\b",
        r"\bAccount Management\b",
        r"\bCustomer Success\b",
    ]),
    ("Operations", [
        r"\bOperations?\b",
        r"\bRisk\b",
        r"\bCompliance\b",
        r"\bTrust\s*&?\s*Safety\b",
        r"\bFraud\b",
    ]),
    ("Product", [
        r"\bProduct\b",
        r"\bUX\b",
        r"\bDesign\b",
    ]),
    ("Growth", [
        r"\bGrowth\b",
        r"\bPerformance Marketing\b",
        r"\bDemand Gen(?:eration)?\b",
        r"\bUser Acquisition\b",
        r"\bLifecycle\b",
        r"\bRetention\b",
        r"\bAcquisition Marketing\b",
        r"\bIntegrated Campaigns?\b",
    ]),
    ("Engineering", [
        r"\bEngineering\b",
        r"\bSoftware\b",
        r"\bInfrastructure\b",
        r"\bPlatform\b",
        r"\bArchitect(?:ure)?\b",
        r"\bData\s+(?:Engineering|Platform)\b",
        r"\bSecurity\s+(?:Engineering|Operations)\b",
    ]),
]


@dataclass(frozen=True)
class ClassifiedPosting:
    """One leadership posting after level + function classification.

    Mirrors the column shape of the `Postings` tab so a sourcer can
    promote rows from `Scraped — Pending Review` by copy-paste later.
    Two extra columns vs. `Postings` — `raw_title` (the exact title as
    scraped, useful for spotting classifier misses) and `tier` (which
    filter group the company belongs to).
    """
    company: str
    raw_title: str
    title: str
    function: str
    level: str
    location: str
    posted_date: str
    source_url: str
    tier: str


# Tier-specific level whitelists. The classifier returns the canonical
# level for a matched title, but the scraper then filters out any level
# not in the tier's allowed set.
_PRIMARY_ALLOWED_LEVELS = {
    LEVEL_DIRECTOR,
    LEVEL_SENIOR_DIRECTOR,
    LEVEL_HEAD_OF,
    LEVEL_VICE_PRESIDENT,
    LEVEL_SENIOR_VICE_PRESIDENT,
}
# Plain Director skipped for secondary tier because consumer tech
# companies (Lyft, Roblox, Reddit, etc.) frequently use "Director" for
# senior individual contributors (Art Director, Account Director, etc.)
# rather than people management.
_SECONDARY_ALLOWED_LEVELS = {
    LEVEL_SENIOR_DIRECTOR,
    LEVEL_HEAD_OF,
    LEVEL_VICE_PRESIDENT,
    LEVEL_SENIOR_VICE_PRESIDENT,
}


def classify_level(title: str, tier: str = "primary") -> Optional[str]:
    """Return the canonical unabbreviated level for a title, or None.

    Returns None for titles that don't match any leadership pattern OR
    that match a pattern not allowed for the given tier. Manager titles,
    IC titles, and C-suite always return None — those are outside scope.

    Args:
        title: The job title from the scraped board.
        tier: 'primary' (broad filter — Director and above) or
            'secondary' (narrower filter — skip plain Director).
    """
    allowed = _PRIMARY_ALLOWED_LEVELS if tier == "primary" else _SECONDARY_ALLOWED_LEVELS
    for canonical_name, patterns in _LEVEL_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, title, re.IGNORECASE):
                return canonical_name if canonical_name in allowed else None
    return None


def classify_function(title: str) -> str:
    """Return one of the six BUILD_SPEC functions for a title, or 'Other'.

    First-pattern-wins with the priority order documented above. Falls
    back to "Other" when nothing matches — explicitly NOT "Engineering"
    because Engineering would silently absorb Marketing/Comms/Legal/HR
    titles and make the classifier look more accurate than it is. The
    Pending Review tab surfaces "Other" rows so sourcers can manually
    reclassify (or drop) before promoting to Postings.
    """
    for function_name, patterns in _FUNCTION_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, title, re.IGNORECASE):
                return function_name
    return "Other"


# =============================================================================
# Public-board fetchers
# =============================================================================
#
# Each fetcher targets one SaaS-hosted public job board provider and
# returns a *normalized* list of job dicts so the downstream classifier
# stays source-agnostic. Normalized shape:
#
#     {"title": str, "location": str, "posted_date": str, "source_url": str}
#
# Companies expose their public boards through their SaaS provider:
#   - Greenhouse: boards-api.greenhouse.io/v1/boards/<slug>/jobs
#   - Ashby:      api.ashbyhq.com/posting-api/job-board/<slug>
# No authentication required for either — we're consuming the same
# public data anyone visiting the careers page sees in their browser.

_GREENHOUSE_BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
_ASHBY_BOARD_URL = "https://api.ashbyhq.com/posting-api/job-board/{slug}"
_USER_AGENT = "affirm-talent-mapping-tool/1.0 (internal sourcer tool)"
_REQUEST_TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class FetchResult:
    """Outcome of fetching one competitor's job board."""
    slug: str
    name: str
    source: str  # "greenhouse" | "ashby"
    status: str  # "ok" | "http_404" | "http_error" | "network_error" | "parse_error"
    total_jobs: int
    error_message: Optional[str] = None


def _fetch_json(url: str) -> dict:
    """Fetch and parse JSON. Raises on network/parse failures so the
    per-source wrappers can translate them into FetchResult statuses."""
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
        return json.load(response)


def fetch_greenhouse_jobs(slug: str, name: str) -> Tuple[FetchResult, List[dict]]:
    """Pull all jobs from one Greenhouse-hosted competitor board.

    Returns a (FetchResult, normalized_jobs) pair. On any failure the
    FetchResult captures the cause and the jobs list is empty.
    """
    url = _GREENHOUSE_BOARD_URL.format(slug=slug)
    try:
        payload = _fetch_json(url)
    except urllib.error.HTTPError as exc:
        status = "http_404" if exc.code == 404 else "http_error"
        return FetchResult(slug, name, "greenhouse", status, 0, f"HTTP {exc.code}"), []
    except urllib.error.URLError as exc:
        return FetchResult(slug, name, "greenhouse", "network_error", 0, str(exc.reason)), []
    except Exception as exc:
        return FetchResult(slug, name, "greenhouse", "parse_error", 0, repr(exc)), []

    raw_jobs = payload.get("jobs", []) or []
    # Normalize. first_published reflects when the role hit the market;
    # updated_at shifts on any edit (recruiter changes, description
    # tweaks) so it's noisier as a freshness signal.
    normalized = [
        {
            "title": (j.get("title") or "").strip(),
            "location": ((j.get("location") or {}).get("name") or ""),
            "posted_date": (j.get("first_published") or "")[:10],
            "source_url": j.get("absolute_url") or "",
        }
        for j in raw_jobs
    ]
    return FetchResult(slug, name, "greenhouse", "ok", len(raw_jobs), None), normalized


def fetch_ashby_jobs(slug: str, name: str) -> Tuple[FetchResult, List[dict]]:
    """Pull all jobs from one Ashby-hosted competitor board.

    Ashby's posting API uses different field names than Greenhouse but
    exposes the same public job data. Returns the same normalized shape
    as fetch_greenhouse_jobs so downstream code is source-agnostic.
    """
    url = _ASHBY_BOARD_URL.format(slug=slug)
    try:
        payload = _fetch_json(url)
    except urllib.error.HTTPError as exc:
        status = "http_404" if exc.code == 404 else "http_error"
        return FetchResult(slug, name, "ashby", status, 0, f"HTTP {exc.code}"), []
    except urllib.error.URLError as exc:
        return FetchResult(slug, name, "ashby", "network_error", 0, str(exc.reason)), []
    except Exception as exc:
        return FetchResult(slug, name, "ashby", "parse_error", 0, repr(exc)), []

    raw_jobs = payload.get("jobs", []) or []
    # Ashby exposes: title, location (string, not nested), publishedAt
    # (full ISO timestamp), jobUrl (public posting URL). Also has
    # secondaryLocations for multi-location postings — ignored for now;
    # primary location only goes into normalized output.
    normalized = [
        {
            "title": (j.get("title") or "").strip(),
            "location": (j.get("location") or ""),
            "posted_date": (j.get("publishedAt") or "")[:10],
            "source_url": j.get("jobUrl") or "",
        }
        for j in raw_jobs
    ]
    return FetchResult(slug, name, "ashby", "ok", len(raw_jobs), None), normalized


# Registry maps a source name → its fetcher function. Adding a new
# source (Lever, Workday, custom) is one new entry here plus one new
# fetch_* function — no other code needs to change.
FETCHERS = {
    "greenhouse": fetch_greenhouse_jobs,
    "ashby": fetch_ashby_jobs,
}


def fetch_company_jobs(
    slug: str,
    name: str,
    source: str,
) -> Tuple[FetchResult, List[dict]]:
    """Dispatch to the right fetcher for the given source.

    Returns a (FetchResult with status='unknown_source', []) pair if the
    source isn't registered, so the scraper can log it and continue.
    """
    fetcher = FETCHERS.get(source)
    if fetcher is None:
        return (
            FetchResult(slug, name, source, "unknown_source", 0, f"No fetcher for source '{source}'"),
            [],
        )
    return fetcher(slug, name)


def classify_jobs(
    jobs: List[dict],
    company_name: str,
    tier: str,
) -> List[ClassifiedPosting]:
    """Filter + classify normalized jobs into ClassifiedPosting rows.

    Operates on normalized job dicts (output of any fetcher in FETCHERS)
    so this function is source-agnostic. Only jobs whose title matches
    the tier's allowed level filter are returned. Function is best-
    effort with an 'Other' fallback so misclassifications stay visible.
    """
    classified: List[ClassifiedPosting] = []
    for job in jobs:
        raw_title = (job.get("title") or "").strip()
        if not raw_title:
            continue
        level = classify_level(raw_title, tier=tier)
        if level is None:
            continue
        function = classify_function(raw_title)
        classified.append(
            ClassifiedPosting(
                company=company_name,
                raw_title=raw_title,
                title=raw_title,
                function=function,
                level=level,
                location=job.get("location", "") or "",
                posted_date=job.get("posted_date", "") or "",
                source_url=job.get("source_url", "") or "",
                tier=tier,
            )
        )
    return classified


# =============================================================================
# Config loading
# =============================================================================

_DEFAULT_CONFIG_PATH = Path(__file__).parent / "data" / "competitors.json"
_DEFAULT_SOURCE = "greenhouse"  # back-compat for entries missing 'source'


def load_competitor_config(
    config_path: Optional[Path] = None,
) -> Tuple[List[dict], List[dict]]:
    """Load the competitor tier config. Returns (primary_list, secondary_list).

    Each entry has 'slug', 'name', and 'source' keys. Older entries
    without 'source' default to greenhouse for back-compatibility.
    """
    path = config_path or _DEFAULT_CONFIG_PATH
    with open(path, "r") as f:
        cfg = json.load(f)

    def _normalize(entries: List[dict]) -> List[dict]:
        return [
            {**e, "source": e.get("source", _DEFAULT_SOURCE)}
            for e in entries
        ]

    return _normalize(cfg.get("primary", [])), _normalize(cfg.get("secondary", []))
