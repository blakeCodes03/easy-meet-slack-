from rest_framework import serializers
from api.models import Api_response

class ApiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Api_response
        fields = '__all__'