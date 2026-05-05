"""Smoke tests for the LinkedIn X-Ray string generator."""

from src.xray import LEVEL_TERMS, build_linkedin_xray


def test_linkedin_xray_contains_required_parts() -> None:
    result = build_linkedin_xray(
        function_keyword="Product",
        companies=["Stripe", "Brex"],
        location="San Francisco",
    )

    assert result.startswith("site:linkedin.com/in")
    assert '"Product"' in result
    assert '"Stripe"' in result
    assert '"Brex"' in result
    assert '"San Francisco"' in result
    for level_term in LEVEL_TERMS:
        assert f'"{level_term}"' in result


def test_linkedin_xray_handles_single_company() -> None:
    result = build_linkedin_xray(
        function_keyword="Engineering",
        companies=["Stripe"],
        location="New York",
    )
    assert '("Stripe")' in result
    assert " OR " in result  # level terms still OR-joined
