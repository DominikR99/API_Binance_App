from binance.client import Client
import time
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Transaction
from .models import Strategy
from threading import Thread
from django.utils.timezone import now
from .models import User
from datetime import datetime

def convert_to_seconds(time_str):
    """
    Konwertuje ciąg czasu (np. "1m", "1h") na liczbę sekund.
    
    Args:
        time_str (str): Czas w formacie, np. "1m", "2h", "1d".
        
    Returns:
        int: Liczba sekund.
    """
    # Mapowanie jednostek czasu na sekundy
    time_multipliers = {
        'm': 60,        # Minuta na sekundy
        'h': 3600,      # Godzina na sekundy
        'd': 86400,     # Dzień na sekundy
        'w': 604800     # Tydzień na sekundy
    }

    # Pobieramy ostatni znak jako jednostkę czasu (np. 'm', 'h', 'd', 'w')
    unit = time_str[-1]
    # Pobieramy liczbę (np. '1', '2') jako mnożnik
    value = int(time_str[:-1])

    # Przeliczamy na sekundy
    return value * time_multipliers.get(unit, 0)

def initialize_client(api_key, secret_key, testnet):
    """
    Inicjalizuje klienta Binance z uwzględnieniem trybu testnet.
    """
    client = Client(api_key, secret_key, testnet=testnet)
    return client

def fetch_candles(client, symbol, timeframe):
    """
    Pobiera dane OHLCV dla podanego symbolu i interwału czasowego.
    """
    try:
        # Pobranie danych świec
        klines = client.get_klines(symbol=symbol, interval=timeframe)
        candles = [
            [int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])]
            for k in klines
        ]
        return candles
    except Exception as e:
        print(f"Błąd podczas pobierania świec: {e}")
        return None
    
def fetch_historical_candles(client, symbol, interval, start_time, end_time=None):
    """
    Pobiera historyczne świece OHLCV dla danego symbolu i interwału.
    """
    try:
        klines = client.get_historical_klines(symbol, interval, start_time, end_time)
        candles = [
            [int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])]
            for k in klines
        ]
        return candles
    except Exception as e:
        print(f"Błąd podczas pobierania danych historycznych: {e}")
        return None
    
import requests

from datetime import datetime
import requests

def fetch_historical_candles_official_paginated1(symbol, interval, start_time, end_time=None):
    """
    Pobiera dane historyczne z Binance w sposób stronicowany.
    """
    base_url = "https://api.binance.com/api/v3/klines"
    all_candles = []
    current_start_time = int(datetime.strptime(start_time, "%Y-%m-%d").timestamp() * 1000)

    while current_start_time < int(datetime.strptime(end_time, "%Y-%m-%d").timestamp() * 1000):
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_start_time,
            "limit": 1000  # Maksymalna liczba świec
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            break

        all_candles.extend(data)
        current_start_time = data[-1][0] + 1  # Ustaw start na koniec ostatniej świecy

    return [
        [int(c[0]), float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])]
        for c in all_candles
    ]

def fetch_historical_candles_official_paginated(symbol, interval, start_time, end_time=None):
    """
    Pobiera dane historyczne z Binance w sposób stronicowany z poprawnym ograniczeniem do end_time.
    
    :param symbol: Symbol pary (np. "BTCUSDT").
    :param interval: Interwał świec (np. "4h", "1d").
    :param start_time: Początek okresu (format "YYYY-MM-DD").
    :param end_time: Koniec okresu (format "YYYY-MM-DD").
    :return: Lista świec w formacie [timestamp, open, high, low, close, volume].
    """
    base_url = "https://api.binance.com/api/v3/klines"
    all_candles = []
    current_start_time = int(datetime.strptime(start_time, "%Y-%m-%d").timestamp() * 1000)
    end_time_ms = int(datetime.strptime(end_time, "%Y-%m-%d").timestamp() * 1000) if end_time else None

    while current_start_time < (end_time_ms if end_time_ms else float('inf')):
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": current_start_time,
            "limit": 1000  # Maksymalna liczba świec
        }
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        # Przetwarzanie danych świec
        for candle in data:
            candle_time = candle[0]
            if end_time_ms and candle_time >= end_time_ms:
                # Jeśli świeca przekracza end_time, przerwij dodawanie danych
                return [
                    [int(c[0]), float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])]
                    for c in all_candles
                ]
            all_candles.append(candle)

        # Aktualizacja current_start_time
        current_start_time = data[-1][0] + 1  # Ustaw start na koniec ostatniej świecy

    return [
        [int(c[0]), float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])]
        for c in all_candles
    ]


def fetch_historical_candles_official(symbol, interval, start_time, end_time=None):
    """
    Pobiera historyczne świece OHLCV dla danego symbolu i interwału z oficjalnego rynku Binance.
    """
    base_url = "https://api.binance.com/api/v3/klines"
    
    # Konwersja start_time i end_time na obiekty datetime
    try:
        start_time = datetime.strptime(start_time, "%Y-%m-%d")
        start_timestamp = int(start_time.timestamp() * 1000)  # Konwersja na milisekundy
    except ValueError:
        raise ValueError("start_time must be in the format 'YYYY-MM-DD'")

    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_timestamp,
    }
    
    if end_time:
        try:
            end_time = datetime.strptime(end_time, "%Y-%m-%d")
            params["endTime"] = int(end_time.timestamp() * 1000)  # Konwersja na milisekundy
        except ValueError:
            raise ValueError("end_time must be in the format 'YYYY-MM-DD'")

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Rzuć wyjątek, jeśli status != 200
        data = response.json()

        candles = [
            [int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])]
            for k in data
        ]
        return candles
    except Exception as e:
        print(f"Błąd podczas pobierania danych historycznych: {e}")
        return None


    
# Obliczanie średnich kroczących
def calculate_moving_averages(candles, short_window, long_window):
    closes = [candle[4] for candle in candles]  # Zamknięcia świec
    short_ma = sum(closes[-short_window:]) / short_window
    long_ma = sum(closes[-long_window:]) / long_window
    return short_ma, long_ma

# Obliczanie RSI
def calculate_rsi(candles, period):
    closes = [candle[4] for candle in candles]
    gains = []
    losses = []
    for i in range(1, len(closes)):
        change = closes[i] - closes[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:  # Zapobiega dzieleniu przez zero
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Funkcja do sprawdzania warunku stop-loss
def check_stop_loss(entry_price, current_price, side, stop_loss_percentage):
    if side == 'long':
        return current_price <= entry_price * (1 - stop_loss_percentage)
    elif side == 'short':
        return current_price >= entry_price * (1 + stop_loss_percentage)
    return False

def place_order(client, symbol, side, quantity, strategy_id):
    """
    Składa zlecenie rynkowe na Binance i zapisuje transakcję w bazie danych.
    """
    try:
        order = client.create_order(
            symbol=symbol,
            side=side.upper(),
            type='MARKET',
            quantity=quantity
        )
        # Pobranie ceny z transakcji
        fills = order.get('fills', [])
        price = float(fills[0]['price']) if fills else None

        # Zapis transakcji do bazy danych
        Transaction.objects.create(
            strategy_id=strategy_id,
            action=side,
            price=price,
            amount=quantity
        )

        print(f"Zlecenie {side} złożone: {order}")
        return order
    except Exception as e:
        print(f"Błąd przy składaniu zlecenia: {e}")
        return None

def run_strategy(client, symbol, timeframe, short_window, long_window, stop_loss_percentage, rsi_period, 
                strategy_duration, strategy_id, trade_amount):
    position = None
    entry_price = None
    start_time = time.time()
    timeframe_in_seconds = convert_to_seconds(timeframe)

    while True:
        try:
            elapsed_time = time.time() - start_time

            # Jeśli czas upłynął i brak otwartej pozycji, zakończ strategię
            if elapsed_time >= float(strategy_duration) and position is None:
                print("Czas strategii upłynął i brak otwartej pozycji. Kończę działanie strategii...")
                Strategy.objects.filter(id=strategy_id).update(
                    end_time=now(),
                    status='completed'
                )
                break

            candles = fetch_candles(client, symbol, timeframe)
            if not candles:
                time.sleep(60)
                continue

            short_ma, long_ma = calculate_moving_averages(candles, short_window, long_window)
            rsi = calculate_rsi(candles, period=rsi_period)
            current_price = candles[-1][4]

            if position:
                # Sprawdzenie stop-loss dla otwartej pozycji
                if check_stop_loss(entry_price, current_price, position, stop_loss_percentage):
                    print("Stop-loss aktywowany. Zamykam pozycję...")
                    side = 'SELL' if position == 'long' else 'BUY'
                    place_order(client, symbol, side, trade_amount, strategy_id)
                    position = None
                    entry_price = None

            # Sygnał kupna
            if short_ma > long_ma and rsi < 30 and position != 'long':
                print("Sygnał kupna. Składanie zlecenia kupna...")
                order = place_order(client, symbol, 'BUY', trade_amount, strategy_id)
                if order:
                    position = 'long'
                    entry_price = current_price

            # Sygnał sprzedaży
            elif short_ma < long_ma and rsi > 70 and position == 'long':
                print("Sygnał sprzedaży. Składanie zlecenia sprzedaży...")
                order = place_order(client, symbol, 'SELL', trade_amount, strategy_id)
                if order:
                    position = None  # Pozycja zamknięta
                    entry_price = None

                    # Jeśli czas strategii upłynął i pozycja została zamknięta, kończymy
                    if elapsed_time >= float(strategy_duration):
                        print("Czas strategii upłynął i pozycja zamknięta. Kończę strategię...")
                        Strategy.objects.filter(id=strategy_id).update(
                            end_time=now(),
                            status='completed'
                        )
                        break

            time.sleep(timeframe_in_seconds)

        except Exception as e:
            print(f"Błąd w pętli strategii: {e}")
            Strategy.objects.filter(id=strategy_id).update(
                    end_time=now(),
                    status='canceled'
                )
            break

            
def create_transaction(strategy_id, action, current_price, trade_amount, current_candles_time):
    Transaction.objects.create(
        strategy_id=strategy_id,
        action=action,
        price=current_price,
        amount=trade_amount,
        timestamp=current_candles_time
    )
        
def run_strategy_backtest(client, symbol, timeframe, short_window, long_window, stop_loss_percentage, rsi_period, trade_amount, start_time, end_time):
    # Pobieranie danych historycznych
    candles = fetch_historical_candles_official_paginated(symbol, timeframe, start_time, end_time)
    if not candles:
        print("Brak danych historycznych.")
        return []

    transactions = []  # Lista do przechowywania transakcji
    position = None
    entry_price = None

    for i in range(max(short_window, long_window), len(candles)):
        try:
            # Wyciąg aktualnych świec
            current_candles = candles[:i+1]
            short_ma, long_ma = calculate_moving_averages(current_candles, short_window, long_window)
            rsi = calculate_rsi(current_candles, period=rsi_period)
            current_price = current_candles[-1][4]  # Zamknięcie ostatniej świecy
            current_time = datetime.fromtimestamp(current_candles[-1][0] / 1000).strftime("%Y-%m-%d %H:%M:%S")  # Format czasu

            # Obsługa otwartej pozycji i sprawdzanie warunku stop-loss
            if position:
                if check_stop_loss(entry_price, current_price, position, stop_loss_percentage):
                    print(f"Stop-loss aktywowany przy cenie {current_price}. Zamykam pozycję...")
                    side = 'SELL' if position == 'long' else 'BUY'

                    # Dodanie transakcji do listy
                    transactions.append({
                        "action": side,
                        "price": current_price,
                        "amount": trade_amount,
                        "time": current_time
                    })

                    position = None
                    entry_price = None

            # Rozpocznij od sygnału kupna, jeśli brak pozycji
            if position != 'long' and short_ma > long_ma and rsi < 30:
                print(f"Sygnał kupna (MA + RSI) przy cenie {current_price}.")
                action = 'BUY'
                position = 'long'
                entry_price = current_price

                # Dodanie transakcji do listy
                transactions.append({
                    "action": action,
                    "price": current_price,
                    "amount": trade_amount,
                    "time": current_time
                })
                
            # Obsługa sygnału sprzedaży
            if position == 'long' and short_ma < long_ma and rsi > 70:
                print(f"Sygnał sprzedaży (MA + RSI) przy cenie {current_price}.")
                action = 'SELL'
                position = None  # Pozycja zamknięta
                entry_price = None

                # Dodanie transakcji do listy
                transactions.append({
                    "action": action,
                    "price": current_price,
                    "amount": trade_amount,
                    "time": current_time
                })
            print(current_time)

        except Exception as e:
            print(f"Błąd w symulacji strategii: {e}")

    # # Zakończenie strategii sygnałem sprzedaży
    # if position == 'long':
    #     print(f"Końcowy sygnał sprzedaży przy cenie {current_price}.")
    #     current_time = datetime.fromtimestamp(candles[-1][0] / 1000).strftime("%Y-%m-%d %H:%M:%S")
    #     transactions.append({
    #         "action": 'SELL',
    #         "price": current_price,
    #         "amount": trade_amount,
    #         "time": current_time
    #     })
    #     position = None
    # Sprawdzenie i usunięcie ostatniej transakcji, jeśli to 'BUY'
    if transactions and transactions[-1]["action"] == 'BUY':
        print("Ostatnia transakcja to 'BUY'. Usuwam z listy.")
        transactions.pop()

    print("Symulacja strategii zakończona.")
    return transactions


@api_view(['POST'])
def start_strategy(request):
    try:
        data = request.data
        api_key = data.get("username")
    except:
        return Response({"error": "Invalid JSON format"}, status=400)

    user = User.objects.filter(api_key=api_key).first()
    
     # Weryfikacja kluczy Binance
    try:
        client = Client(user.api_key, user.decrypt_secret_key(), testnet=user.testnet)
        client.get_account()  # Próba pobrania danych konta
    except Exception as e:
        return Response({"error": f"Invalid API key or Secret Key: {str(e)}"}, status=401)

    # Tworzenie strategii w bazie danych
    strategy = Strategy.objects.create(
        user=user,
        name=data['name'],
        pair=data['symbol'],
        short_window=data['short_window'],
        long_window=data['long_window'],
        stop_loss_percentage=data['stop_loss_percentage'],
        rsi_period=data['rsi_period'],
        trade_amount=data['trade_amount'],
        time_frame = data['timeframe']
    )

    # Uruchamianie strategii w tle
    def run():
        run_strategy(
            client,
            symbol=data['symbol'],
            timeframe=data['timeframe'],
            short_window=int(data['short_window']),
            long_window=int(data['long_window']),
            stop_loss_percentage=float(data['stop_loss_percentage']),
            rsi_period=int(data['rsi_period']),
            strategy_duration=float(data['strategy_duration']),
            strategy_id=strategy.id,
            trade_amount=float(data['trade_amount'])
        )

    strategy_thread = Thread(target=run)
    strategy_thread.start()

    return Response({"message": "Strategy started", "strategy_id": strategy.id})


@api_view(['POST'])
def backtest_strategy(request):
    try:
        data = request.data
        user = User.objects.get(api_key=data.get("username"))

        client = initialize_client(user.api_key, user.decrypt_secret_key(), testnet=user.testnet)
        
        if "strategy_id" in data and data["strategy_id"]:
            strategy = Strategy.objects.get(id=data["strategy_id"])
            data["symbol"] = strategy.pair
            data["timeframe"] = strategy.time_frame
            data["short_window"] = strategy.short_window
            data["long_window"] = strategy.long_window
            data["stop_loss_percentage"] = strategy.stop_loss_percentage
            data["rsi_period"] = strategy.rsi_period
            data["trade_amount"] = strategy.trade_amount

        if "formData" in data and data["formData"]:
            data = data["formData"]
            
            
        transactions = run_strategy_backtest(
            client,
            symbol=data['symbol'],
            timeframe=data['timeframe'],
            short_window=int(data['short_window']),
            long_window=int(data['long_window']),
            stop_loss_percentage=float(data['stop_loss_percentage']),
            rsi_period=int(data['rsi_period']),
            trade_amount=float(data['trade_amount']),
            start_time=request.data["startDate"],
            end_time=request.data["endDate"]
        )

        return Response({"message": "Backtest completed", "transactions": transactions})
    except Exception as e:
        return Response({"error": f"Błąd: {str(e)}"}, status=500)
