from django.apps import AppConfig
from django.db.models.signals import post_migrate

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        post_migrate.connect(povoar_db, sender=self)

def povoar_db(sender, **kwargs):
    from .models import Usuario, Postagem, Bairro
    from shapely.geometry import Point, Polygon

    if not Usuario.objects.filter(username='admin').exists():
        admin = Usuario.objects.create_superuser(username='admin')
        admin.set_password('admin')
        admin.save()

        for postagem in Postagem.objects,filter(status='1'):
            for bairro in Bairro.objects.all():
                poligono = Polygon(bairro.pontos)
    
                latitude, longitude = postagem.geolocalizacao.split(',')
    
                ponto = Point(float(latitude), float(longitude))
    
                if poligono.contains(ponto):
                    bairro.quantidade_reclamacoes+=1
                    bairro.save()
                    break
