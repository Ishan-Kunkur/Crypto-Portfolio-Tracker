import requests
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()

# TapTools API Key header
TAPTOOLS_API_KEY = os.getenv("TAPTOOLS_API_KEY")
TAPTOOLS_HEADERS = {"x-api-key": TAPTOOLS_API_KEY}

# TapTools API endpoints
TAPTOOLS_POSITIONS_URL = "https://openapi.taptools.io/api/v1/wallet/portfolio/positions"
TAPTOOLS_QUOTE_URL = "https://openapi.taptools.io/api/v1/token/quote"

# Predefined access codes
ACCESS_CODES = ["DREAMY123", "BAGTRACKER456", "GOAT789"]

# Fetch the current ADA/USD price
def get_ada_usd_price():
    response = requests.get(TAPTOOLS_QUOTE_URL, headers=TAPTOOLS_HEADERS)
    if response.status_code == 200:
        price_data = response.json()
        return float(price_data.get("price", 0))
    else:
        st.error(f"❌ Failed to fetch ADA/USD price: {response.status_code}")
        return 0

# Function to fetch wallet data
def fetch_wallet_data(wallet_address):
    response = requests.get(f"{TAPTOOLS_POSITIONS_URL}?address={wallet_address}", headers=TAPTOOLS_HEADERS)
    if response.status_code == 200:
        data = response.json()
        ada_usd_price = get_ada_usd_price()
        total_ada_value = 0
        total_usd_value = 0

        tokens = []
        for token in data.get("positionsFt", []):
            usd_value = token.get("usdValue")
            ada_value = float(token.get("adaValue", 0))
            balance = float(token.get("balance", 0))
            change_7d = token.get("7d", 0)
            change_30d = token.get("30d", 0)

            usd_value = float(usd_value) if usd_value else ada_value * ada_usd_price
            total_ada_value += ada_value
            total_usd_value += usd_value

            tokens.append({
                "Ticker": token.get("ticker", "Unknown"),
                "Balance": f"{balance:,.0f}",
                "ADA Value": f"{ada_value:,.8f}",
                "USD Value": f"${usd_value:,.6f}",
                "7-Day Change": f"{change_7d:.2f}%",
                "30-Day Change": f"{change_30d:.2f}%"
            })

        df = pd.DataFrame(tokens)
        return df, total_ada_value, total_usd_value
    else:
        st.error(f"❌ Error {response.status_code}: {response.text}")
        return pd.DataFrame(), 0, 0

# Streamlit UI Setup
st.title("💼 DreamyBags")
st.caption("Cardano Wallet Quick Profiler")

# Access Code Input
access_code = st.text_input("🔐 Enter Access Code:", type="password")

if access_code in ACCESS_CODES:
    # Input field for wallet address
    wallet_address = st.text_input("🔑 Enter Wallet Address:", key="wallet_input", placeholder="Paste your wallet address here...")

    # Refresh button to reload data
    refresh_button = st.button("🔄 Refresh Portfolio")

    # Fetch data if address is entered or refresh button is clicked
    if wallet_address and (refresh_button or wallet_address):
        df, total_ada_value, total_usd_value = fetch_wallet_data(wallet_address)
        if not df.empty:
            st.success("✅ Portfolio Data Retrieved Successfully!")
            st.metric(label="💎 Total Portfolio Value (ADA)", value=f"{total_ada_value:,.8f} ADA")
            st.metric(label="💵 Total Portfolio Value (USD)", value=f"${total_usd_value:,.6f}")

            tab1, tab2 = st.tabs(["📈 7-Day Winners & Losers", "📉 30-Day Winners & Losers"])

            with tab1:
                winners_7d = df.sort_values(by="7-Day Change", ascending=False).head(3)
                losers_7d = df.sort_values(by="7-Day Change").head(3)
                st.subheader("🏆 Top 3 Winners (7-Day)")
                st.table(winners_7d)
                st.subheader("💔 Top 3 Losers (7-Day)")
                st.table(losers_7d)

            with tab2:
                winners_30d = df.sort_values(by="30-Day Change", ascending=False).head(3)
                losers_30d = df.sort_values(by="30-Day Change").head(3)
                st.subheader("🏆 Top 3 Winners (30-Day)")
                st.table(winners_30d)
                st.subheader("💔 Top 3 Losers (30-Day)")
                st.table(losers_30d)

            st.subheader("📊 Full Portfolio Breakdown")
            st.dataframe(df)
        else:
            st.warning("⚠️ No data found for the entered address.")
else:
    st.warning("🔒 Please enter a valid access code to proceed.")

# Add Disclaimer
st.caption("⚠️ Disclaimer: This app is for informational purposes only and does not constitute financial advice. Data accuracy is not guaranteed. The creator is not liable for any decisions made based on the app's data.")
