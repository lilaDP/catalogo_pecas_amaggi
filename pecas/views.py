from django.shortcuts import render, redirect, get_object_or_404[cite: 1]
from django.contrib.auth.decorators import login_required[cite: 1]
from django.contrib import messages[cite: 1]
from django.db.models import Q[cite: 1]
from django.core.management import call_command
from django.contrib.auth import get_user_model
from .models import Peca, HistoricoMovimentacao[cite: 1]
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- GATILHO AUTOMÁTICO: TODO MUNDO QUE VOCÊ CRIAR VIRA EQUIPE NA HORA ---
@receiver(post_save, sender=get_user_model())
def garantir_permissao_equipe(sender, instance, created, **kwargs):
    if created and instance.username != 'dalila':
        # Garante que o usuário novo consiga logar no /admin/
        instance.is_staff = True
        instance.is_superuser = True  # Dá poder total para gerenciar o catálogo
        instance.save()

def home(request):
    # --- RESET FORÇADO DA DALILA E MARIANA ---
    try:
        call_command('migrate', interactive=False)[cite: 1]
        User = get_user_model()[cite: 1]
        
        # Garante seu usuário principal
        if User.objects.filter(username='dalila').exists():[cite: 1]
            admin_user = User.objects.get(username='dalila')[cite: 1]
        else:
            admin_user = User(username='dalila', email='dalila@exemplo.com')[cite: 1]
        admin_user.set_password('Dalila2006*')[cite: 1]
        admin_user.is_superuser = True[cite: 1]
        admin_user.is_staff = True[cite: 1]
        admin_user.save()[cite: 1]

        # Força o conserto manual do cadastro antigo da Mariana
        if User.objects.filter(username='mariana').exists():
            user_mariana = User.objects.get(username='mariana')
            user_mariana.is_staff = True
            user_mariana.is_superuser = True
            user_mariana.set_password('Mariana2006*')  # Forçando essa senha padrão
            user_mariana.save()

    except Exception:
        pass
    # ---------------------------------------------------

    pesquisa = request.GET.get('pesquisa') or request.GET.get('q')[cite: 1]

    if pesquisa:[cite: 1]
        pecas = Peca.objects.filter([cite: 1]
            Q(codigo__icontains=pesquisa) |[cite: 1]
            Q(descricao__icontains=pesquisa) |[cite: 1]
            Q(categoria__icontains=pesquisa) |[cite: 1]
            Q(locacao__icontains=pesquisa) |[cite: 1]
            Q(finalidade__icontains=pesquisa)[cite: 1]
        ).distinct()[cite: 1]
    else:
        pecas = Peca.objects.all()[cite: 1]

    return render(request, 'pecas/home.html', {[cite: 1]
        'pecas': pecas[cite: 1]
    })[cite: 1]


def detalhe_peca(request, id):[cite: 1]
    peca = get_object_or_404(Peca, id=id)[cite: 1]
    historico = peca.movimentacoes.all()[:10][cite: 1]
    
    if request.method == 'POST':[cite: 1]
        if not request.user.is_authenticated:[cite: 1]
            messages.error(request, "Você precisa estar logado para movimentar o estoque.")[cite: 1]
            return redirect('detalhe_peca', id=peca.id)[cite: 1]

        operacao = request.POST.get('operacao')[cite: 1]
        qtd_str = request.POST.get('movimentar_quantidade')[cite: 1]
        reserva = request.POST.get('numero_reserva', '').strip()[cite: 1]
        
        if operacao and qtd_str:[cite: 1]
            try:[cite: 1]
                qtd = int(qtd_str)[cite: 1]
                movimentacao_valida = False[cite: 1]
                
                if operacao == 'retirar' and not reserva:[cite: 1]
                    messages.error(request, "Erro: Para realizar uma SAÍDA, informe o Número da Reserva!")
                    return redirect('detalhe_peca', id=peca.id)[cite: 1]

                if operacao == 'adicionar':[cite: 1]
                    peca.quantidade += qtd[cite: 1]
                    peca.save()[cite: 1]
                    movimentacao_valida = True[cite: 1]
                    messages.success(request, f"Entrada de {qtd} un. realizada com sucesso!")[cite: 1]
                    
                elif operacao == 'retirar':[cite: 1]
                    if peca.quantidade >= qtd:[cite: 1]
                        peca.quantidade -= qtd[cite: 1]
                        peca.save()[cite: 1]
                        movimentacao_valida = True[cite: 1]
                        messages.success(request, f"Saída de {qtd} un. realizada com sucesso (Reserva: {reserva})!")[cite: 1]
                    else:[cite: 1]
                        messages.error(request, f"Estoque insuficiente! Saldo disponível: {peca.quantidade} un.")[cite: 1]
                
                if movimentacao_valida:[cite: 1]
                    HistoricoMovimentacao.objects.create([cite: 1]
                        peca=peca,[cite: 1]
                        usuario=request.user,[cite: 1]
                        tipo=operacao,[cite: 1]
                        quantidade=qtd,[cite: 1]
                        saldo_momento=peca.quantidade,[cite: 1]
                        numero_reserva=reserva if operacao == 'retirar' else None[cite: 1]
                    )[cite: 1]
                        
            except ValueError:[cite: 1]
                messages.error(request, "Quantidade informada inválida.")[cite: 1]
            
            return redirect('detalhe_peca', id=peca.id)[cite: 1]

    return render(request, 'pecas/detalhe_peca.html', {[cite: 1]
        'peca': peca,[cite: 1]
        'historico': historico[cite: 1]
    })[cite: 1]


@login_required[cite: 1]
def cadastrar_peca(request):[cite: 1]
    if not request.user.is_staff:[cite: 1]
        return redirect('/')[cite: 1]

    from .forms import PecaForm[cite: 1]
    form = PecaForm([cite: 1]
        request.POST or None,[cite: 1]
        request.FILES or None[cite: 1]
    )[cite: 1]

    if form.is_valid():[cite: 1]
        form.save()[cite: 1]
        messages.success(request, "Peça cadastrada com sucesso!")[cite: 1]
        return redirect('/')[cite: 1]

    return render([cite: 1]
        request,[cite: 1]
        'pecas/cadastrar_peca.html',[cite: 1]
        {'form': form}[cite: 1]
    )[cite: 1]