from binance.client import Client
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import User, Transaction, Strategy
from datetime import datetime

def fetch_all_transactions(client, start_time=None, end_time=None):
    """
    Pobiera wszystkie transakcje użytkownika dla wszystkich symboli.
    """
    try:
        # Pobierz wszystkie dostępne symbole handlowe
        exchange_info = client.get_exchange_info()
        valid_symbols = [s['symbol'] for s in exchange_info['symbols']]

        all_trades = []

        for symbol in valid_symbols:
            try:
                # Pobierz transakcje dla konkretnego symbolu
                trades = client.get_my_trades(
                    symbol=symbol,
                    startTime=start_time,
                    endTime=end_time
                )
                all_trades.extend(trades)  # Dodaj do listy wszystkich transakcji
            except Exception as e:
                # Pomiń błędy dla symboli bez transakcji
                print(f"No trades for symbol {symbol}: {e}")

        return all_trades
    except Exception as e:
        print(f"Błąd podczas pobierania transakcji: {e}")
        return []


@api_view(['GET'])
def transactions_history(request):
    """
    Endpoint do pobierania historii transakcji.
    - Jeśli podano `strategy_id`, pobiera transakcje z tabeli `Transaction`.
    - Jeśli nie, pobiera transakcje z Binance API na podstawie konta użytkownika.
    """
    username = request.query_params.get('username', None)
    symbol = request.query_params.get('symbol', None)  # Opcjonalny symbol
    strategy_id = request.query_params.get('strategy', None)  # Opcjonalny ID strategii
    start_time = request.query_params.get('startTime', None)  # Opcjonalny początek przedziału
    end_time = request.query_params.get('endTime', None)  # Opcjonalny koniec przedziału

    if not username:
        return Response({"error": "Username is required to fetch transactions"}, status=400)

    try:
        # Znajdź użytkownika na podstawie `username`
        user = User.objects.get(username=username)
        api_key = user.api_key
        secret_key = user.decrypt_secret_key()
        testnet = user.testnet
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    # Jeśli podano `strategy_id`, pobierz transakcje z lokalnej bazy danych
    if strategy_id:
        try:
            # strategy = Strategy.objects.filter(id=strategy_id, user=user)
            transactions = Transaction.objects.filter(strategy_id=strategy_id, strategy__user=user)
            processed_transactions = [
                {
                    "symbol": txn.strategy.pair,
                    "price": float(txn.price),
                    "qty": float(txn.amount),
                    "time": txn.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "isBuyer": txn.action.lower() == "buy",  # Oparte na akcji transakcji
                }
                for txn in transactions
            ]
            return Response(processed_transactions, status=200)
        except Exception as e:
            return Response({"error": f"Failed to fetch transactions from database: {str(e)}"}, status=500)

    # Jeśli nie podano `strategy_id`, pobierz dane z Binance API
    try:
        client = Client(api_key, secret_key, testnet=testnet)

        # Zamiana dat na timestampy (jeśli podano)
        if start_time:
            start_time = int(datetime.strptime(start_time, "%Y-%m-%d").timestamp() * 1000)
        if end_time:
            end_time = int(datetime.strptime(end_time, "%Y-%m-%d").timestamp() * 1000)

        # Pobranie transakcji z Binance
        trades = []
        if symbol:
            trades = client.get_my_trades(symbol=symbol, startTime=start_time, endTime=end_time)

        # Przetwarzanie danych transakcji
        processed_trades = [
            {
                "symbol": trade["symbol"],
                "price": float(trade["price"]),
                "qty": float(trade["qty"]),
                "time": datetime.fromtimestamp(trade["time"] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
                "isBuyer": trade["isBuyer"],
            }
            for trade in trades
        ]

        return Response(processed_trades, status=200)
    except Exception as e:
        return Response({"error": f"Failed to fetch transactions: {str(e)}"}, status=500)
