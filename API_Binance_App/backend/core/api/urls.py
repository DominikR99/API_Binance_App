# api/urls.py
from django.urls import path
from .views.account_views import binance_account_info
from .views.portfolio_views import binance_portfolio_balance, get_user_portfolio
from .views.auth_user import authenticate_user, logout, csrf_token_view
from .sma_rsi_strategy import start_strategy, backtest_strategy
from .views.strategy_views import get_strategies
from .views.transaction_history import transactions_history

urlpatterns = [
    path('binance-account/', binance_account_info, name='binance_account_info'),
    path('binance/portfolio/balance/', binance_portfolio_balance, name='binance_portfolio_balance'),
    path('login/', authenticate_user, name='authenticate_user'),
    path('logout/', logout, name='logout'),
    path('csrf-token/', csrf_token_view, name='csrf_token'),
    path('binance/portfolio/', get_user_portfolio, name='get_user_portfolio'),
    path('start-strategy/', start_strategy, name='start_strategy'),
    path('test-strategy/', backtest_strategy, name='backtest_strategy'),
    path('strategies/', get_strategies, name='get_strategies'),
    path('transactions-history/', transactions_history, name='transactions_history'),
]
