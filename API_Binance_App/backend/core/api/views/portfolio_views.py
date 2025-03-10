import time
import hmac
import hashlib
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from binance.client import Client
from ..models import User

# Funkcja do pobrania cen wszystkich aktywów w USDT
def get_all_symbol_prices(client):
    """
    Pobiera ceny wszystkich aktywów i przelicza je na USDT dla testnetu Binance.
    """
    try:
        # Pobranie cen wszystkich par handlowych
        prices = client.get_all_tickers()
        
        # Filtrowanie i przeliczanie na USDT
        usdt_prices = {
            item['symbol']: float(item['price'])
            for item in prices
            if item['symbol'].endswith("USDT")
        }
        return usdt_prices
    except Exception as e:
        print(f"Error fetching symbol prices: {str(e)}")
        return None

# Funkcja do pobrania ceny aktywa w USDT
def get_symbol_price(symbol, client):
    all_prices = get_all_symbol_prices(client)
    if all_prices and f"{symbol}USDT" in all_prices:
        return all_prices[f"{symbol}USDT"]
    return None

# Funkcja do pobierania informacji o koncie
def get_binance_account_info(api_key, secret_key, testnet):
    client = Client(api_key, secret_key, testnet=testnet)
    try:
        account_data = client.get_account()
        if 'balances' in account_data:
            return account_data
        else:
            return {"error": "Invalid API or Secret Key"}
    except Exception as e:
        print(f"Error fetching account info: {str(e)}")
        return {"error": str(e)}

# Funkcja obliczająca bilans w USDT
def calculate_total_balance_in_usdt(api_key, secret_key, testnet):
    client = Client(api_key, secret_key, testnet=testnet)
    account_info = get_binance_account_info(api_key, secret_key, testnet)
    if "error" in account_info:
        return account_info

    total_value_usdt = 0.0
    usdt_prices = get_all_symbol_prices(client)

    for balance in account_info.get('balances', []):
        asset = balance['asset']
        free_balance = float(balance['free'])

        if free_balance > 0:
            price = usdt_prices.get(f"{asset}USDT")
            if price:
                total_value_usdt += free_balance * price

    return {"total_balance_in_usdt": total_value_usdt}

# Funkcja do obliczania najlepszych aktywów
def calculate_top_assets(api_key, secret_key, testnet):
    client = Client(api_key, secret_key, testnet=testnet)
    account_info = get_binance_account_info(api_key, secret_key, testnet)
    
    assets = []
    usdt_prices = get_all_symbol_prices(client)

    for balance in account_info.get('balances', []):
        asset = balance['asset']
        free_balance = float(balance['free'])

        if free_balance > 0:
            price = usdt_prices.get(f"{asset}USDT")
            if price:
                assets.append({
                    'symbol': asset,
                    'value_in_usdt': free_balance * price
                })
    
    assets = sorted(assets, key=lambda x: x['value_in_usdt'], reverse=True)
    return assets[:5]

# Endpoint REST API w Django
@api_view(['POST'])
def binance_portfolio_balance(request):
    try:
        data = request.data
        api_key = data.get("username")
    except:
        return Response({"error": "Invalid JSON format"}, status=400)

    user = User.objects.filter(api_key=api_key).first()
    
    if not user:
        return Response({"error": "API key and secret key are required"}, status=400)
    
    secret_key = user.decrypt_secret_key()
    
    if not user.api_key or not secret_key:
        return Response({"error": "API key and secret key are required"}, status=400)

    total_balance = calculate_total_balance_in_usdt(api_key, secret_key, user.testnet)

    if "error" in total_balance:
        return Response(total_balance, status=500)

    top_assets = calculate_top_assets(api_key, secret_key, user.testnet)

    return Response({
        "total_balance_in_usdt": total_balance["total_balance_in_usdt"],
        "topAssets": top_assets
    })

@api_view(['GET'])
def get_user_portfolio(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=403)

    try:
        # Tworzenie obiektu Client na podstawie użytkownika
        client = Client(api_key=user.api_key, secret_key=user.decrypt_secret_key(), testnet=user.testnet)
        account_info = client.get_account()

        # Obliczanie bilansu w USDT
        total_balance = calculate_total_balance_in_usdt(user.api_key, user.decrypt_secret_key(), user.testnet)

        return Response({"account_info": account_info, "total_balance": total_balance})
    except Exception as e:
        return Response({"error": f"Failed to fetch portfolio: {str(e)}"}, status=500)

