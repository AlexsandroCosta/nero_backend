from rest_framework import permissions, viewsets, authentication
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    Usuario
)
#from .serializers import ()
from django.contrib.auth.validators import UnicodeUsernameValidator

class CadastroViewSet(viewsets.ViewSet):

    @swagger_auto_schema(
        tags=['Usuarios'],
        operation_description='',
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
            'nome': openapi.Schema(type=openapi.TYPE_STRING),
            'sexo': openapi.Schema(type=openapi.TYPE_STRING, enum=['m', 'f'])
        })
    )
    @action(detail=False, methods=['post'], url_path='cadastrar')
    def cadastar(self, request):
        pass