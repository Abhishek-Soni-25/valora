
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ValuationInput(BaseModel):
    company_name: str = Field(min_length=1, max_length=100)
    currency: Literal["INR", "USD", "GBP", "EUR"] = "INR"

    revenue: float = Field(ge=0)
    ebit: float
    tax_rate: float = Field(ge=0, le=100)
    depreciation: float = Field(ge=0)
    capex: float = Field(ge=0)
    change_nwc: float

    revenue_growth: float = Field(ge=-100, le=200)
    ebit_margin: float = Field(ge=-100, le=100)

    wacc: float = Field(gt=0, le=100)
    terminal_growth: float = Field(ge=-100, le=100)

    cash: float = Field(ge=0)
    debt: float = Field(ge=0)
    shares: float = Field(gt=0)

    forecast_years: int = Field(ge=1, le=10)

    @model_validator(mode="after")
    def validate_assumptions(self):
        if self.wacc <= self.terminal_growth:
            raise ValueError(
                "WACC must be greater than the terminal growth rate."
            )

        if not self.company_name.strip():
            raise ValueError("Company name cannot be blank.")

        return self


class ValuationResult(BaseModel):
    company_name: str
    currency: str
    enterprise_value: float
    equity_value: float
    value_per_share: float
    projected_cash_flows: list[float]
    projected_revenue: list[float]
    projected_ebit: list[float]
    discount_factors: list[float]
    present_values: list[float]
    terminal_value: float
    discounted_terminal_value: float
    sensitivity_analysis: dict
