from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Strategy
from ..serializers import StrategySerializer

from ..models import User
from rest_framework.exceptions import NotFound, PermissionDenied

@api_view(['GET'])
def get_strategies(request):
    """
    Endpoint do pobierania strategii dla konkretnego użytkownika.
    Wymaga podania `username` w parametrach zapytania.
    Jeśli podano `id`, zwraca szczegóły konkretnej strategii tego użytkownika.
    """
    username = request.query_params.get('username', None)
    strategy_id = request.query_params.get('id', None)

    if not username:
        return Response({"error": "Username is required to fetch strategies"}, status=400)

    try:
        # Pobieranie użytkownika na podstawie `username`
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise NotFound("User not found")

    if strategy_id:
        # Pobieranie szczegółów konkretnej strategii dla użytkownika
        try:
            strategy = Strategy.objects.get(id=strategy_id, user=user)
            serializer = StrategySerializer(strategy)
            return Response(serializer.data, status=200)
        except Strategy.DoesNotExist:
            raise NotFound("Strategy not found")
    else:
        # Pobieranie wszystkich strategii dla użytkownika
        strategies = Strategy.objects.filter(user=user)
        serializer = StrategySerializer(strategies, many=True)
        return Response(serializer.data, status=200)

