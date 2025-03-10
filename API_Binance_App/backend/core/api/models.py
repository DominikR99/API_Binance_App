from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from cryptography.fernet import Fernet
from django.conf import settings

class User(AbstractUser):
    api_key = models.CharField(max_length=255, unique=True)
    secret_key = models.TextField()  # Zaszyfrowany klucz
    testnet = models.BooleanField(default=False)

    def encrypt_secret_key(self, raw_secret_key):
        """
        Szyfruje secret_key za pomocą klucza zdefiniowanego w ustawieniach.
        """
        fernet = Fernet(settings.SECRET_ENCRYPTION_KEY)
        self.secret_key = fernet.encrypt(raw_secret_key.encode()).decode()

    def decrypt_secret_key(self):
        """
        Deszyfruje secret_key.
        """
        fernet = Fernet(settings.SECRET_ENCRYPTION_KEY)
        return fernet.decrypt(self.secret_key.encode()).decode()
    
class Strategy(models.Model):
    # Powiązanie strategii z użytkownikiem
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='strategies')

    # Podstawowe informacje o strategii
    name = models.CharField(max_length=255)  # Nazwa strategii
    pair = models.CharField(max_length=20)  # Para handlowa, np. BTC/USDT
    status = models.CharField(
        max_length=50,
        choices=[('active', 'Active'), ('stopped', 'Stopped'), ('completed', 'Completed')],
        default='active'
    )

    # Parametry strategii
    time_frame = models.CharField(max_length=20)
    short_window = models.PositiveIntegerField()  # Okno krótkoterminowej średniej kroczącej
    long_window = models.PositiveIntegerField()  # Okno długoterminowej średniej kroczącej
    stop_loss_percentage = models.FloatField()  # Stop-loss w procentach
    rsi_period = models.FloatField()  # Próg RSI
    trade_amount = models.FloatField()  # Wartość handlowa

    # Czas uruchomienia i zakończenia strategii
    start_time = models.DateTimeField(auto_now_add=True)  # Czas rozpoczęcia
    end_time = models.DateTimeField(null=True, blank=True)  # Czas zakończenia (dla zakończonych strategii)

    # Wyniki strategii
    results = models.JSONField(null=True, blank=True)  # JSON przechowujący wyniki strategii

    def __str__(self):
        return f"{self.name} ({self.pair})"
    
class Transaction(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE, related_name='transactions')
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=10, choices=[('buy', 'Buy'), ('sell', 'Sell')])
    amount = models.FloatField()
    price = models.FloatField()

    def __str__(self):
        return f"{self.action} {self.amount} at {self.price}"

