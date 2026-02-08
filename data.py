import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Sidebar: Theme Option
# -------------------------------
theme_option = st.sidebar.radio("Select Theme", ["Light Mode", "Dark Mode"])

if theme_option == "Dark Mode":
    bg_color = "#0e1117"
    text_color = "white"
    template = "plotly_dark"
else:
    bg_color = "white"
    text_color = "black"
    template = "plotly_white"

st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.markdown(
    f"""
    <style>
    body {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .stSidebar {{
        background-color: {bg_color};
        color: {text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📊 Stock Dashboard")
st.write("Compare Apple and Netflix stock performance interactively")

# -------------------------------
# Load & Combine CSVs
# -------------------------------
apple = pd.read_csv("AAPL.csv")
netflix = pd.read_csv("NFLX.csv")

apple['Date'] = pd.to_datetime(apple['Date'])
netflix['Date'] = pd.to_datetime(netflix['Date'])

apple['Ticker'] = 'AAPL'
netflix['Ticker'] = 'NFLX'

df = pd.concat([apple, netflix], ignore_index=True)

# -------------------------------
# Sidebar: Stock Selection & Date Range
# -------------------------------
tickers = st.sidebar.multiselect("Select Stocks", df['Ticker'].unique(), default=['AAPL','NFLX'])
start_date = st.sidebar.date_input("Start Date", df['Date'].min())
end_date = st.sidebar.date_input("End Date", df['Date'].max())

filtered_df = df[(df['Ticker'].isin(tickers)) &
                 (df['Date'] >= pd.to_datetime(start_date)) &
                 (df['Date'] <= pd.to_datetime(end_date))]

# -------------------------------
# Normalize Prices to 100
# -------------------------------
normalized_df = filtered_df.copy()
normalized_df['Normalized Close'] = 0
for ticker in tickers:
    stock_data = filtered_df[filtered_df['Ticker']==ticker].sort_values('Date')
    start_price = stock_data['Close'].iloc[0]
    normalized_df.loc[normalized_df['Ticker']==ticker, 'Normalized Close'] = stock_data['Close']/start_price*100

# -------------------------------
# Unified Graphic Chart
# -------------------------------
st.subheader("📈 Stock Performance (Normalized + Actual)")

fig = px.line()

# Add normalized lines
for ticker in tickers:
    stock = normalized_df[normalized_df['Ticker']==ticker]
    fig.add_scatter(x=stock['Date'], y=stock['Normalized Close'], mode='lines+markers',
                    name=f"{ticker} Normalized", line=dict(width=4))

# Add actual close lines as dashed
for ticker in tickers:
    stock = filtered_df[filtered_df['Ticker']==ticker]
    fig.add_scatter(x=stock['Date'], y=stock['Close'], mode='lines',
                    name=f"{ticker} Actual", line=dict(dash='dash', width=2))

fig.update_layout(
    template=template,
    plot_bgcolor=bg_color,
    paper_bgcolor=bg_color,
    font=dict(color=text_color),
    height=700,
    xaxis_title="Date",
    yaxis_title="Price / Normalized Value",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Summary Metrics
# -------------------------------
st.subheader("📊 Summary Metrics")
summary = filtered_df.groupby('Ticker')['Close'].agg(['min','max','mean']).reset_index()
st.dataframe(summary, use_container_width=True)

# -------------------------------
# Save Combined CSV
# -------------------------------
df.to_csv("combined_stock_data.csv", index=False)
st.info("Combined CSV saved as 'combined_stock_data.csv'")
