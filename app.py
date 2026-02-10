import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="ETF Fund Flows Analysis", layout="wide")

def parse_aum(aum_str):
    """Parse AUM string like '$868.24B' to millions"""
    if pd.isna(aum_str):
        return None
    aum_str = str(aum_str).replace('$', '').replace(',', '').strip()
    if aum_str in ['-', '', 'N/A', 'nan']:
        return None
    try:
        if aum_str.endswith('B'):
            return float(aum_str[:-1]) * 1000  # Convert B to M
        elif aum_str.endswith('M'):
            return float(aum_str[:-1])
        elif aum_str.endswith('K'):
            return float(aum_str[:-1]) / 1000
        else:
            return float(aum_str)
    except ValueError:
        return None

@st.cache_data
def load_data():
    xlsx = pd.ExcelFile('ETF_Fund_Flows_5016_Complete.xlsx')
    ark_funds = pd.read_excel(xlsx, sheet_name='ARK funds')
    top100_inflows = pd.read_excel(xlsx, sheet_name='top100 inflows')
    top100_outflows = pd.read_excel(xlsx, sheet_name='top100 outflows')

    # Convert Date columns
    for df in [ark_funds, top100_inflows, top100_outflows]:
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

    # Load AUM data
    aum_df = pd.read_csv('etf_screener_data.csv')
    aum_dict = {}
    for _, row in aum_df.iterrows():
        ticker = row['Ticker']
        aum = parse_aum(row['AUM'])
        if aum:
            aum_dict[ticker] = aum

    return ark_funds, top100_inflows, top100_outflows, aum_dict

def get_sorted_tickers(df, ascending=False):
    """Sort tickers by total fund flows"""
    cols = [col for col in df.columns if col != 'Date']
    totals = {col: df[col].sum() for col in cols}
    sorted_tickers = sorted(totals.keys(), key=lambda x: totals[x], reverse=not ascending)
    return sorted_tickers

def create_chart(ark_df, top100_df, chart_title, flow_type, value_type, selected_tickers, aum_dict):
    """Create a plotly chart comparing ARK funds vs top100"""
    fig = go.Figure()

    # Get ARK fund columns
    ark_columns = [col for col in ark_df.columns if col != 'Date']
    # Filter top100 columns based on selection
    top100_columns = [col for col in selected_tickers if col in top100_df.columns]

    # Prepare data based on flow type
    if flow_type == "Cumulative":
        ark_data = ark_df.copy()
        top100_data = top100_df.copy()
        for col in ark_columns:
            ark_data[col] = ark_data[col].cumsum()
        for col in top100_columns:
            top100_data[col] = top100_data[col].cumsum()
    else:  # Daily
        ark_data = ark_df.copy()
        top100_data = top100_df.copy()

    # Calculate percentage of AUM if selected
    if value_type == "% of AUM":
        for col in ark_columns:
            if col in aum_dict and aum_dict[col] > 0:
                ark_data[col] = ark_data[col] / aum_dict[col] * 100
            else:
                ark_data[col] = 0
        for col in top100_columns:
            if col in aum_dict and aum_dict[col] > 0:
                top100_data[col] = top100_data[col] / aum_dict[col] * 100
            else:
                top100_data[col] = 0

    # Add top100 lines (gray, thinner)
    for col in top100_columns:
        fig.add_trace(go.Scatter(
            x=top100_data['Date'],
            y=top100_data[col],
            mode='lines',
            name=col,
            line=dict(color='rgba(150, 150, 150, 0.3)', width=1),
            hovertemplate=f'{col}: %{{y:.2f}}<extra></extra>',
            legendgroup='top100',
            showlegend=False
        ))

    # Add ARK fund lines (colored, thicker, highlighted)
    ark_colors = {
        'ARKK': '#FF6B6B',
        'ARKF': '#4ECDC4',
        'ARKB': '#45B7D1',
        'ARKX': '#96CEB4',
        'ARKG': '#FFEAA7',
        'ARKQ': '#DDA0DD'
    }

    for col in ark_columns:
        color = ark_colors.get(col, '#FF0000')
        fig.add_trace(go.Scatter(
            x=ark_data['Date'],
            y=ark_data[col],
            mode='lines',
            name=col,
            line=dict(color=color, width=3),
            hovertemplate=f'{col}: %{{y:.2f}}<extra></extra>'
        ))

    # Add a dummy trace for legend grouping
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='lines',
        name='Top 100 ETFs',
        line=dict(color='rgba(150, 150, 150, 0.5)', width=1),
        legendgroup='top100'
    ))

    if value_type == "Absolute Value":
        y_title = "Fund Flow ($ Millions)"
    else:
        y_title = "Fund Flow / AUM (%)"

    if flow_type == "Cumulative":
        y_title = "Cumulative " + y_title

    fig.update_layout(
        title=f"{chart_title} - {flow_type} Flows ({value_type})",
        xaxis_title="Date",
        yaxis_title=y_title,
        height=600,
        hovermode='x',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig

def main():
    st.title("ETF Fund Flows Analysis")
    st.markdown("Comparing **ARK Funds** performance against Top 100 ETFs")
    st.caption("Fund flows in $ Millions | AUM converted to Millions (B×1000, M×1)")

    # Load data
    ark_funds, top100_inflows, top100_outflows, aum_dict = load_data()

    # Get sorted tickers
    inflow_tickers_sorted = get_sorted_tickers(top100_inflows, ascending=False)  # Highest first
    outflow_tickers_sorted = get_sorted_tickers(top100_outflows, ascending=True)  # Lowest first

    # Create tabs for different charts
    tab1, tab2, tab3 = st.tabs(["ARK vs Top100 Inflows", "ARK vs Top100 Outflows", "Download Data"])

    with tab1:
        st.subheader("ARK Funds vs Top 100 Inflows")

        col1, col2 = st.columns(2)
        with col1:
            flow_type_1 = st.radio(
                "Flow Type:",
                ["Cumulative", "Daily"],
                key="flow_type_inflows",
                horizontal=True
            )
        with col2:
            value_type_1 = st.radio(
                "Value Type:",
                ["Absolute Value", "% of AUM"],
                key="value_type_inflows",
                horizontal=True
            )

        col_filter, col_chart = st.columns([1, 4])

        with col_filter:
            st.markdown("**Filter Top 100 ETFs**")
            selected_inflows = st.multiselect(
                "Select ETFs:",
                options=inflow_tickers_sorted,
                default=inflow_tickers_sorted,
                key="selected_inflows",
                label_visibility="collapsed"
            )

        with col_chart:
            fig1 = create_chart(ark_funds, top100_inflows, "ARK Funds vs Top 100 Inflows", flow_type_1, value_type_1, selected_inflows, aum_dict)
            st.plotly_chart(fig1, width="stretch")

    with tab2:
        st.subheader("ARK Funds vs Top 100 Outflows")

        col1, col2 = st.columns(2)
        with col1:
            flow_type_2 = st.radio(
                "Flow Type:",
                ["Cumulative", "Daily"],
                key="flow_type_outflows",
                horizontal=True
            )
        with col2:
            value_type_2 = st.radio(
                "Value Type:",
                ["Absolute Value", "% of AUM"],
                key="value_type_outflows",
                horizontal=True
            )

        col_filter, col_chart = st.columns([1, 4])

        with col_filter:
            st.markdown("**Filter Top 100 ETFs**")
            selected_outflows = st.multiselect(
                "Select ETFs:",
                options=outflow_tickers_sorted,
                default=outflow_tickers_sorted,
                key="selected_outflows",
                label_visibility="collapsed"
            )

        with col_chart:
            fig2 = create_chart(ark_funds, top100_outflows, "ARK Funds vs Top 100 Outflows", flow_type_2, value_type_2, selected_outflows, aum_dict)
            st.plotly_chart(fig2, width="stretch")

    with tab3:
        st.subheader("Download Data")

        st.markdown("### Available Datasets")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**ARK Funds Data**")
            csv_ark = ark_funds.to_csv(index=False)
            st.download_button(
                label="Download ARK Funds CSV",
                data=csv_ark,
                file_name="ark_funds_flows.csv",
                mime="text/csv"
            )

        with col2:
            st.markdown("**Top 100 Inflows Data**")
            csv_inflows = top100_inflows.to_csv(index=False)
            st.download_button(
                label="Download Top 100 Inflows CSV",
                data=csv_inflows,
                file_name="top100_inflows.csv",
                mime="text/csv"
            )

        with col3:
            st.markdown("**Top 100 Outflows Data**")
            csv_outflows = top100_outflows.to_csv(index=False)
            st.download_button(
                label="Download Top 100 Outflows CSV",
                data=csv_outflows,
                file_name="top100_outflows.csv",
                mime="text/csv"
            )

        st.markdown("---")
        st.markdown("### Data Preview")

        preview_option = st.selectbox(
            "Select data to preview:",
            ["ARK Funds", "Top 100 Inflows", "Top 100 Outflows"]
        )

        if preview_option == "ARK Funds":
            st.dataframe(ark_funds, width="stretch")
        elif preview_option == "Top 100 Inflows":
            st.dataframe(top100_inflows, width="stretch")
        else:
            st.dataframe(top100_outflows, width="stretch")

if __name__ == "__main__":
    main()
