from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.gis.db import models as gis_models

class Usuario(AbstractUser):
    GRAU_CHOICES = [
        ('1', 'ANALFABETO, INCLUSIVE O QUE, EMBORA TENHA RECEBIDO INSTRUÇÃO, NÃO SE ALFABETIZOU.'),
        ('2', 'ATÉ O 5º ANO INCOMPLETO DO ENSINO FUNDAMENTAL (ANTIGA 4ª SÉRIE) QUE SE TENHA ALFABETIZADO SEM TER FREQÜENTADO ESCOLA REGULAR.'),
        ('3', '5º ANO COMPLETO DO ENSINO FUNDAMENTAL.'),
        ('4', 'DO 6º AO 9º ANO DO ENSINO FUNDAMENTAL INCOMPLETO (ANTIGA 5ª À 8ª SÉRIE).'),
        ('5', 'ENSINO FUNDAMENTAL COMPLETO.'),
        ('6', 'ENSINO MÉDIO INCOMPLETO.'),
        ('7', 'ENSINO MÉDIO COMPLETO.'),
        ('8', 'EDUCAÇÃO SUPERIOR INCOMPLETA.'),
        ('9', 'EDUCAÇÃO SUPERIOR COMPLETA.'),
        ('10', 'PÓS GRADUAÇÃO INCOMPLETA.'),
        ('11', 'PÓS GRADUAÇÃO COMPLETA.'),
        ('12', 'MESTRADO COMPLETO.'),
        ('13', 'DOUTORADO COMPLETO.')
    ]

    SEXO_CHOICES = [
        ('m', 'Masculino'),
        ('f', 'Feminino')
    ]

    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, null=True, blank=True)
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True)
    grau_ensino = models.CharField(max_length=2, choices=GRAU_CHOICES, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    foto_perfil = models.ImageField(upload_to='perfil/', null=True, blank=True)

    class Meta:
        swappable = "AUTH_USER_MODEL"
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

class Postagem(models.Model):
    NATUREZA_CHOICES = [
        ('1', 'denúncias'),
        ('2', 'dúvidas'),
        ('3', 'elogios'),
        ('4', 'reclamações'),
        ('5', 'serviços'),
        ('6', 'sugestões'),
        ('7', 'urgências')
    ]

    STATUS_CHOICES = [
        ('1', 'pendente'),
        ('2', 'resolvido'),
        ('3', 'falso')
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    criacao = models.DateTimeField(auto_now_add=True)
    imagem = models.ImageField(upload_to='imagens/', null=True, blank=True)
    votos = models.IntegerField(default=0)
    geolocalizacao = models.CharField(max_length=150, null=True, blank=True)
    natureza = models.CharField(max_length=1, choices=NATUREZA_CHOICES)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='1')
    anonima = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
    
class Comentario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    postagem = models.ForeignKey(Postagem, on_delete=models.CASCADE)
    texto = models.CharField(max_length=300)
