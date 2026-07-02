from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from django.utils.html import format_html
from django.contrib import messages
from django.middleware.csrf import get_token
from .models import Peca, HistoricoMovimentacao

@admin.register(Peca)
class PecaAdmin(admin.ModelAdmin):
    # Reativados todos os campos novos para exibição e filtragem lateral no admin
    list_display = ('codigo', 'descricao', 'quantidade', 'categoria', 'deposito', 'locacao', 'botoes_movimentacao')
    list_filter = ('categoria', 'deposito')
    search_fields = ('codigo', 'descricao', 'locacao')
    
    readonly_fields = ('quantidade',)

    def changelist_view(self, request, extra_context=None):
        self.current_request = request
        return super().changelist_view(request, extra_context=extra_context)

    def botoes_movimentacao(self, obj):
        token = get_token(self.current_request)
        opts = self.model._meta
        action_url = f'/admin/{opts.app_label}/{opts.model_name}/{obj.id}/movimentar/'
        
        return format_html(
            '''
            <form method="POST" action="{}" style="display:inline-flex; align-items:center; gap:5px; margin:0;">
                <input type="hidden" name="csrfmiddlewaretoken" value="{}">
                <select name="operacao" style="padding: 2px 5px; height: 24px; border-radius: 4px; font-size: 11px; border: 1px solid #ccc; background: white; font-weight: bold;">
                    <option value="adicionar" style="color: #2e7d32;">＋ Entrada</option>
                    <option value="retirar" style="color: #c62828;">－ Saída</option>
                </select>
                <input type="number" name="movimentar_quantidade" value="1" min="1" 
                       style="width: 45px; padding: 2px; text-align: center; border-radius: 4px; border: 1px solid #ccc; font-size: 11px; height: 24px; box-sizing: border-box;">
                <button type="submit" style="padding: 0 10px; background: #264b5d; color: white; border-radius: 4px; border: none; cursor: pointer; font-size: 10px; font-weight: bold; height: 24px; line-height: 24px;">
                    Lançar
                </button>
            </form>
            ''',
            action_url,
            token
        )
    botoes_movimentacao.short_description = 'Movimentação Rápida'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:peca_id>/movimentar/', self.admin_site.admin_view(self.processar_movimentacao), name='peca-movimentar'),
        ]
        return custom_urls + urls

    def processar_movimentacao(self, request, peca_id):
        if request.method == 'POST':
            peca = self.get_object(request, peca_id)
            operacao = request.POST.get('operacao')
            qtd_str = request.POST.get('movimentar_quantidade')

            if peca and operacao and qtd_str:
                try:
                    qtd = int(qtd_str)
                    movimentacao_valida = False
                    
                    if operacao == 'adicionar':
                        peca.quantidade += qtd
                        peca.save()
                        movimentacao_valida = True
                        messages.success(request, f"Entrada de {qtd} un. para a peça {peca.codigo}.")
                    elif operacao == 'retirar':
                        if peca.quantidade >= qtd:
                            peca.quantidade -= qtd
                            peca.save()
                            movimentacao_valida = True
                            messages.success(request, f"Saída de {qtd} un. para a peça {peca.codigo}.")
                        else:
                            messages.error(request, f"Estoque insuficiente na peça {peca.codigo}.")
                    
                    if movimentacao_valida:
                        HistoricoMovimentacao.objects.create(
                            peca=peca, usuario=request.user, tipo=operacao, quantidade=qtd, saldo_momento=peca.quantidade
                        )
                except ValueError:
                    messages.error(request, "Quantidade inválida.")
        
        opts = self.model._meta
        return redirect(f'admin:{opts.app_label}_{opts.model_name}_changelist') 

@admin.register(HistoricoMovimentacao)
class HistoricoMovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'peca', 'tipo', 'quantidade', 'saldo_momento', 'usuario')
    list_filter = ('tipo', 'usuario', 'data_hora')
    search_fields = ('peca__codigo', 'peca__descricao', 'usuario__username')
    readonly_fields = ('peca', 'usuario', 'tipo', 'quantidade', 'saldo_momento', 'data_hora')

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False