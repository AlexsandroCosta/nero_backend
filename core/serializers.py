from rest_framework import serializers
from .models import (
    Usuario,
    Postagem,
    Comentario,
    Avaliacao
)

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'password',
            'first_name',
            'email',
            'sexo',
            'cpf',
            'grau_ensino',
            'data_nascimento',
            'foto_perfil',
            'tipo'
        ]

        extra_kwargs = {
            'password': {'write_only': True},
            'tipo': {'read_only': True}
        }

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['foto_perfil']

class PostagemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Postagem
        fields = [
            'id',
            'usuario',
            'titulo',
            'descricao',
            'criacao',
            'imagem',
            'votos',
            'geolocalizacao',
            'natureza',
            'status'
        ]

        extra_kwargs = {
            'usuario': {'read_only': True},
            'votos': {'read_only': True},
            'status': {'read_only': True}
        }

class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = [
            'texto',
            'usuario',
            'postagem'
        ]

        extra_kwargs = {
            'usuario': {'read_only': True}
        }

class AvaliacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaliacao
        fields = [
            'id',
            'usuario',
            'postagem',
            'avaliacao'
        ]
        extra_kwargs = {
            'usuario': {'read_only': True},
            'postagem': {'read_only': True}
        }