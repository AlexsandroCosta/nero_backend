from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r'usuario', views.CadastroViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
]