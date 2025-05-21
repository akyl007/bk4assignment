import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta

load_dotenv()

class CryptoNews:
    def __init__(self):
        self.coingecko_url = os.getenv("COINGECKO_API_URL", "https://api.coingecko.com/api/v3")
        self.cryptopanic_url = "https://cryptopanic.com/api/v1/posts"
        self.cryptopanic_api_key = os.getenv("CRYPTOPANIC_API_KEY")
        self.max_retries = 1  # reduce to 1 attempt for speed
        self.retry_delay = 0.5  # reduce delay
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.last_request_time = 0
        self.min_request_interval = 0.2  # reduce request interval
        
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
        try:
            self._handle_rate_limit()
            response = requests.get(url, params=params, timeout=3)  # reduce timeout to 3 seconds
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return None

    def get_news(self, crypto_name: str) -> List[Dict]:
        """
        Gets cryptocurrency news from different sources
        """
        try:
            # Check cache
            cache_key = f"news_{crypto_name}"
            if cache_key in self.cache:
                cache_time, cache_data = self.cache[cache_key]
                if time.time() - cache_time < self.cache_timeout:
                    return cache_data

            # First try to get news from CoinGecko (faster)
            coingecko_news = self._get_coingecko_news(crypto_name)
            
            # If no CoinGecko news, try CryptoPanic
            cryptopanic_news = []
            if not coingecko_news and self.cryptopanic_api_key:
                cryptopanic_news = self._get_cryptopanic_news(crypto_name)

            # Combine news
            all_news = []
            if coingecko_news:
                all_news.extend(coingecko_news)
            if cryptopanic_news:
                all_news.extend(cryptopanic_news)

            # Sort by publication date
            all_news.sort(key=lambda x: x.get('published_at', ''), reverse=True)

            # Update cache
            self.cache[cache_key] = (time.time(), all_news)

            return all_news

        except Exception as e:
            print(f"Error getting news: {str(e)}")
            return []

    def _get_cryptopanic_news(self, crypto_name: str) -> List[Dict]:
        """
        Gets news from CryptoPanic API
        """
        if not self.cryptopanic_api_key:
            return []

        params = {
            'auth_token': self.cryptopanic_api_key,
            'currencies': crypto_name.upper(),
            'kind': 'news',
            'filter': 'hot',
            'limit': 5
        }

        response = self._make_request(self.cryptopanic_url, params)
        if not response or 'results' not in response:
            return []

        news_items = []
        for item in response['results']:
            news_items.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'source': item.get('source', {}).get('title', 'CryptoPanic'),
                'published_at': item.get('published_at', '')
            })

        return news_items

    def _get_coingecko_news(self, crypto_name: str) -> List[Dict]:
        """
        Gets news from CoinGecko API
        """
        coin_id = self._get_coin_id(crypto_name)
        url = f"{self.coingecko_url}/coins/{coin_id}"

        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'false',
            'community_data': 'true',
            'developer_data': 'false'
        }

        response = self._make_request(url, params)
        if not response:
            return []

        news_items = []
        if 'community_data' in response:
            for item in response['community_data'].get('reddit_posts', [])[:5]:
                news_items.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'source': 'Reddit',
                    'published_at': item.get('published_at', '')
                })

        return news_items 