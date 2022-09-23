from rest_framework import serializers
from .models import Log, Patient

class LogSerializer(serializers.ModelSerializer):
    #date = serializers.DateField(format=None, input_formats=None)
    #date=serializers.DateField(format="%Y-%m-%dT%h:%m:%s",input_formats=['%Y-%m-%d',"%Y-%m-%dT%H:%M:%S"])
    #insulin = serializers.IntegerField(allow_null=True) 
    # def to_internal_value(self, data):
        # if data.get('insulin') == 'null':
            # data['insulin'] = None
            # return super(LogSerializer, self).to_internal_value(data)
            
    class Meta:
        model = Log
        fields = '__all__'
        #extra_kwargs = {'insulin': {'allow_blank': True}}

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
