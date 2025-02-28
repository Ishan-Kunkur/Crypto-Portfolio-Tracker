# DreamyBags : Cardano Wallet Quick Profiler

## Overview

**DreamyBags** is a **Cardano wallet portfolio tracker** that allows users to quickly view their portfolio value in **ADA** and **USD**. This simple app helps Cardano users track the performance of their wallet by showing the **total balance** of assets, including **native tokens** in their wallet. It provides the **top-performing tokens** based on the **7-day** and **30-day** price changes, helping users stay informed about their portfolio’s performance in real-time.

### Features:
- **Real-time Portfolio Value**: View your Cardano wallet's total value in **ADA** and **USD**.
- **Token Tracking**: View the value of each **native token** in your wallet, including ADA.
- **Winners & Losers**: Track the **top-performing tokens** based on **7-day** and **30-day** price changes.
- **Easy Refresh**: One-click refresh to keep the data up-to-date.
- **Access Control**: Use an **access code** to unlock the app.

### How It Works:
DreamyBags fetches data from the **TapTools API** to get wallet details such as balances and performance data. The app converts ADA values into USD based on the **current ADA/USD price**, which is updated in real-time.

---

## Installation

### Prerequisites:
To run the app locally, you’ll need:
- **Python 3.x** or higher
- **Streamlit** for app deployment
- **Requests** and **Pandas** for API calls and data manipulation
- A **TapTools API Key** (free account for basic access)

### Setup Instructions:

#### 1. Clone the Repository:
```bash
git clone https://github.com/your-username/dreamybags.git
cd dreamybags

#### 2. Install Dependencies:
Create a virtual environment and install the required packages:

bash
Copy
Edit
pip install -r requirements.txt
#### 3. Configure API Key:
Create a .env file in the project’s root directory to store your TapTools API Key.

plaintext
Copy
Edit
TAPTOOLS_API_KEY=your-api-key-here
#### 4. Run the App Locally:
Launch the app using Streamlit:

bash
Copy
Edit
streamlit run wallet_tracker_usd.py
Features Breakdown
Real-Time Portfolio Value:
DreamyBags shows your total portfolio value in both ADA and USD. The ADA value is updated with each API request, while the USD value is fetched using the current ADA/USD price.

Top Tokens (Winners & Losers):
View your wallet’s top-performing tokens based on their 7-day and 30-day price changes. This gives you a quick way to track your portfolio’s trends and see which tokens are gaining or losing the most value.

Manual Refresh:
Easily refresh your wallet data with the refresh button to get the most up-to-date information.

Usage Instructions
Enter Wallet Address:
Paste your Cardano wallet address into the input box.

View Portfolio Info:
The app will display your total ADA balance, total USD value, and the list of top-performing tokens in your wallet.

Use Access Code:
To access the app, enter a valid access code like ABCXYZ to unlock the features.

Contributing
We welcome contributions! If you would like to contribute to DreamyBags, you can:

Fork this repository.
Create a feature branch (git checkout -b feature-name).
Commit your changes (git commit -am 'Add feature').
Push to your fork (git push origin feature-name).
Open a Pull Request to the main repository.
License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgements
TapTools for providing the API to fetch wallet and token data.
Streamlit for an easy and efficient way to deploy interactive web apps.
Pandas and Requests for data handling and API communication.
