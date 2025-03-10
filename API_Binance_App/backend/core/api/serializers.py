from rest_framework import serializers
from .models import Strategy

class StrategySerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    class Meta:
        model = Strategy
        fields = '__all__'  