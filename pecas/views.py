from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Peca, HistoricoMovimentacao
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- 🚀 GATILHO MÁGICO DEFINITIVO ---
# Qualquer usuário que você criar pelo painel vira administrador AUTOMATICAMENTE na hora!
@receiver(post_save, sender=get_user_model())
def garantir_permissao_equipe(sender, instance, created, **kwargs):
    if created and instance.username != 'dalila':
        instance.is_staff = True
        instance.is_superuser = True  
        instance.save()

def home(request):
    # Apenas carrega as peças de forma super leve
    pesquisa = request.GET.get('pesquisa') or request.GET.get('q')

    if pesquisa:
        pecas = Peca.objects.filter(
            Q(codigo__icontains=pesquisa) |
            Q(descricao__icontains=pesquisa) |
            Q(categoria__icontains=pesquisa) |
            Q(locacao__icontains=pesquisa) |
            Q(finalidade__icontains=pesquisa)
        ).distinct()
    else:
        pecas = Peca.objects.all()

    return render(request, 'pecas/home.html', {
        'pecas': pecas
    })

