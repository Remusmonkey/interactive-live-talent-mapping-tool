"""LinkedIn X-Ray boolean search string generator.

Used by Section 4 (sourcing engine). LinkedIn is the only supported platform —
multi-platform X-Ray strings are an explicit non-goal (see BUILD_SPEC.md).

Template:

    site:linkedin.com/in (
        "VP" OR "Vice President" OR "SVP" OR "Senior Vice President" OR "Senior Director"
    ) "<function_keyword>" ("<company1>" OR "<company2>" OR ...) "<location>"
"""

from __future__ import annotations

LEVEL_TERMS = (
    "VP",
    "Vice President",
    "SVP",
    "Senior Vice President",
    "Senior Director",
)


def build_linkedin_xray(
    function_keyword: str,
    companies: list[str],
    location: str,
) -> str:
    """Build a LinkedIn X-Ray search string for a function + companies + location.

    Args:
        function_keyword: Free-form keyword describing the function
            (e.g., "Product", "Engineering", "FP&A").
        companies: Tier 1 company names to scope the search to.
        location: City, region, or country (e.g., "San Francisco", "United States").

    Returns:
        A Google-search-ready boolean string.
    """
    levels_clause = " OR ".join(f'"{term}"' for term in LEVEL_TERMS)
    companies_clause = " OR ".join(f'"{company}"' for company in companies)
    return (
        f"site:linkedin.com/in ({levels_clause}) "
        f'"{function_keyword}" ({companies_clause}) "{location}"'
    )
