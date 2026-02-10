import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="ETF Fund Flows Analysis", layout="wide")

@st.cache_data
def load_data():
    xlsx = pd.ExcelFile('ETF_Fund_Flows_5016_Complete.xlsx')
    ark_funds = pd.read_excel(xlsx, sheet_name='ARK funds')
    top100_inflows = pd.read_excel(xlsx, sheet_name='top100 inflows')
    top100_outflows = pd.read_excel(xlsx, sheet_name='top100 outflows')

    # Convert Date columns
    for df in [ark_funds, top100_inflows, top100_outflows]:
        df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

    return ark_funds, top100_inflows, top100_outflows

def create_chart(ark_df, top100_df, chart_title, flow_type, value_type):
    """Create a plotly chart comparing ARK funds vs top100"""
    fig = go.Figure()

    # Get ARK fund columns
    ark_columns = [col for col in ark_df.columns if col != 'Date']
    # Get top100 columns
    top100_columns = [col for col in top100_df.columns if col != 'Date']

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

    # Calculate percentage change if selected
    if value_type == "Percentage Change":
        for col in ark_columns:
            ark_data[col] = ark_data[col].pct_change() * 100
        for col in top100_columns:
            top100_data[col] = top100_data[col].pct_change() * 100

    # Add top100 lines (gray, thinner)
    for col in top100_columns:
        fig.add_trace(go.Scatter(
            x=top100_data['Date'],
            y=top100_data[col],
            mode='lines',
            name=col,
            line=dict(color='rgba(150, 150, 150, 0.3)', width=1),
            hovertemplate=f'{col}<br>Date: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>',
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
            hovertemplate=f'{col}<br>Date: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
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

    y_title = "Flow Value ($ Millions)" if value_type == "Absolute Value" else "Percentage Change (%)"
    if flow_type == "Cumulative":
        y_title = "Cumulative " + y_title

    fig.update_layout(
        title=f"{chart_title} - {flow_type} Flows ({value_type})",
        xaxis_title="Date",
        yaxis_title=y_title,
        height=600,
        hovermode='x unified',
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

    # Load data
    ark_funds, top100_inflows, top100_outflows = load_data()

    # Create tabs for different charts
    tab1, tab2, tab3 = st.tabs(["ARK vs Top100 Inflows", "ARK vs Top100 Outflows", "Download Data"])

    with tab1:
        st.subheader("ARK Funds vs Top 100 Inflows")

        col1, col2 = st.columns(2)
        with col1:
            flow_type_1 = st.radio(
                "Select Flow Type:",
                ["Cumulative", "Daily"],
                key="flow_type_inflows",
                horizontal=True
            )
        with col2:
            value_type_1 = st.radio(
                "Select Value Type:",
                ["Absolute Value", "Percentage Change"],
                key="value_type_inflows",
                horizontal=True
            )

        fig1 = create_chart(ark_funds, top100_inflows, "ARK Funds vs Top 100 Inflows", flow_type_1, value_type_1)
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.subheader("ARK Funds vs Top 100 Outflows")

        col1, col2 = st.columns(2)
        with col1:
            flow_type_2 = st.radio(
                "Select Flow Type:",
                ["Cumulative", "Daily"],
                key="flow_type_outflows",
                horizontal=True
            )
        with col2:
            value_type_2 = st.radio(
                "Select Value Type:",
                ["Absolute Value", "Percentage Change"],
                key="value_type_outflows",
                horizontal=True
            )

        fig2 = create_chart(ark_funds, top100_outflows, "ARK Funds vs Top 100 Outflows", flow_type_2, value_type_2)
        st.plotly_chart(fig2, use_container_width=True)

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
            st.dataframe(ark_funds, use_container_width=True)
        elif preview_option == "Top 100 Inflows":
            st.dataframe(top100_inflows, use_container_width=True)
        else:
            st.dataframe(top100_outflows, use_container_width=True)

if __name__ == "__main__":
    main()
