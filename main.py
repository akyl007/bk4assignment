import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(page_title="Crypto Assistant", page_icon="💰")

import os
from dotenv import load_dotenv
from news import CryptoNews
from price import CryptoPrice
from market_data import MarketData
from ai_response import AIResponse

# Load environment variables
load_dotenv()

# Initialize components
news = CryptoNews()
price = CryptoPrice()
market_data = MarketData()
ai = AIResponse()

st.title("Crypto Assistant")

# Input field
user_input = st.text_input("Enter your question about cryptocurrency:", 
                          placeholder="Example: Tell me news about bitcoin")

if user_input:
    try:
        # Extract cryptocurrency name from the query
        words = user_input.lower().split()
        crypto_name = None
        for word in words:
            if word in ['bitcoin', 'ethereum', 'solana', 'cardano', 'ripple', 'polkadot', 'dogecoin',
                       'btc', 'eth', 'sol', 'ada', 'xrp', 'dot', 'doge']:
                crypto_name = word
                break

        if not crypto_name:
            st.error("Please specify a cryptocurrency name in your query")
            st.stop()

        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Get data
        try:
            # Get news (25%)
            status_text.text("Getting news...")
            news_data = news.get_news(crypto_name)
            progress_bar.progress(25)

            # Get price (50%)
            status_text.text("Getting current price...")
            price_data = price.get_price(crypto_name)
            if not price_data or price_data.get("price") == "0":
                st.warning("Failed to get price")
                price_data = {"price": "0"}
            progress_bar.progress(50)

            # Get market data (75%)
            status_text.text("Getting market data...")
            market_data_result = market_data.get_market_data(crypto_name)
            if not market_data_result:
                st.warning("Failed to get market data")
                market_data_result = {
                    "price": 0,
                    "market_cap": 0,
                    "volume_24h": 0,
                    "change_24h": 0,
                    "rank": 0,
                    "last_updated": "unknown"
                }
            progress_bar.progress(75)

            # Generate response (100%)
            status_text.text("Generating response...")
            response = ai.generate_response(
                user_input,
                price_data,
                market_data_result,
                news_data
            )

            if response:
                progress_bar.progress(100)
                status_text.text("Done!")
                st.write(response)
            else:
                st.error("Failed to generate response")

        except Exception as e:
            st.error(f"An error occurred while getting data: {str(e)}")
            st.info("Please check your internet connection and API availability")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please check the cryptocurrency name and ensure all required API keys are in the .env file") 