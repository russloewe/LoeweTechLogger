from rest_framework import serializers
from .models import Log, Patient

class LogSerializer(serializers.ModelSerializer):
    #date = serializers.DateField(format=None, input_formats=None)
    #date=serializers.DateField(format="%Y-%m-%dT%h:%m:%s",input_formats=['%Y-%m-%d',"%Y-%m-%dT%H:%M:%S"])
    
    class Meta:
        model = Log
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
