# 🤖 AI Crypto Assistant

AI-ассистент для анализа криптовалютного рынка, использующий live-данные с различных API и GPT для генерации ответов.

## 📌 Возможности

- Получение актуальных новостей о криптовалютах
- Мониторинг цен в реальном времени
- Анализ рыночных данных
- Генерация информативных ответов с помощью GPT

## 🚀 Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/ai-crypto-assistant.git
cd ai-crypto-assistant
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и добавьте необходимые API ключи:
```env
OPENAI_API_KEY=your_openai_api_key
CRYPTOPANIC_API_KEY=your_cryptopanic_api_key
COINGECKO_API_URL=https://api.coingecko.com/api/v3
```

## ▶️ Использование

Запустите приложение:
```bash
streamlit run main.py
```

## 📝 Примеры запросов

- "Расскажи новости про Ethereum"
- "Как дела у Bitcoin?"
- "Что происходит с Solana?"

## 🛠 Технологии

- Python 3.10+
- Streamlit
- OpenAI GPT-4
- CryptoPanic API
- Binance API
- CoinGecko API

## 📄 Лицензия

MIT 