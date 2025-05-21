import os
import requests
from typing import Dict
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

class CryptoPrice:
    def __init__(self):
        self.binance_url = "https://api.binance.com/api/v3"
        self.max_retries = 3
        self.retry_delay = 1
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 200ms between requests
        
        # Symbol mapping for different cryptocurrency names
        self.symbol_mapping = {
            'bitcoin': 'BTCUSDT',
            'btc': 'BTCUSDT',
            'ethereum': 'ETHUSDT',
            'eth': 'ETHUSDT',
            'solana': 'SOLUSDT',
            'sol': 'SOLUSDT',
            'cardano': 'ADAUSDT',
            'ada': 'ADAUSDT',
            'ripple': 'XRPUSDT',
            'xrp': 'XRPUSDT',
            'polkadot': 'DOTUSDT',
            'dot': 'DOTUSDT',
            'dogecoin': 'DOGEUSDT',
            'doge': 'DOGEUSDT'
        }

    def _get_symbol(self, name: str) -> str:
        """
        Converts cryptocurrency name to Binance symbol
        """
        name = name.lower().strip()
        # Remove any non-alphanumeric characters
        name = ''.join(c for c in name if c.isalnum())
        return self.symbol_mapping.get(name, f"{name.upper()}USDT")

    def _handle_rate_limit(self):
        """
        Handles rate limiting
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def _make_request(self, url: str, params: Dict = None) -> Dict:
        """
        Makes HTTP request with error handling and retries
        """
        for attempt in range(self.max_retries):
            try:
                self._handle_rate_limit()
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    print(f"Request error after {self.max_retries} attempts: {str(e)}")
                    return {"price": "0"}
                time.sleep(self.retry_delay)

    def get_price(self, token: str) -> Dict:
        """
        Gets current cryptocurrency price
        """
        try:
            # Check cache
            cache_key = f"price_{token}"
            if cache_key in self.cache:
                cache_time, cache_data = self.cache[cache_key]
                if time.time() - cache_time < self.cache_timeout:
                    return cache_data

            symbol = self._get_symbol(token)
            url = f"{self.binance_url}/ticker/price"
            params = {"symbol": symbol}
            
            result = self._make_request(url, params)
            
            # Update cache
            self.cache[cache_key] = (time.time(), result)
            
            return result
        except Exception as e:
            print(f"Error getting price: {str(e)}")
            # Return cached data if available
            cache_key = f"price_{token}"
            if cache_key in self.cache:
                return self.cache[cache_key][1]
            return {"price": "0"}

    def get_24h_stats(self, token: str) -> Dict:
        """
        Gets 24-hour cryptocurrency statistics
        """
        try:
            symbol = self._get_symbol(token)
            url = f"{self.binance_url}/ticker/24hr"
            params = {"symbol": symbol}
            
            return self._make_request(url, params)
        except Exception as e:
            print(f"Error getting 24h stats: {str(e)}")
            return {
                "priceChange": "0",
                "priceChangePercent": "0",
                "volume": "0",
                "quoteVolume": "0"
            } 