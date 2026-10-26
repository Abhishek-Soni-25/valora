
from app.schemas.valuation import ValuationInput, ValuationResult


def calculate_dcf(data: ValuationInput) -> ValuationResult:
    """
    Calculate a basic FCFF-based discounted cash flow valuation.

    Monetary inputs must use consistent units, e.g. all in INR crore.
    Rates are supplied as percentages, e.g. WACC = 10 means 10%.
    """

    tax_rate = data.tax_rate / 100
    growth_rate = data.revenue_growth / 100
    ebit_margin = data.ebit_margin / 100
    wacc = data.wacc / 100
    terminal_growth = data.terminal_growth / 100

    revenue = data.revenue
    projected_revenue = []
    projected_ebit = []
    projected_cash_flows = []
    discount_factors = []
    present_values = []

    # Project the business over the selected forecast period.
    for year in range(1, data.forecast_years + 1):
        revenue *= 1 + growth_rate
        ebit = revenue * ebit_margin

        # For this first version, D&A, CapEx and change in NWC
        # grow at the same rate as revenue.
        depreciation = data.depreciation * (1 + growth_rate) ** year
        capex = data.capex * (1 + growth_rate) ** year
        change_nwc = data.change_nwc * (1 + growth_rate) ** year

        # Free Cash Flow to the Firm.
        fcff = (
            ebit * (1 - tax_rate)
            + depreciation
            - capex
            - change_nwc
        )

        discount_factor = 1 / ((1 + wacc) ** year)
        present_value = fcff * discount_factor

        projected_revenue.append(revenue)
        projected_ebit.append(ebit)
        projected_cash_flows.append(fcff)
        discount_factors.append(discount_factor)
        present_values.append(present_value)

    # Terminal value using the Gordon Growth Model.
    final_fcff = projected_cash_flows[-1]

    terminal_value = (
        final_fcff * (1 + terminal_growth)
        / (wacc - terminal_growth)
    )

    discounted_terminal_value = (
        terminal_value / ((1 + wacc) ** data.forecast_years)
    )

    enterprise_value = sum(present_values) + discounted_terminal_value

    # Basic EV-to-equity bridge.
    equity_value = enterprise_value + data.cash - data.debt
    value_per_share = equity_value / data.shares

    sensitivity_analysis = calculate_sensitivity(
        projected_cash_flows=projected_cash_flows,
        base_wacc=wacc,
        base_growth=terminal_growth,
    )

    return ValuationResult(
        company_name=data.company_name.strip(),
        currency=data.currency,
        enterprise_value=enterprise_value,
        equity_value=equity_value,
        value_per_share=value_per_share,
        projected_cash_flows=projected_cash_flows,
        projected_revenue=projected_revenue,
        projected_ebit=projected_ebit,
        discount_factors=discount_factors,
        present_values=present_values,
        terminal_value=terminal_value,
        discounted_terminal_value=discounted_terminal_value,
        sensitivity_analysis=sensitivity_analysis,
    )


def calculate_sensitivity(
    projected_cash_flows: list[float],
    base_wacc: float,
    base_growth: float,
) -> dict:
    """Calculate Enterprise Value at different WACC/growth combinations."""

    wacc_values = sorted({
        round(max(0.001, base_wacc + offset), 6)
        for offset in (-0.02, -0.01, 0, 0.01, 0.02)
    })

    growth_values = sorted({
        round(base_growth + offset, 6)
        for offset in (-0.01, -0.005, 0, 0.005, 0.01)
    })

    rows = []

    for wacc in wacc_values:
        values = []

        for growth in growth_values:
            # Gordon Growth requires WACC > terminal growth.
            if wacc <= growth:
                values.append(None)
                continue

            pv_cash_flows = sum(
                fcff / ((1 + wacc) ** year)
                for year, fcff in enumerate(projected_cash_flows, start=1)
            )

            terminal_value = (
                projected_cash_flows[-1] * (1 + growth)
                / (wacc - growth)
            )

            discounted_terminal_value = terminal_value / (
                (1 + wacc) ** len(projected_cash_flows)
            )

            values.append(pv_cash_flows + discounted_terminal_value)

        rows.append({
            "wacc": wacc * 100,
            "enterprise_values": values,
        })

    return {
        "terminal_growth_rates": [value * 100 for value in growth_values],
        "rows": rows,
    }
