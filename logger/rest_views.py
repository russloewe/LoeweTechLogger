#Rest Framework
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .models import Patient, Log
from .serializers import PatientSerializer,  LogSerializer
from django.contrib.auth.models import User
from rest_framework import mixins
from rest_framework import generics


class PatientPermission(permissions.BasePermission):
    edit_methods = ('PUT')
    
    def has_permission(self, request, view):
        pk = self.request.query_params['patient']
        patient = Patient.objects.filter(pk =  patient_id)[0]
        owner_patients = Patient.objects.filter(user_id = request.user.id)
        connected_patients = Patient.objects.filter(connected = request.user.id)
        patients = owner_patients | connected_patients
        if patient in patients:
            return(True)
        else:
            return(False)

class LogUpdateView(mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class FitbitRedirectEndpoint(APIView):
    
    def get(self, pk):
        data = ''
        for key in self.request.query_params:
            data += '({}, {})'.format(key, self.request.query_params[key])
        raise Exception(data)
        return Response({'status':1})

class ServerStatus(APIView):
    
    def get(self, pk):
        return(Response({'status': 1}))



class LogList(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LogSerializer
    
    def get_queryset(self):
        #patient = self.kwargs['patient']
        pk = self.request.query_params['patient']
        queryset = Log.objects.filter(patient=pk).order_by('-date')[0:100]
        return(queryset)

    def perform_create(self, serializer):
        # user = User.objects.get(pk=)
        patient_id = int(self.request.query_params['patient'])
        patient = Patient.objects.filter(pk =  patient_id)[0]
        serializer.save(user=self.request.user, patient= patient, date=timezone.now() )
        return Response({ 'status': 1})

class LogListNoSteps(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LogSerializer
    
    def get_queryset(self):
        #patient = self.kwargs['patient']
        pk = self.request.query_params['patient']
        queryset = Log.objects.filter(patient=pk, steps=None).order_by('-date')[0:30]
        return(queryset)
        
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        #Retreive and format data for patiens this user has access to
        patients = Patient.objects.filter(user_id = user.id)
        connected_patients = Patient.objects.filter(connected = user.id)
        all_patients = [p for p in patients] + [p for p in connected_patients]
        all_patients = map(lambda x:  PatientSerializer(x).data, all_patients)
        
        
        #Retrieve user token from db
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'user_id': user.pk,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                },
            'status': 1,
            'patients': all_patients
        })                                                                                                                                                                                                                                                                                                                                          
