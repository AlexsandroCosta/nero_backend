from rest_framework import permissions, viewsets, authentication
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    Usuario
)
from .serializers import (
    UsuarioSerializer
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

class ModAuthToken(ObtainAuthToken):

    @swagger_auto_schema(
        tags=['auth'],
        operation_description='',
        responses={
            201: openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'sexo': openapi.Schema(type=openapi.TYPE_STRING, enum=['Masculino', 'Feminino']),
                'cpf': openapi.Schema(type=openapi.TYPE_STRING),
                'grau_ensino': openapi.Schema(type=openapi.TYPE_STRING),
                'data_nascimento': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'token': openapi.Schema(type=openapi.TYPE_STRING),
            })
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        userSerializer = UsuarioSerializer(user)

        user_data = userSerializer.data
        user_data['token'] = token.key
 
        return Response(user_data)

class CadastroViewSet(viewsets.ViewSet):

    @swagger_auto_schema(
        tags=['Usuários'],
        operation_description='',
        request_body=UsuarioSerializer,
        responses={
            201: 'Usuário cadastrado com sucesso!'
        }
    )
    def create(self, request):
        serializer = UsuarioSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            serializer.instance.set_password(request.data['password'])
            serializer.instance.save()

            return Response({'detail': 'Usuário cadastrado com sucesso!'}, status=201) 

        return Response(serializer.errors, status=400)

class UsuarioViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]

    @swagger_auto_schema(
        tags=['Usuários'],
        operation_description='',
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token de autenticação no formato `Token <token>`',
            )
        ],
    )
    def retrieve(self, request, pk=None):
        try:
            user = Usuario.objects.get(id=pk)

            serializer = UsuarioSerializer(user)

            return Response(serializer.data, status=200)

        except Usuario.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado!'}, status=404)
        
    