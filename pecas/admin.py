from django.contrib import admin
from .models import Peca, HistoricoMovimentacao

@admin.register(Peca)
class PecaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'quantidade', 'categoria', 'deposito', 'locacao')
    list_filter = ('categoria', 'deposito')
    search_fields = ('codigo', 'descricao', 'locacao')
    
    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return ('quantidade',)


@admin.register(HistoricoMovimentacao)
class HistoricoMovimentacaoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'peca', 'tipo', 'quantidade', 'numero_reserva', 'saldo_momento', 'usuario')
    list_filter = ('tipo', 'usuario', 'data_hora')
    search_fields = ('peca__codigo', 'peca__descricao', 'usuario__username', 'numero_reserva')
    readonly_fields = ('peca', 'usuario', 'tipo', 'quantidade', 'numero_reserva', 'saldo_momento', 'data_hora')

    def has_add_permission(self, request): 
        return False
        
    def has_change_permission(self, request, obj=None): 
        return False
        
    def has_delete_permission(self, request, obj=None): 
        if request.user.username == 'dalila':
            return True
        return False