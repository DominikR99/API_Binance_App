# api/views/account_views.py
import time
import hmac
import hashlib
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['POST'])
def binance_account_info(request):
    try:
        data = request.data
        api_key = data.get("api_key")
        secret_key = data.get("secret_key")
    except:
        return Response({"error": "Invalid JSON format"}, status=400)

    if not api_key or not secret_key:
        return Response({"error": "API key and secret key are required"}, status=400)

    base_url = "https://api.binance.com"
    endpoint = "/api/v3/account"
    timestamp = int(time.time() * 1000)
    query_string = f"timestamp={timestamp}"
    signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    headers = {"X-MBX-APIKEY": api_key}

    try:
        response = requests.get(f"{base_url}{endpoint}?{query_string}&signature={signature}", headers=headers)
        response.raise_for_status()
        account_data = response.json()
        return Response(account_data)
    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=500)
