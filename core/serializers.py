from rest_framework import serializers
from .models import (
    Usuario,
    Postagem,
    Comentario,
    Avaliacao,
    Cidade,
    Bairro
)
from PIL import Image

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

    def validate_foto_perfil(self, value):
        if value:
            try:
                img = Image.open(value)
                img.verify()  # Verifica se o arquivo é uma imagem válida
                
                # Lista de formatos permitidos
                formatos_permitidos = ["JPEG", "JPG", "PNG"]
                
                if img.format.upper() not in formatos_permitidos:
                    raise serializers.ValidationError("Apenas imagens nos formatos JPEG, JPG e PNG são permitidas.")

            except (IOError, SyntaxError):
                raise serializers.ValidationError("O arquivo enviado não é uma imagem válida.")
        
        return value

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
            'status',
            'anonima'
        ]

        extra_kwargs = {
            'usuario': {'read_only': True},
            'votos': {'read_only': True},
            'status': {'read_only': True}
        }

    def validate_imagem(self, value):
        if value:
            try:
                img = Image.open(value)
                img.verify()  # Verifica se o arquivo é uma imagem válida
                
                # Lista de formatos permitidos
                formatos_permitidos = ["JPEG", "JPG", "PNG"]
                
                if img.format.upper() not in formatos_permitidos:
                    raise serializers.ValidationError("Apenas imagens nos formatos JPEG, JPG e PNG são permitidas.")

            except (IOError, SyntaxError):
                raise serializers.ValidationError("O arquivo enviado não é uma imagem válida.")
        
        return value
        
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

class CidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cidade
        fields = '__all__'

class BairroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bairro
        fields = '__all__'
 