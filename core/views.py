from rest_framework import permissions, viewsets, authentication
from rest_framework.response import Response
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    Usuario,
    Postagem
)
from .serializers import (
    UsuarioSerializer,
    PerfilSerializer,
    PostagemSerializer
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
                'foto_perfil': openapi.Schema(type=openapi.TYPE_STRING, format='uri'), 
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
    parser_classes = (MultiPartParser, FormParser)

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

            if request.user.is_superuser or request.user.id == int(pk):

                serializer = UsuarioSerializer(user)

                return Response(serializer.data, status=200)
            
            return Response({'detail': 'Você não tem permissão para executar esta ação.'}, status=400)

        except Usuario.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=404)
    
    @swagger_auto_schema(
        tags=['Usuários'],
        operation_description='',
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token de autenticação no formato `Token <token>`',
            ),
            openapi.Parameter(name='foto_perfil', in_=openapi.IN_FORM, type=openapi.TYPE_FILE)
        ],
        request_body=PerfilSerializer,
        responses={
            200: 'Foto de perfil atualizada com sucesso!'
        }
    )
    @action(detail=False, methods=['put'], url_path='foto-perfil')
    def atualizar_foto_perfil(self, request):
        
        foto_perfil = request.FILES.get('foto_perfil')
        
        if not foto_perfil:
            return Response({'detail': 'Imagem não enviada'}, status=400)
        
        user = request.user

        user.foto_perfil = foto_perfil
        user.save()

        return Response('Foto de perfil atualizada com sucesso!', status=200)
    
class InfosViewSet(viewsets.ViewSet):

    @swagger_auto_schema(
        tags=['Informações'],
        operation_description='',
        responses={
            200: openapi.Schema(type=openapi.TYPE_ARRAY, items=
                                openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                    '<id>': openapi.Schema(type=openapi.TYPE_STRING)
                                    }
                                ))
        }
    )
    @action(detail=False, url_path='grau-ensino')
    def grau_ensino(self, request):
        data = {}

        for grau in Usuario.GRAU_CHOICES:
            data[grau[0]] = grau[1]

        return Response(data, status=200)
    
    @swagger_auto_schema(
        tags=['Informações'],
        operation_description='',
        responses={
            200: openapi.Schema(type=openapi.TYPE_ARRAY, items=
                                openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                    '<id>': openapi.Schema(type=openapi.TYPE_STRING)
                                    }
                                ))
        }
    )
    @action(detail=False, url_path='natureza-postagem')
    def natureza_postagem(self, request):
        data = {}

        for natureza in Postagem.NATUREZA_CHOICES:
            data[natureza[0]] = natureza[1]

        return Response(data, status=200)
    
    @swagger_auto_schema(
        tags=['Informações'],
        operation_description='',
        responses={
            200: openapi.Schema(type=openapi.TYPE_ARRAY, items=
                                openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                    '<id>': openapi.Schema(type=openapi.TYPE_STRING)
                                    }
                                ))
        }
    )
    @action(detail=False, url_path='status-postagem')
    def status_postagem(self, request):
        data = {}

        for status in Postagem.STATUS_CHOICES:
            data[status[0]] = status[1]

        return Response(data, status=200) 

class PostagemViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        tags=['Postagem'],
        operation_description='',
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token de autenticação no formato `Token <token>`',
            ),
        ],
        request_body=PostagemSerializer,
        responses={
            201: 'Postagem criada com sucesso!'
        }
    )
    def create(self, request):
        postagem_data = request.data

        serializer = PostagemSerializer(data=postagem_data)

        if serializer.is_valid():
            serializer.save()
            serializer.instance.usuario = request.user
            serializer.instance.save()

            return Response({'detail': 'Postagem criada com sucesso!'}, status=201)
        
        return Response(serializer.errors, status=400)
    
    @swagger_auto_schema(
        tags=['Postagem'],
        operation_description='',
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token de autenticação no formato `Token <token>`',
            ),
        ],
        request_body=PostagemSerializer,
        responses={
            200: 'Postagem atualizada com sucesso!',
            404: 'Postagem não encontrada.'
        }
    )
    def partial_update(self, request, pk=None):
        try:
            postagem = Postagem.objects.get(id=pk)
            
            serializer = PostagemSerializer(postagem, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()

                return Response({'detail': 'Postagem atualizada com sucesso!'}, status=200)

        except Postagem.DoesNotExist:
            return Response({'detail': 'Postagem não encontrada.'}, status=404)
        
    @swagger_auto_schema(
        tags=['Postagem'],
        operation_description='',
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token de autenticação no formato `Token <token>`',
            ),
        ],
        responses={
            204: 'Postagem deletada com sucesso!',
            404: 'Postagem não encontrada.'
        }
    )
    def destroy(self, request, pk=None):
        try:
            postagem = Postagem.objects.get(id=pk, usuario=request.user)

            postagem.delete()

            return Response({'detail': 'Postagem deletada com sucesso!'}, status=204)

        except Postagem.DoesNotExist:
            return Response({'detail': 'Postagem não encontrada.'}, status=404)

    @swagger_auto_schema(
        tags=['Postagem'],
        operation_description='',
        manual_parameters=[
            openapi.Parameter(
                name='Authorization',
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                description='Token de autenticação no formato `Token <token>`',
            ),
        ],
        responses={
            200: PostagemSerializer(many=True)
        }
    )
    def list(self, request):
        postagens = Postagem.objects.filter(usuario=request.user)

        serializer = PostagemSerializer(postagens, many=True)

        return Response(serializer.data, status=200)