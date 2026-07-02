# Global Debt Crisis Indicator

A data science project that tracks and forecasts debt distress risk across 178 countries using World Bank economic indicators — identifying which countries are approaching a debt crisis and which are on a worsening trajectory toward 2027.

## The Problem

Global debt levels have reached historic highs. For developing countries especially, the combination of high external debt, rising debt service costs, slowing growth, and depleted reserves creates conditions for debt distress that can trigger economic crises, currency collapses, and austerity measures that hit the poorest hardest. This project builds a transparent, data-driven early warning system to track which countries are most at risk.

## Live Dashboard

https://global-debt.streamlit.app/

## What the Dashboard Shows

- **Risk tier classification** for 178 countries (High Risk, Elevated Risk, Moderate Risk, Low Risk)
- **Country Explorer** — historical debt risk trend and 2027 forecast for any country
- **Country Comparison** — side-by-side risk trajectory comparison for up to 4 countries
- **World Map** — global choropleth of debt risk scores by country
- **Forecast crossover list** — countries currently not in High Risk but forecast to cross that threshold by 2027

## Key Findings (2024 Data)

- **7 countries** are currently in High Risk territory: West Bank and Gaza, Lebanon, Argentina, Zambia, Lao PDR, Estonia, Mozambique
- **7 additional countries** are forecast to cross into High Risk by 2027: Belarus, Bermuda, Mozambique, Sudan, Suriname, Venezuela, and Guam
- **Kenya** sits at 54.95/100 (Elevated Risk) with a slightly improving trend, driven by a 34.99% external debt-to-GNI ratio and a high debt service ratio of 27.2% of exports — partially offset by 4.7% GDP growth

## The Five Indicators

| Indicator | World Bank Code | Risk Direction |
|---|---|---|
| External Debt as % of GNI | DT.DOD.DECT.GN.ZS | Higher = more risk |
| Debt Service as % of Exports | DT.TDS.DECT.EX.ZS | Higher = more risk |
| GDP Growth % | NY.GDP.MKTP.KD.ZG | Lower = more risk |
| Reserves in Months of Imports | FI.RES.TOTL.MO | Lower = more risk |
| Inflation % | FP.CPI.TOTL.ZG | Higher = more risk |

## How the Risk Score Works

Each indicator is normalized to a 0–100 percentile rank across all countries and years. The composite score is the average of available indicators (minimum 3 of 5 required). Higher scores indicate higher debt distress risk. Countries are then classified into four tiers based on their composite score.

## Forecasting Model

A per-country linear trend model is fitted to historical risk score data and extended to 2027. The model was validated by training on data through 2018 and testing against actual 2019–2024 values.

**Median validation error: 11.94 points** on a 0–100 scale. Debt distress indicators are inherently volatile — debt restructuring, IMF interventions, or currency crises cause non-linear jumps that linear trends cannot anticipate. Forecasts should be read as directional signals identifying countries on a worsening trajectory, not as precise predictions.

## Data Source

**World Bank Open Data API** — free, no API key required, updated annually. Coverage: 178 countries, 2000–2024.

## Tech Stack

- **Data collection:** World Bank Open Data API via Python requests
- **Analysis:** pandas, NumPy, scikit-learn
- **Visualization:** Plotly, Streamlit
- **Deployment:** Streamlit Cloud

## Known Limitations

- Ireland and some high-income countries score unexpectedly high due to GDP distortions from multinational corporate activity — a known issue with national accounts data for these countries
- Non-sovereign territories (Guam, Bermuda) appear in the dataset despite not having independent debt policy — their scores should be interpreted with caution
- Linear trends cannot anticipate policy changes, debt restructuring, or economic shocks — the model captures trajectory, not sudden reversals

