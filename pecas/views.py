from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone  # IMPORTADO: Para capturar a data atual do servidor
from .models import Peca, HistoricoMovimentacao

def home(request):
    # --- ROTA LIMPA E LEVE (SEM RISCO DE ERRO 500) ---
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
    
    # FILTRO DIÁRIO: Pega apenas a data de hoje (ano-mês-dia) desconsiderando as horas
    hoje = timezone.localdate()
    
    # Filtra as movimentações da peça realizadas HOJE, ordenando das mais recentes para as mais antigas
    # (Substitua 'data_hora' pelo nome do campo de data do seu model HistoricoMovimentacao se for diferente)
    historico = peca.movimentacoes.filter(data_hora__date=hoje).order_by('-data_hora')
    
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
