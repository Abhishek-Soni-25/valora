
import pytest
from pydantic import ValidationError

from app.schemas.valuation import ValuationInput
from app.services.dcf import calculate_dcf


@pytest.fixture
def sample_input():
    return ValuationInput(
        company_name="Example Company",
        currency="INR",
        revenue=1000,
        ebit=150,
        tax_rate=25,
        depreciation=20,
        capex=30,
        change_nwc=5,
        revenue_growth=10,
        ebit_margin=15,
        wacc=10,
        terminal_growth=3,
        cash=100,
        debt=200,
        shares=10,
        forecast_years=5,
    )


def test_forecast_has_correct_number_of_years(sample_input):
    result = calculate_dcf(sample_input)

    assert len(result.projected_revenue) == 5
    assert len(result.projected_ebit) == 5
    assert len(result.projected_cash_flows) == 5


def test_first_year_revenue(sample_input):
    result = calculate_dcf(sample_input)

    assert result.projected_revenue[0] == pytest.approx(1100)


def test_enterprise_value_reconciles(sample_input):
    result = calculate_dcf(sample_input)

    expected = (
        sum(result.present_values)
        + result.discounted_terminal_value
    )

    assert result.enterprise_value == pytest.approx(expected)


def test_equity_value_reconciles(sample_input):
    result = calculate_dcf(sample_input)

    assert result.equity_value == pytest.approx(
        result.enterprise_value + 100 - 200
    )


def test_per_share_value_reconciles(sample_input):
    result = calculate_dcf(sample_input)

    assert result.value_per_share == pytest.approx(
        result.equity_value / 10
    )


def test_terminal_growth_must_be_less_than_wacc():
    with pytest.raises(ValidationError):
        ValuationInput(
            company_name="Example",
            revenue=1000,
            ebit=150,
            tax_rate=25,
            depreciation=20,
            capex=30,
            change_nwc=5,
            revenue_growth=10,
            ebit_margin=15,
            wacc=8,
            terminal_growth=8,
            cash=100,
            debt=200,
            shares=10,
            forecast_years=5,
        )


def test_sensitivity_analysis_is_returned(sample_input):
    result = calculate_dcf(sample_input)

    sensitivity = result.sensitivity_analysis

    assert len(sensitivity["rows"]) == 5
    assert len(sensitivity["terminal_growth_rates"]) == 5
    assert len(sensitivity["rows"][0]["enterprise_values"]) == 5
