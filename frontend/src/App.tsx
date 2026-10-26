
import { useState } from "react";
import "./App.css";

type ValuationInput = {
  company_name: string;
  currency: string;
  revenue: number;
  ebit: number;
  tax_rate: number;
  depreciation: number;
  capex: number;
  change_nwc: number;
  revenue_growth: number;
  ebit_margin: number;
  wacc: number;
  terminal_growth: number;
  cash: number;
  debt: number;
  shares: number;
  forecast_years: number;
};

type ValuationResult = {
  enterprise_value: number;
  equity_value: number;
  value_per_share: number;
  projected_cash_flows: number[];
};

const initialInputs: ValuationInput = {
  company_name: "",
  currency: "INR",
  revenue: 1000,
  ebit: 150,
  tax_rate: 25,
  depreciation: 20,
  capex: 30,
  change_nwc: 5,
  revenue_growth: 10,
  ebit_margin: 15,
  wacc: 10,
  terminal_growth: 3,
  cash: 100,
  debt: 200,
  shares: 10,
  forecast_years: 5,
};

function formatValue(value: number, currency: string) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

function App() {
  const [inputs, setInputs] = useState(initialInputs);
  const [result, setResult] = useState<ValuationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function updateInput(
    field: keyof ValuationInput,
    value: string
  ) {
    setInputs((previous) => ({
      ...previous,
      [field]:
        field === "company_name" || field === "currency"
          ? value
          : Number(value),
    }));
    setResult(null);
    setError("");
  }

  async function calculateValuation() {
    setError("");
    setResult(null);

    if (!inputs.company_name.trim()) {
      setError("Please enter a company name.");
      return;
    }

    if (
      inputs.revenue < 0 ||
      inputs.ebit < 0 ||
      inputs.tax_rate < 0 ||
      inputs.tax_rate > 100 ||
      inputs.wacc <= inputs.terminal_growth ||
      inputs.shares <= 0 ||
      inputs.forecast_years < 1 ||
      inputs.forecast_years > 10
    ) {
      setError(
        "Check your inputs. WACC must exceed terminal growth, " +
        "shares must be positive, and the forecast must be 1–10 years."
      );
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        "https://valora-api-53e8.onrender.com/api/valuation/dcf",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(inputs),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Valuation calculation failed.");
      }

      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not connect to the valuation backend."
      );
    } finally {
      setLoading(false);
    }
  }

  const field = (
    label: string,
    key: keyof ValuationInput,
    suffix = "",
    step = "any"
  ) => (
    <label className="field" key={key}>
      <span>{label}</span>
      <div className="input-wrap">
        <input
          type={key === "company_name" || key === "currency" ? "text" : "number"}
          value={inputs[key]}
          step={step}
          onChange={(event) => updateInput(key, event.target.value)}
          required
        />
        {suffix && <span className="suffix">{suffix}</span>}
      </div>
    </label>
  );

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-mark">V</span>
          <span>valora</span>
        </a>
        <span className="topbar-label">DCF VALUATION WORKSPACE</span>
      </header>

      <section className="page-heading">
        <div>
          <p className="eyebrow">FINANCIAL ANALYSIS</p>
          <h1>DCF Valuation Calculator</h1>
          <p className="subtitle">
            Estimate a company's intrinsic value using projected free cash flows.
          </p>
        </div>
        <span className="version-tag">VERSION 1.0</span>
      </section>

      <div className="workspace">
        <section className="form-panel">
          <div className="panel-heading">
            <div>
              <h2>Valuation assumptions</h2>
              <p>Enter your company's financial data and assumptions.</p>
            </div>
            <span className="step-number">01</span>
          </div>

          <div className="form-section">
            <h3>Company information</h3>
            <div className="form-grid">
              {field("Company name", "company_name")}
              <label className="field">
                <span>Reporting currency</span>
                <select
                  value={inputs.currency}
                  onChange={(e) => updateInput("currency", e.target.value)}
                >
                  <option value="INR">INR — Indian Rupee</option>
                  <option value="USD">USD — US Dollar</option>
                  <option value="GBP">GBP — British Pound</option>
                  <option value="EUR">EUR — Euro</option>
                </select>
              </label>
              <label className="field">
                <span>Forecast period</span>
                <select
                  value={inputs.forecast_years}
                  onChange={(e) =>
                    updateInput("forecast_years", e.target.value)
                  }
                >
                  {[3, 5, 7, 10].map((year) => (
                    <option key={year} value={year}>
                      {year} years
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </div>

          <div className="form-section">
            <h3>Base-year financials</h3>
            <p className="section-description">
              Enter values in the same currency units, for example ₹ crore.
            </p>
            <div className="form-grid">
              {field("Revenue", "revenue")}
              {field("EBIT / Operating profit", "ebit")}
              {field("Tax rate", "tax_rate", "%")}
              {field("Depreciation & amortization", "depreciation")}
              {field("Capital expenditure", "capex")}
              {field("Change in net working capital", "change_nwc")}
            </div>
          </div>

          <div className="form-section">
            <h3>Forecast assumptions</h3>
            <div className="form-grid">
              {field("Annual revenue growth", "revenue_growth", "%")}
              {field("EBIT margin", "ebit_margin", "%")}
              {field("WACC / Discount rate", "wacc", "%")}
              {field("Terminal growth rate", "terminal_growth", "%")}
            </div>
          </div>

          <div className="form-section">
            <h3>Equity value adjustments</h3>
            <div className="form-grid">
              {field("Cash & cash equivalents", "cash")}
              {field("Total debt", "debt")}
              {field("Diluted shares outstanding", "shares")}
            </div>
          </div>

          <div className="form-footer">
            <p>All assumptions should be reviewed before relying on results.</p>
            <button
              className="calculate-button"
              onClick={calculateValuation}
              disabled={loading}
            >
              {loading ? "Calculating..." : "Calculate valuation"}
              {!loading && <span aria-hidden="true"> →</span>}
            </button>
          </div>

          {error && <div className="error-message">{error}</div>}
        </section>

        <aside className="results-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">VALUATION OUTPUT</p>
              <h2>Results</h2>
            </div>
            <span className="step-number">02</span>
          </div>

          {!result ? (
            <div className="empty-state">
              <div className="empty-icon">↗</div>
              <h3>Your valuation starts here</h3>
              <p>
                Submit the assumptions to calculate enterprise value,
                equity value and estimated value per share.
              </p>
              <div className="empty-divider" />
              <div className="metric-placeholder">
                <span>Enterprise value</span>
                <strong>—</strong>
              </div>
              <div className="metric-placeholder">
                <span>Equity value</span>
                <strong>—</strong>
              </div>
              <div className="metric-placeholder">
                <span>Value per share</span>
                <strong>—</strong>
              </div>
            </div>
          ) : (
            <div className="results-content">
              <p className="result-company">{inputs.company_name}</p>
              <div className="primary-result">
                <span>Enterprise value</span>
                <strong>
                  {formatValue(result.enterprise_value, inputs.currency)}
                </strong>
              </div>
              <div className="result-metric">
                <span>Equity value</span>
                <strong>
                  {formatValue(result.equity_value, inputs.currency)}
                </strong>
              </div>
              <div className="result-metric">
                <span>Estimated value per share</span>
                <strong>
                  {formatValue(result.value_per_share, inputs.currency)}
                </strong>
              </div>

              <div className="empty-divider" />
              <h3>Projected free cash flows</h3>
              {result.projected_cash_flows.map((cashFlow, index) => (
                <div className="cash-flow-row" key={index}>
                  <span>Year {index + 1}</span>
                  <strong>
                    {formatValue(cashFlow, inputs.currency)}
                  </strong>
                </div>
              ))}
              <p className="result-note">
                Valuation estimates depend on the quality of inputs and
                assumptions. They are not investment advice.
              </p>
            </div>
          )}
        </aside>
      </div>

      <footer className="app-footer">
        <span>VALORA · DCF ANALYSIS</span>
        <span>For analytical and educational use</span>
      </footer>
    </main>
  );
}

export default App;
