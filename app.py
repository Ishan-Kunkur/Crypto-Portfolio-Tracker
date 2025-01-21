import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TAPTOOLS_API_KEY = os.getenv("TAPTOOLS_API_KEY")
ACCESS_CODE = os.getenv("ACCESS_CODE", "mysecretcode")
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=cardano&vs_currencies=usd"
TAPTOOLS_POSITIONS_URL = "https://openapi.taptools.io/api/v1/wallet/portfolio/positions"

TAPTOOLS_HEADERS = {
    "x-api-key": TAPTOOLS_API_KEY
}


# ---------------------------------------------------------------------
# Backend Functions
# ---------------------------------------------------------------------

def get_cardano_price():
    """Fetch current Cardano price in USD from CoinGecko."""
    try:
        response = requests.get(COINGECKO_URL)
        data = response.json()
        return data["cardano"]["usd"]
    except Exception as e:
        print(f"Error fetching Cardano price: {e}")
        return None

def get_wallet_portfolio(wallet_address):
    """Fetch portfolio data for a single wallet from TapTools API."""
    url = f"{TAPTOOLS_POSITIONS_URL}?address={wallet_address}"
    try:
        response = requests.get(url, headers=TAPTOOLS_HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"TapTools API error {response.status_code} for {wallet_address}")
            return None
    except Exception as e:
        print(f"Error fetching portfolio data for {wallet_address}: {e}")
        return None

def aggregate_wallet_data(wallet_addresses):
    """
    Aggregate token data across multiple wallets.
    Returns a dictionary with total_ada_value, total_usd_value, etc.
    """
    total_ada_value = 0.0
    total_usd_value = 0.0
    token_data = {}
    wallet_data = {}

    # Fetch the Cardano price
    cardano_price_usd = get_cardano_price()
    if cardano_price_usd is None:
        return None

    for address in wallet_addresses:
        address = address.strip()
        if not address:
            continue
        portfolio_data = get_wallet_portfolio(address)
        if portfolio_data and "positionsFt" in portfolio_data:
            wallet_token_data = {}
            for token in portfolio_data["positionsFt"]:
                token_name = token.get("ticker", "Unknown Token")
                token_balance = token.get("balance", 0.0)
                token_ada_value = token.get("adaValue", 0.0)
                token_usd_value = token_ada_value * cardano_price_usd

                # Global aggregation
                if token_name in token_data:
                    token_data[token_name]["quantity"] += token_balance
                    token_data[token_name]["ada_value"] += token_ada_value
                    token_data[token_name]["usd_value"] += token_usd_value
                else:
                    token_data[token_name] = {
                        "quantity": token_balance,
                        "ada_value": token_ada_value,
                        "usd_value": token_usd_value
                    }

                # Wallet-level aggregation
                if token_name in wallet_token_data:
                    wallet_token_data[token_name]["quantity"] += token_balance
                    wallet_token_data[token_name]["ada_value"] += token_ada_value
                    wallet_token_data[token_name]["usd_value"] += token_usd_value
                else:
                    wallet_token_data[token_name] = {
                        "quantity": token_balance,
                        "ada_value": token_ada_value,
                        "usd_value": token_usd_value
                    }

            wallet_data[address] = wallet_token_data
            total_ada_value += sum(item["ada_value"] for item in wallet_token_data.values())
            total_usd_value += sum(item["usd_value"] for item in wallet_token_data.values())

    return {
        "total_ada_value": total_ada_value,
        "total_usd_value": total_usd_value,
        "token_data": token_data,
        "wallet_data": wallet_data,
        "cardano_price_usd": cardano_price_usd
    }


# ---------------------------------------------------------------------
# Streamlit Frontend: 3-Step Wizard (No st.experimental_rerun)
# ---------------------------------------------------------------------

def main():
    st.set_page_config(page_title="DreamyBags (Beta)", layout="wide")

    # Custom CSS
    st.markdown("""
    <style>
    .summary-card {
        background-color: #f0f0f0;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: center;
        color: #000;
    }
    .summary-card h3 {
        margin: 0;
        padding: 0;
        font-size: 1.2rem;
        color: #000;
    }
    .summary-card p {
        margin: 0;
        padding: 0;
        font-size: 1rem;
        font-weight: bold;
        color: #000;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        padding: 0.5rem;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)

    # Session states
    if "access_granted" not in st.session_state:
        st.session_state.access_granted = False
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1
    if "aggregated_result" not in st.session_state:
        st.session_state.aggregated_result = None
    if "wallet_addresses" not in st.session_state:
        st.session_state.wallet_addresses = ["", "", "", "", ""]

    def go_to_step(step_number):
        st.session_state.current_step = step_number

    st.title("DreamyBags: Cardano Wallet Profiler (Beta)")

    # -----------------------------------------------------------------
    # STEP 1: Access Code
    # -----------------------------------------------------------------
    if st.session_state.current_step == 1 and not st.session_state.access_granted:
        st.markdown("**Step 1**: Enter your Access Code to proceed.")
        
        # Use a simple text input and button (no form).
        code_input = st.text_input("Access Code", type="password")
        if st.button("Submit Access Code"):
            if code_input == ACCESS_CODE:
                # Grant access, move to Step 2
                st.session_state.access_granted = True
                go_to_step(2)
            else:
                st.warning("Incorrect access code. Please try again.")

    # -----------------------------------------------------------------
    # STEP 2: Wallet Addresses
    # -----------------------------------------------------------------
    if st.session_state.current_step == 2 and st.session_state.access_granted:
        st.markdown("**Step 2**: Enter up to 5 Cardano wallet addresses.")
        # Use a form so we get a single submission for all addresses
        with st.form("wallet_form"):
            st.session_state.wallet_addresses[0] = st.text_input("Wallet Address 1", value=st.session_state.wallet_addresses[0])
            st.session_state.wallet_addresses[1] = st.text_input("Wallet Address 2", value=st.session_state.wallet_addresses[1])
            st.session_state.wallet_addresses[2] = st.text_input("Wallet Address 3", value=st.session_state.wallet_addresses[2])
            st.session_state.wallet_addresses[3] = st.text_input("Wallet Address 4", value=st.session_state.wallet_addresses[3])
            st.session_state.wallet_addresses[4] = st.text_input("Wallet Address 5", value=st.session_state.wallet_addresses[4])

            submit_wallets = st.form_submit_button("Submit Wallet Addresses")

            if submit_wallets:
                # Aggregate the data
                valid_addresses = [addr.strip() for addr in st.session_state.wallet_addresses if addr.strip()]
                st.session_state.aggregated_result = aggregate_wallet_data(valid_addresses)

                go_to_step(3)

    # -----------------------------------------------------------------
    # STEP 3: Display Results
    # -----------------------------------------------------------------
    if st.session_state.current_step == 3 and st.session_state.access_granted:
        st.markdown("**Step 3**: Your Aggregated Portfolio Results")

        result = st.session_state.aggregated_result
        if result is None:
            st.error("Error retrieving data or no addresses provided. Please go back and try again.")
        else:
            # Display summary cards
            cardano_price_usd = result["cardano_price_usd"]
            total_ada_value = result["total_ada_value"]
            total_usd_value = result["total_usd_value"]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="summary-card">
                    <h3>ADA Price</h3>
                    <p>${cardano_price_usd:,.6f}</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="summary-card">
                    <h3>Total ADA Value</h3>
                    <p>{total_ada_value:,.2f} ADA</p>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="summary-card">
                    <h3>Total USD Value</h3>
                    <p>${total_usd_value:,.2f}</p>
                </div>
                """, unsafe_allow_html=True)

            # Aggregated Token Table
            st.subheader("Aggregated Token Data (Sorted by Highest ADA Value)")
            token_data = result["token_data"]
            if token_data:
                df_aggregated = pd.DataFrame(token_data).T
                df_aggregated.sort_values("ada_value", ascending=False, inplace=True)
                df_aggregated["Quantity"] = df_aggregated["quantity"].apply(lambda x: f"{x:,.2f}")
                df_aggregated["ADA Value"] = df_aggregated["ada_value"].apply(lambda x: f"{x:,.2f}")
                df_aggregated["USD Value"] = df_aggregated["usd_value"].apply(lambda x: f"${x:,.2f}")
                st.table(df_aggregated[["Quantity", "ADA Value", "USD Value"]])
            else:
                st.write("No tokens found across the given wallets.")

            # Wallet-Specific Data
            for address, wallet_dict in result["wallet_data"].items():
                if wallet_dict:
                    st.subheader(f"Token Data for Wallet: {address}")
                    df_wallet = pd.DataFrame(wallet_dict).T
                    df_wallet.sort_values("ada_value", ascending=False, inplace=True)
                    df_wallet["Quantity"] = df_wallet["quantity"].apply(lambda x: f"{x:,.2f}")
                    df_wallet["ADA Value"] = df_wallet["ada_value"].apply(lambda x: f"{x:,.2f}")
                    df_wallet["USD Value"] = df_wallet["usd_value"].apply(lambda x: f"${x:,.2f}")
                    st.table(df_wallet[["Quantity", "ADA Value", "USD Value"]])

        # Navigation Buttons
        if st.button("Go Back to Wallet Input"):
            go_to_step(2)

        st.markdown("""
        ---
        **Disclaimer**: Data is sourced from third-party APIs (TapTools & CoinGecko).
        Please verify accuracy before making decisions. The app developers are not
        liable for any actions taken based on this data.
        """)


if __name__ == "__main__":
    main()
