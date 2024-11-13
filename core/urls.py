from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.DefaultRouter()

router.register(r'usuario', views.CadastroViewSet, basename='cadastro')
router.register(r'usuario', views.UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', views.ModAuthToken.as_view(), name='api-token-auth'),
]