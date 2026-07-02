import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Global Debt Crisis Indicator",
    page_icon="💰",
    layout="wide"
)

@st.cache_data
def load_data():
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    df = pd.read_csv(os.path.join(base, 'debt_features.csv'))
    df_latest = pd.read_csv(os.path.join(base, 'debt_risk_latest.csv'))
    forecast_df = pd.read_csv(os.path.join(base, 'debt_forecasts_2027.csv'))
    return df, df_latest, forecast_df

df, df_latest, forecast_df = load_data()

color_map = {
    'High Risk': '#e74c3c',
    'Elevated Risk': '#f39c12',
    'Moderate Risk': '#3498db',
    'Low Risk': '#2ecc71',
    'Unknown': '#95a5a6'
}

def risk_tier(score):
    if pd.isna(score):
        return 'Unknown'
    elif score >= 75:
        return 'High Risk'
    elif score >= 50:
        return 'Elevated Risk'
    elif score >= 25:
        return 'Moderate Risk'
    else:
        return 'Low Risk'

st.sidebar.title(" Global Debt Crisis Indicator")
st.sidebar.markdown("Tracking debt distress risk across 178 countries using World Bank data.")
st.sidebar.markdown("---")
st.sidebar.markdown("**Data source:** World Bank Open Data API")
st.sidebar.markdown("**Coverage:** 178 countries, 2000-2024")
st.sidebar.markdown("**Model validation MAE:** 11.94 points")

page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Country Explorer", "Country Comparison", "World Map", "Methodology"]
)

if page == "Overview":
    st.title(" Global Debt Crisis Indicator")
    st.markdown(
        "Tracking which countries are approaching debt distress using 5 World Bank indicators — "
        "external debt burden, debt service costs, GDP growth, foreign reserves, and inflation. "
        "Data covers 178 countries through 2024, with forecasts to 2027."
    )
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Countries Tracked", df_latest['country'].nunique())
    col2.metric("High Risk", (df_latest['risk_tier'] == 'High Risk').sum())
    col3.metric("Elevated Risk", (df_latest['risk_tier'] == 'Elevated Risk').sum())
    col4.metric("Worsening Trend", (df_latest['trend_slope'] > 2).sum())

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Risk Tier Distribution (2024)")
        status_counts = df_latest['risk_tier'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color=status_counts.index,
            color_discrete_map=color_map
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 15 Highest Risk Countries (2024)")
        top15 = df_latest.nlargest(15, 'debt_risk_score')[['country', 'debt_risk_score', 'risk_tier']]
        fig = px.bar(
            top15, x='debt_risk_score', y='country',
            orientation='h', color='risk_tier',
            color_discrete_map=color_map,
            labels={'debt_risk_score': 'Risk Score', 'country': ''}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Countries Forecast to Enter High Risk by 2027")
        crossover = forecast_df[
            (forecast_df['current_tier'] != 'High Risk') &
            (forecast_df['forecast_tier'] == 'High Risk')
        ][['country', 'current_score', 'forecast_score', 'current_tier']].copy()
        crossover.columns = ['Country', 'Current Score', '2027 Forecast', 'Current Tier']
        st.dataframe(crossover, use_container_width=True)

    with col2:
        st.subheader("Fastest Worsening Debt Trajectories")
        worsening = df_latest.dropna(subset=['trend_slope']).nlargest(10, 'trend_slope')[
            ['country', 'debt_risk_score', 'risk_tier', 'trend_slope']
        ].copy()
        worsening.columns = ['Country', 'Risk Score', 'Risk Tier', 'Trend (slope)']
        st.dataframe(worsening, use_container_width=True)

elif page == "Country Explorer":
    st.title("Country Explorer")
    st.markdown("Explore any country's debt risk profile, historical trend, and 2027 forecast.")

    countries = sorted(df['country'].unique())
    default_idx = countries.index('Kenya') if 'Kenya' in countries else 0
    selected_country = st.selectbox("Select a country", countries, index=default_idx)

    country_data = df[df['country'] == selected_country].sort_values('year')
    country_latest = df_latest[df_latest['country'] == selected_country]
    country_forecast = forecast_df[forecast_df['country'] == selected_country]

    if len(country_latest) > 0:
        row = country_latest.iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Risk Score (2024)", f"{row['debt_risk_score']:.1f}/100")
        col2.metric("Risk Tier", row['risk_tier'])
        trend_label = "Worsening ↑" if row['trend_slope'] > 0 else "Improving ↓"
        col3.metric("5-Year Trend", trend_label)
        if len(country_forecast) > 0:
            fc = country_forecast.iloc[0]
            col4.metric("2027 Forecast", f"{fc['forecast_score']:.1f}", f"{fc['expected_change']:+.1f} pts")

    st.markdown("---")
    st.subheader(f"{selected_country} — Debt Risk Score Over Time")

    country_valid = country_data.dropna(subset=['debt_risk_score'])
    if len(country_valid) > 0:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=country_valid['year'],
            y=country_valid['debt_risk_score'],
            mode='lines+markers',
            name='Historical Risk Score',
            line=dict(color='#e74c3c', width=2),
            fill='tozeroy',
            fillcolor='rgba(231, 76, 60, 0.1)'
        ))

        if len(country_forecast) > 0:
            fc = country_forecast.iloc[0]
            last_year = country_valid['year'].max()
            last_score = country_valid['debt_risk_score'].iloc[-1]
            fig.add_trace(go.Scatter(
                x=[last_year, 2027],
                y=[last_score, fc['forecast_score']],
                mode='lines+markers',
                name='2027 Forecast',
                line=dict(color='orange', width=2, dash='dash')
            ))

        fig.add_hline(y=75, line_dash='dot', line_color='red',
                      annotation_text='High Risk (75)', annotation_position='right')
        fig.add_hline(y=50, line_dash='dot', line_color='orange',
                      annotation_text='Elevated Risk (50)', annotation_position='right')
        fig.add_hline(y=25, line_dash='dot', line_color='blue',
                      annotation_text='Moderate Risk (25)', annotation_position='right')

        fig.update_layout(
            xaxis_title='Year',
            yaxis_title='Debt Risk Score (0-100)',
            yaxis=dict(range=[0, 100]),
            height=450,
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Raw Indicator Values")
            indicators = country_data[['year', 'external_debt_pct_gni',
                                       'debt_service_pct_exports', 'gdp_growth_pct',
                                       'reserves_months_imports', 'inflation_pct']].dropna(how='all')
            st.dataframe(indicators.sort_values('year', ascending=False), use_container_width=True)

        with col2:
            st.subheader("How This Country Compares")
            if len(country_latest) > 0:
                row = country_latest.iloc[0]
                percentile = (df_latest['debt_risk_score'] < row['debt_risk_score']).mean() * 100
                st.metric("Risk Percentile", f"{percentile:.0f}th")
                st.markdown(f"**{selected_country}** has a higher debt risk score than "
                            f"**{percentile:.0f}%** of tracked countries.")
    else:
        st.warning(f"No debt risk score data available for {selected_country}")

elif page == "Country Comparison":
    st.title("Compare Countries")
    st.markdown("Select 2-4 countries to compare their debt risk trajectories side by side.")

    countries = sorted(df['country'].unique())
    default_countries = [c for c in ['Kenya', 'Argentina', 'Germany', 'Zambia'] if c in countries]
    selected = st.multiselect("Select countries to compare", countries, default=default_countries)

    if len(selected) >= 2:
        fig = go.Figure()
        for country in selected:
            country_data = df[df['country'] == country].sort_values('year').dropna(subset=['debt_risk_score'])
            if len(country_data) > 0:
                fig.add_trace(go.Scatter(
                    x=country_data['year'],
                    y=country_data['debt_risk_score'],
                    mode='lines+markers',
                    name=country,
                    line=dict(width=2)
                ))

        fig.add_hline(y=75, line_dash='dot', line_color='red', annotation_text='High Risk')
        fig.add_hline(y=50, line_dash='dot', line_color='orange', annotation_text='Elevated Risk')
        fig.update_layout(
            title='Debt Risk Score Comparison Over Time',
            xaxis_title='Year',
            yaxis_title='Debt Risk Score (0-100)',
            yaxis=dict(range=[0, 100]),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("2027 Forecast Comparison")
        comp = forecast_df[forecast_df['country'].isin(selected)][
            ['country', 'current_score', 'forecast_score', 'expected_change', 'current_tier', 'forecast_tier']
        ].copy()
        comp.columns = ['Country', 'Current Score', '2027 Forecast', 'Change', 'Current Tier', '2027 Tier']
        st.dataframe(comp, use_container_width=True)
    else:
        st.info("Select at least 2 countries to compare")

elif page == "World Map":
    st.title("Global Debt Risk Map")

    map_data = df_latest.dropna(subset=['debt_risk_score', 'iso_code'])
    fig = px.choropleth(
        map_data,
        locations='iso_code',
        color='debt_risk_score',
        hover_name='country',
        hover_data={'risk_tier': True, 'debt_risk_score': ':.1f', 'iso_code': False},
        color_continuous_scale='RdYlGn_r',
        range_color=[0, 100],
        labels={'debt_risk_score': 'Risk Score (0-100)'},
        title='Global Debt Risk Score by Country (2024)'
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Countries Forecast to Worsen Most by 2027")
    worsening_forecast = forecast_df.nlargest(15, 'expected_change')[
        ['country', 'current_score', 'forecast_score', 'expected_change', 'current_tier', 'forecast_tier']
    ].copy()
    worsening_forecast.columns = ['Country', 'Current Score', '2027 Forecast',
                                   'Expected Change', 'Current Tier', '2027 Tier']
    st.dataframe(worsening_forecast, use_container_width=True)

elif page == "Methodology":
    st.title("Methodology and Limitations")
    st.markdown("""
    ### Data Source
    **World Bank Open Data API** — no API key required, updated annually.
    Coverage: 178 countries, 2000–2024.

    ### The Five Indicators
    | Indicator | World Bank Code | Direction |
    |---|---|---|
    | External Debt as % of GNI | DT.DOD.DECT.GN.ZS | Higher = more risk |
    | Debt Service as % of Exports | DT.TDS.DECT.EX.ZS | Higher = more risk |
    | GDP Growth % | NY.GDP.MKTP.KD.ZG | Lower = more risk |
    | Reserves in Months of Imports | FI.RES.TOTL.MO | Lower = more risk |
    | Inflation % | FP.CPI.TOTL.ZG | Higher = more risk |

    ### Risk Score Construction
    Each indicator is normalized to a 0–100 percentile rank across all countries and years.
    The composite score is the mean of available indicators (minimum 3 of 5 required).

    ### Risk Tiers
    - **High Risk:** score ≥ 75
    - **Elevated Risk:** score 50–74
    - **Moderate Risk:** score 25–49
    - **Low Risk:** score < 25

    ### Forecasting
    Per-country linear trend model, validated by training through 2018 and testing against
    actual 2019–2024 values. **Median validation error: 11.94 points** on a 0–100 scale.
    Forecasts are directional signals, not precise predictions.

    ### Kenya Context
    Kenya scores **54.95/100 (Elevated Risk)** with a slightly improving trend,
    reflecting external debt of 34.99% of GNI and debt service ratio of 27.2% of exports,
    partially offset by 4.7% GDP growth. Forecast to remain Elevated Risk through 2027.

    ### Known Limitations
    - Ireland scores unexpectedly high due to GDP distortions from multinational activity
    - Non-sovereign territories (Guam, Bermuda) appear despite lacking independent debt policy
    - Linear trends cannot anticipate debt restructuring, IMF interventions, or economic shocks
    """)
