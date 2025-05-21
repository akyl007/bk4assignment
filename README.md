# 🤖 AI Crypto Assistant

AI is an assistant for analyzing the cryptocurrency market, using live data from various APIs and GPT to generate responses.

## 📌 Features

- Getting up-to-date news about cryptocurrencies
- Real-time price monitoring
- Market data analysis
- Generation of informative responses using GPT

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-crypto-assistant.git
cd ai-crypto-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create file `.env` and add API keys:
```env
OPENAI_API_KEY=your_openai_api_key
CRYPTOPANIC_API_KEY=your_cryptopanic_api_key
COINGECKO_API_URL=https://api.coingecko.com/api/v3
```

## ▶️ Using

Launch the app:
```bash
streamlit run main.py
```

## 📝 Query examples

- "Tell us the news about Ethereum"
- "How is Bitcoin doing?"
- "What's going on with Solana?"

## 🛠 Technologies:

- Python 3.10+
- Streamlit
- OpenAI GPT-4
- CryptoPanic API
- Binance API
- CoinGecko API

## 📄 Licenze

MIT 