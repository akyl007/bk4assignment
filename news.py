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
        self.max_retries = 3
        self.retry_delay = 2  # увеличиваем задержку между попытками
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.last_request_time = 0
        self.min_request_interval = 1.2  # увеличиваем интервал между запросами до 1.2 секунд
        
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
        for attempt in range(self.max_retries):
            try:
                self._handle_rate_limit()
                response = requests.get(url, params=params, timeout=5)  # увеличиваем таймаут
                
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
            'market_data': 'true',
            'community_data': 'true',
            'developer_data': 'false',
            'sparkline': 'false'
        }

        response = self._make_request(url, params)
        if not response:
            return []

        news_items = []
        
        # Get description
        if 'description' in response and 'en' in response['description']:
            description = response['description']['en']
            if description:
                # Split description into paragraphs and take first two
                paragraphs = description.split('\r\n\r\n')
                summary = ' '.join(paragraphs[:2])
                news_items.append({
                    'title': f"About {response.get('name', crypto_name)}",
                    'url': f"https://www.coingecko.com/en/coins/{coin_id}",
                    'source': 'CoinGecko',
                    'published_at': datetime.now().isoformat(),
                    'description': summary[:500] + '...' if len(summary) > 500 else summary
                })

        # Get categories as news
        if 'categories' in response:
            categories = response.get('categories', [])
            if categories:
                news_items.append({
                    'title': f"Categories: {', '.join(categories)}",
                    'url': f"https://www.coingecko.com/en/coins/{coin_id}",
                    'source': 'CoinGecko',
                    'published_at': datetime.now().isoformat()
                })

        # Get public notice
        if 'public_notice' in response and response['public_notice']:
            news_items.append({
                'title': f"Public Notice: {response['public_notice']}",
                'url': f"https://www.coingecko.com/en/coins/{coin_id}",
                'source': 'CoinGecko',
                'published_at': datetime.now().isoformat()
            })

        # Get additional notices
        if 'additional_notices' in response:
            for notice in response['additional_notices']:
                if notice:
                    news_items.append({
                        'title': f"Notice: {notice}",
                        'url': f"https://www.coingecko.com/en/coins/{coin_id}",
                        'source': 'CoinGecko',
                        'published_at': datetime.now().isoformat()
                    })

        # Get market data updates
        if 'market_data' in response:
            market_data = response['market_data']
            if 'price_change_percentage_24h' in market_data:
                change = market_data['price_change_percentage_24h']
                if change is not None:
                    news_items.append({
                        'title': f"24h Price Change: {change:+.2f}%",
                        'url': f"https://www.coingecko.com/en/coins/{coin_id}",
                        'source': 'Market Data',
                        'published_at': datetime.now().isoformat()
                    })

        return news_items 