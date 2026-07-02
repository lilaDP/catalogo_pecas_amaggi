from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.management import call_command
from django.contrib.auth import get_user_model
from .models import Peca, HistoricoMovimentacao

def home(request):
    # --- RESET FORÇADO DE SENHA (À PROVA DE FALHAS) ---
    try:
        # Tenta criar as tabelas se não existirem
        call_command('migrate', interactive=False)[cite: 1]
        
        # Puxa o modelo de usuário do Django
        User = get_user_model()[cite: 1]
        
        # 1. Garante a usuária dalila
        if User.objects.filter(username='dalila').exists():[cite: 1]
            admin_user = User.objects.get(username='dalila')[cite: 1]
        else:
            admin_user = User(username='dalila', email='dalila@exemplo.com')[cite: 1]
        
        admin_user.set_password('Dalila2006*')[cite: 1]
        admin_user.is_superuser = True[cite: 1]
        admin_user.is_staff = True[cite: 1]
        admin_user.save()[cite: 1]

        # 2. RESOLVENDO O LOGIN DA MARIANA (Criptografia e Equipe automáticos)
        if User.objects.filter(username='mariana').exists():
            user_mariana = User.objects.get(username='mariana')
            user_mariana.set_password('Mariana2006*')  # <-- Defina a senha dela aqui (Criptografada)
            user_mariana.is_staff = True               # <-- Ativa a permissão de equipe obrigatória
            user_mariana.is_superuser = True           # <-- Dá os mesmos poderes administrativos que os seus
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