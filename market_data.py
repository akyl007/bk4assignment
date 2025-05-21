import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

class MarketData:
    def __init__(self):
        self.coingecko_url = os.getenv("COINGECKO_API_URL", "https://api.coingecko.com/api/v3")
        self.coingecko_api_key = os.getenv("COINGECKO_API_KEY")
        self.max_retries = 3
        self.retry_delay = 2
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.last_request_time = 0
        self.min_request_interval = 1.2  # увеличиваем интервал между запросами
        
        # Name to ID mapping for CoinGecko
        self.coin_mapping = {
            'bitcoin': 'bitcoin',
            'btc': 'bitcoin',
            'ethereum': 'ethereum',
            'eth': 'ethereum',
            'solana': 'solana',
            'sol': 'solana',
            'cardano': 'cardano',
            'ada': 'cardano',
            'ripple': 'ripple',
            'xrp': 'ripple',
            'polkadot': 'polkadot',
            'dot': 'polkadot',
            'dogecoin': 'dogecoin',
            'doge': 'dogecoin'
        }

    def _get_coin_id(self, name: str) -> str:
        """
        Converts cryptocurrency name to CoinGecko API ID
        """
        name = name.lower().strip()
        return self.coin_mapping.get(name, name)

    def _handle_rate_limit(self):
        """
        Handles rate limiting
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """
        Makes HTTP request with error handling and retries
        """
        headers = {}
        if self.coingecko_api_key:
            headers['X-CG-API-KEY'] = self.coingecko_api_key

        for attempt in range(self.max_retries):
            try:
                self._handle_rate_limit()
                response = requests.get(
                    url, 
                    params=params, 
                    headers=headers,
                    timeout=5
                )
                
                # Проверяем заголовки лимитов
                if 'X-RateLimit-Remaining' in response.headers:
                    remaining = int(response.headers['X-RateLimit-Remaining'])
                    if remaining <= 1:
                        # Если остался 1 запрос или меньше, ждем дольше
                        time.sleep(self.min_request_interval * 2)
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Too Many Requests
                    if attempt < self.max_retries - 1:
                        # Увеличиваем задержку при ошибке 429
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                print(f"HTTP error: {str(e)}")
                return None
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                print(f"Request error: {str(e)}")
                return None
                
        return None

    def get_market_data(self, crypto_name: str) -> Optional[Dict]:
        """
        Gets cryptocurrency market data
        """
        try:
            # Check cache
            cache_key = f"market_{crypto_name}"
            if cache_key in self.cache:
                cache_time, cache_data = self.cache[cache_key]
                if time.time() - cache_time < self.cache_timeout:
                    return cache_data

            coin_id = self._get_coin_id(crypto_name)
            url = f"{self.coingecko_url}/coins/{coin_id}"

            params = {
                'localization': 'false',
                'tickers': 'false',
                'market_data': 'true',
                'community_data': 'false',
                'developer_data': 'false',
                'sparkline': 'false'
            }

            response = self._make_request(url, params)
            if not response:
                return self._get_default_market_data()

            market_data = {
                'price': response.get('market_data', {}).get('current_price', {}).get('usd', 0),
                'market_cap': response.get('market_data', {}).get('market_cap', {}).get('usd', 0),
                'volume_24h': response.get('market_data', {}).get('total_volume', {}).get('usd', 0),
                'change_24h': response.get('market_data', {}).get('price_change_percentage_24h', 0),
                'rank': response.get('market_cap_rank', 0),
                'last_updated': response.get('last_updated', '')
            }

            # Update cache
            self.cache[cache_key] = (time.time(), market_data)

            return market_data

        except Exception as e:
            print(f"Error getting market data: {str(e)}")
            return self._get_default_market_data()

    def _get_default_market_data(self) -> Dict:
        """
        Returns default market data in case of errors
        """
        return {
            'price': 0,
            'market_cap': 0,
            'volume_24h': 0,
            'change_24h': 0,
            'rank': 0,
            'last_updated': datetime.now().isoformat()
        } 