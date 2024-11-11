from django.apps import AppConfig
from django.db.models.signals import post_migrate

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        post_migrate.connect(povoar_db, sender=self)

def povoar_db(sender, **kwargs):
    from .models import Usuario

    if not Usuario.objects.filter(username='admin').exists():
        admin = Usuario.objects.create_superuser(username='admin')
        admin.set_password('admin')
        admin.save()