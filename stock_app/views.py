from django.shortcuts import render
from django.http import JsonResponse
import yfinance as yf
import pandas as pd
from rest_framework.decorators import api_view

# Function to render home page
def home(request):
    return render(request, 'index.html')

# Function to calculate EMA
def calculate_ema(data, period=100):
    return data['Close'].ewm(span=period, adjust=False).mean()

# Function to calculate RSI
def calculate_rsi(data, period=14):
    delta = data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

@api_view(['GET'])
def stock_analysis(request, ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")

        if df.empty:
            return JsonResponse({'error': 'No data found for the given ticker'}, status=404)

        df['ema_100'] = calculate_ema(df, 100)
        df['ema_200'] = calculate_ema(df, 200)
        df['rsi'] = calculate_rsi(df)

        # Get the latest 30 days of data
        df_recent = df.tail(30)
        dates = df_recent.index.strftime('%Y-%m-%d').tolist()
        closing_prices = df_recent['Close'].tolist()

        latest_data = df.iloc[-1]
        latest_close = round(latest_data['Close'], 2)
        ema_100 = round(latest_data['ema_100'], 2)
        ema_200 = round(latest_data['ema_200'], 2)
        rsi = round(latest_data['rsi'], 2)
        trend = "Bullish" if ema_100 > ema_200 else "Bearish"

        return JsonResponse({
            'ticker': ticker,
            'latest_close': latest_close,
            'ema_100': ema_100,
            'ema_200': ema_200,
            'rsi': rsi,
            'trend': trend,
            'dates': dates,
            'closing_prices': closing_prices
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)