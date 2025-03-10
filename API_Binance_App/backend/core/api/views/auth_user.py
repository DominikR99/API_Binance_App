from django.contrib.auth import login
from rest_framework.decorators import api_view
from django.contrib.auth import logout
from rest_framework.response import Response
from binance.client import Client
from ..models import User
from django.middleware.csrf import get_token
from django.http import JsonResponse

@api_view(['POST'])
def authenticate_user(request):
    try:
        data = request.data
        api_key = data.get("api_key")
        secret_key = data.get("secret_key")
        testnet = data.get("testnet")
    except:
        return Response({"error": "Invalid JSON format"}, status=400)

    # Weryfikacja kluczy Binance
    try:
        client = Client(api_key, secret_key, testnet=testnet)
        client.get_account()  # Próba pobrania danych konta
    except Exception as e:
        return Response({"error": f"Invalid API key or Secret Key: {str(e)}"}, status=401)

    # Sprawdzanie, czy użytkownik istnieje
    user = User.objects.filter(api_key=api_key).first()
    if not user:
        # Tworzenie nowego użytkownika
        user = User.objects.create_user(
            username=api_key,
            api_key=api_key,
            testnet=testnet,
        )
        user.encrypt_secret_key(secret_key)
        user.save()

    # Logowanie użytkownika
    login(request, user)
    return Response({"message": "Logged in successfully", "username": user.api_key,})

@api_view(['POST'])
def logout_user(request):
    logout(request)
    return Response({"message": "Logged out successfully"})


def csrf_token_view(request):
    response = JsonResponse({"message": "CSRF token set"})
    response.set_cookie('csrftoken', get_token(request))
    return response
