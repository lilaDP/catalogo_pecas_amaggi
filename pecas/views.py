from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Peca, HistoricoMovimentacao
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- GATILHO AUTOMÁTICO: TODO MUNDO QUE VOCÊ CRIAR VIRA EQUIPE NA HORA ---
@receiver(post_save, sender=get_user_model())
def garantir_permissao_equipe(sender, instance, created, **kwargs):
    if created and instance.username != 'dalila':
        instance.is_staff = True
        instance.is_superuser = True  
        instance.save()

def home(request):
    # --- AJUSTE LEVE DE USUÁRIOS (SEM MIGRATE PESADO) ---
    try:
        User = get_user_model()
        
        # Garante seu usuário principal
        if User.objects.filter(username='dalila').exists():
            admin_user = User.objects.get(username='dalila')
            # Só atualiza se a senha não estiver batendo
            if not admin_user.check_password('Dalila2006*'):
                admin_user.set_password('Dalila2006*')
                admin_user.is_superuser = True
                admin_user.is_staff = True
                admin_user.save()
        else:
            User.objects.create_superuser(
                username='dalila', 
                email='dalila@exemplo.com', 
                password='Dalila2006*'
            )

        # Força o conserto manual do cadastro antigo da Mariana
        if User.objects.filter(username='mariana').exists():
            user_mariana = User.objects.get(username='mariana')
            if not user_mariana.is_staff or not user_mariana.check_password('Mariana2006*'):
                user_mariana.is_staff = True
                user_mariana.is_superuser = True
                user_mariana.set_password('Mariana2006*')
                user_mariana.save()

    except Exception:
        pass
    # ---------------------------------------------------

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


def detalhe_peca(request, id):
    peca = get_object_or_404(Peca, id=id)
    historico = peca.movimentacoes.all()[:10]
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Você precisa estar logado para movimentar o estoque.")
            return redirect('detalhe_peca', id=peca.id)

        operacao = request.POST.get('operacao')
        qtd_str = request.POST.get('movimentar_quantidade')
        reserva = request.POST.get('numero_reserva', '').strip()
        
        if operacao and qtd_str:
            try:
                qtd = int(qtd_str)
                movimentacao_valida = False
                
                if operacao == 'retirar' and not reserva:
                    messages.error(request, "Erro: Para realizar uma SAÍDA, informe o Número da Reserva!")
                    return redirect('detalhe_peca', id=peca.id)

                if operacao == 'adicionar':
                    peca.quantidade += qtd
                    peca.save()
                    movimentacao_valida = True
                    messages.success(request, f"Entrada de {qtd} un. realizada com sucesso!")
                    
                elif operacao == 'retirar':
                    if peca.quantidade >= qtd:
                        peca.quantidade -= qtd
                        peca.save()
                        movimentacao_valida = True
                        messages.success(request, f"Saída de {qtd} un. realizada com sucesso (Reserva: {reserva})!")
                    else:
                        messages.error(request, f"Estoque insuficiente! Saldo disponível: {peca.quantidade} un.")
                
                if movimentacao_valida:
                    HistoricoMovimentacao.objects.create(
                        peca=peca,
                        usuario=request.user,
                        tipo=operacao,
                        quantidade=qtd,
                        saldo_momento=peca.quantidade,
                        numero_reserva=reserva if operacao == 'retirar' else None
                    )
                        
            except ValueError:
                messages.error(request, "Quantidade informada inválida.")
            
            return redirect('detalhe_peca', id=peca.id)

    return render(request, 'pecas/detalhe_peca.html', {
        'peca': peca,
        'historico': historico
    })


@login_required
def cadastrar_peca(request):
    if not request.user.is_staff:
        return redirect('/')

    from .forms import PecaForm
    form = PecaForm(
        request.POST or None,
        request.FILES or None
    )

    if form.is_valid():
        form.save()
        messages.success(request, "Peça cadastrada com sucesso!")
        return redirect('/')

    return render(
        request,
        'pecas/cadastrar_peca.html',
        {'form': form}
    )