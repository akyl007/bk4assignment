import os
import json
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv
import time
from datetime import datetime

load_dotenv()

class AIResponse:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3.2"
        self.max_retries = 3
        self.retry_delay = 1
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes

    def _format_date(self, date_str: str) -> str:
        try:
            if not date_str:
                return "unknown"
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date.strftime("%d.%m.%Y %H:%M")
        except Exception:
            return "unknown"

    def _format_news(self, news: List[Dict]) -> str:
        if not news:
            return "No news found"
        
        formatted_news = []
        for item in news[:5]:  # Limit to 5 news items
            title = item.get('title', 'No title')
            url = item.get('url', '#')
            source = item.get('source', 'Unknown source')
            date = self._format_date(item.get('published_at', ''))
            
            formatted_news.append(f"- [{title}]({url}) ({source}, {date})")
        
        return "\n".join(formatted_news)

    def _format_price(self, price: str) -> str:
        try:
            return f"${float(price):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    def _format_market_cap(self, market_cap: float) -> str:
        try:
            return f"${float(market_cap):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    def _format_change_24h(self, change: float) -> str:
        try:
            return f"{float(change):+.2f}%"
        except (ValueError, TypeError):
            return "0.00%"

    def generate_response(self, 
                         user_input: str, 
                         price_data: Dict, 
                         market_data: Dict,
                         news: List[Dict]) -> Optional[str]:
        try:
            # Format data
            price = self._format_price(price_data.get('price', '0'))
            market_cap = self._format_market_cap(market_data.get('market_cap', 0))
            change_24h = self._format_change_24h(market_data.get('change_24h', 0))
            rank = f"#{int(market_data.get('rank', 0))}"
            last_updated = self._format_date(market_data.get('last_updated', ''))
            formatted_news = self._format_news(news)

            # Create prompt
            prompt = f"""User asks: {user_input}

Current cryptocurrency information:
- Price: {price}
- Market Cap: {market_cap}
- 24h Change: {change_24h}
- Rank: {rank}
- Last Updated: {last_updated}

Latest News:
{formatted_news}

Please provide an informative response to the user's question using the provided data.
The response should be structured and include current price and news information.
Use markdown for formatting.

Response format:
1. Brief overview of the cryptocurrency
2. Current market status (price, market cap, 24h change)
3. Market position (rank)
4. Latest news summary
5. Conclusion or outlook

Keep the response concise and focused on the most important information."""

            # Try to get response from Ollama
            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        self.ollama_url,
                        json={
                            "model": self.model,
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=30
                    )
                    response.raise_for_status()
                    result = response.json()
                    return result.get('response', 'Sorry, could not generate response')
                except requests.exceptions.RequestException as e:
                    if attempt == self.max_retries - 1:
                        raise
                    time.sleep(self.retry_delay)

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "Sorry, an error occurred while generating the response. Please try again later." 