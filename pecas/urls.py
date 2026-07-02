from django.urls import path
from . import views  # Isso diz ao Django para buscar o arquivo views.py da mesma pasta

urlpatterns = [
    path('', views.home, name='home'),
    path('peca/<int:id>/', views.detalhe_peca, name='detalhe_peca'),
    path('cadastrar/', views.cadastrar_peca, name='cadastrar_peca'),
]
