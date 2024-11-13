from rest_framework import serializers
from .models import (
    Usuario
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
            'data_nascimento'
        ]

        extra_kwargs = {
            'password': {'write_only': True}
        }