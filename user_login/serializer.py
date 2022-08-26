from rest_framework import serializers
from .models import Users


class LogInSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id']


class SingUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
