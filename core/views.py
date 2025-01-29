from rest_framework import permissions, viewsets, authentication
from rest_framework.response import Response
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import (
    Usuario,
    Postagem,
    Comentario,
    Avaliacao,
    Cidade,
    Bairro
)
from .serializers import (
    UsuarioSerializer,
    PerfilSerializer,
    PostagemSerializer,
    ComentarioSerializer,
    AvaliacaoSerializer,
    CidadeSerializer,
    BairroSerializer
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.db.models import Avg

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
        user_data = request.data
        user_data['username'] = user_data['username'].lower()
              
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
        user_data = request.data
        user_data['username'] = user_data['username'].lower()

        if len(user_data['password']) < 8:
            return Response({'detail': 'A senha deve ter no mínimo 8 caracteres'}, status=400)

        serializer = UsuarioSerializer(data=user_data)

        if serializer.is_valid():
            serializer.save()

            serializer.instance.set_password(request.data['password'])
            serializer.instance.tipo = 'cidadão'
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

            serializer = UsuarioSerializer(user)

            return Response(serializer.data, status=200)
            
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
            openapi.Parameter(name='first_name', in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter(name='email', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, format='email'),
            openapi.Parameter(name='cpf', in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter(name='data_nascimento', in_=openapi.IN_FORM, type=openapi.TYPE_STRING, format='date'),
            openapi.Parameter(name='sexo', in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
            openapi.Parameter(name='grau_ensino', in_=openapi.IN_FORM, type=openapi.TYPE_STRING),
        ],
        responses={
            200: 'Usário atualizado com sucesso!'
        }
    )
    def partial_update(self, request, pk=None):
        try:
            usuario = Usuario.objects.get(id=pk)

            if usuario != request.user:
                return Response({'detail': 'Você não tem permissão para executar esta ação.'}, status=403)
        
            serializer = UsuarioSerializer(usuario, request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                return Response('Usário atualizado com sucesso!', status=200)

            return Response({'detail': request.data})

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

    @swagger_auto_schema(
        tags=['Informações'],
        operation_description='',
        responses={
            200: openapi.Schema(type=openapi.TYPE_ARRAY, items=
                                openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'nome': openapi.Schema(type=openapi.TYPE_STRING),
                                    'pontos': openapi.Schema(type=openapi.TYPE_ARRAY, items=
                                                             openapi.Schema(type=openapi.TYPE_NUMBER)),
                                    'bairros': openapi.Schema(type=openapi.TYPE_ARRAY, items=
                                                             openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                                                                 'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                                                 'nome': openapi.Schema(type=openapi.TYPE_STRING),
                                                                 'pontos': openapi.Schema(type=openapi.TYPE_ARRAY, items=
                                                                                          openapi.Schema(type=openapi.TYPE_NUMBER)),
                                                             }))
                                }))
        }
    )
    @action(detail=False, url_path='cidades')
    def cidades(self, request):
        cidades = Cidade.objects.all()

        cidades_serializer = CidadeSerializer(cidades, many=True)

        for cidade_serializer in cidades_serializer.data:
            bairros = Bairro.objects.filter(cidade__id=cidade_serializer['id'])

            bairros_serializer = BairroSerializer(bairros, many=True)

            cidade_serializer['bairros'] = bairros_serializer.data

        return Response(cidades_serializer.data, status=200)


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
            200: 'Postagem deletada com sucesso!',
            404: 'Postagem não encontrada.'
        }
    )
    def destroy(self, request, pk=None):
        try:
            postagem = Postagem.objects.get(id=pk, usuario=request.user)

            postagem.delete()

            return Response({'detail': 'Postagem deletada com sucesso!'}, status=200)

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
        request_body=ComentarioSerializer,
        responses={
            201: 'Comentário feito.'
        }
    )
    @action(detail=False, methods=['post'], url_path='comentario')
    def fazer_comentario(self, request):
        for campo in ['texto', 'postagem']:
            if not campo in request.data:
                return Response({'detail': f'O campo "{campo}" é obrigatório.'}, status=400)
        
        try:
            postagem = Postagem.objects.get(id=request.data['postagem'])

            Comentario.objects.create(
                usuario = request.user,
                postagem = postagem,
                texto = request.data['texto']
            )

            return Response({'detail': 'Comentário feito.'}, status=201)

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
            200: 'Comentário deletado.'
        }
    )
    @action(detail=False, methods=['delete'], url_path='comentario/(?P<id_comentario>[^/.]+)?')
    def deletar_comentario(self, request, id_comentario=None):
        try:
            comentario = Comentario.objects.get(id=id_comentario)

            comentario.delete()

            return Response({'detail': 'Comentário deletado.'}, status=200)

        except Comentario.DoesNotExist:
            return Response({'detail': 'Comentário não encontrado.'}, status=404)
        
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
            200: ComentarioSerializer(many=True)
        }
    )
    @action(detail=False, url_path='(?P<id_postagem>[^/.]+)?/comentarios')
    def listar_comentarios(self, request, id_postagem=None):
        try:
            postagem = Postagem.objects.get(id=id_postagem)

            comentarios = Comentario.objects.filter(postagem=postagem)

            serializer = ComentarioSerializer(comentarios, many=True)

            return Response(serializer.data, status=200)

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
        request_body=AvaliacaoSerializer,
        responses={
            201: 'Avaliação realizada com sucesso!'
        }
    )
    @action(detail=False, methods=['post'], url_path='(?P<id_postagem>[^/.]+)?/avaliar')
    def avaliar_postagem(self, request, id_postagem=None):
        try:
            postagem = Postagem.objects.get(id=id_postagem)

            if postagem.usuario == request.user:
                return Response({'detail': 'Não é possível executar esta ação.'}, status=402)

            avaliacao = request.data.get('avaliacao')

            if int(avaliacao) < 0:
                avaliacao = 0
            elif int(avaliacao) > 5:
                avaliacao = 5

            obj = Avaliacao.objects.filter(usuario=request.user, postagem=postagem)

            if obj.exists():
                obj.first().avaliacao = avaliacao
                obj.first().save()
            else:
                Avaliacao.objects.create(
                    usuario = request.user,
                    postagem = postagem,
                    avaliacao = avaliacao
                )

            media = Avaliacao.objects.filter(postagem=postagem).aggregate(media=Avg('avaliacao'))
            
            postagem.votos = media['media']
            postagem.save()

            return Response({'detail': 'Avaliação realizada com sucesso!'}, status=201)
        
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
            openapi.Parameter(
                name='novo_status',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: 'Status da postagem atualizado com sucesso!',
            403: 'Você não tem permissão para executar esta ação',
            404: 'Postagem não encontrada'
        }
    )
    @action(detail=False, methods=['patch'], url_path='(?P<id_postagem>[^/.]+)?/atualizar-status')
    def atualizar_status_postagem(self, request, id_postagem=None):
        try:
            if request.user.tipo == 'cidadão':
                return Response({'detail': 'Você não tem permissão para executar esta ação'}, status=403)
            
            postagem = Postagem.objects.get(id=id_postagem)

            if postagem.status != "1":
                return Response({'detail': 'Não é possível atualizar o status dessa postagem'}, status=400)
            
            status = request.data['novo_status'][0]

            if status not in ['1', '2', '3']:
                return Response({'detail': '"novo_status" inválido'}, status=400)

            postagem.status = status
            postagem.save()

            return Response({'detail': 'Status de postagem atualizado com sucesso!'}, status=200)

        except Postagem.DoesNotExist:
            return Response({'detail': 'Postagem não encontrada'}, status=404)

    # @action(detail=False, methods=['post'], url_path='(?P<id_postagem>[^/.]+)?/enviar-formulario')
    # def enviar_formulario(self, request, id_postagem)
    
class FeedViewSet(viewsets.ViewSet):


    @swagger_auto_schema(
        tags=['Feed'],
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
        postagens = Postagem.objects.filter(status='1')

        serializer = PostagemSerializer(postagens, many=True)

        return Response(serializer.data, status=200)
