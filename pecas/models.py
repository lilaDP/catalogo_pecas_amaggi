from django.db import models
from django.contrib.auth.models import User

OPCOES_DEPOSITO = [
    ('pc01', 'PC01'),
    ('pc02', 'PC02'),
    ('tint', 'TINT'),
    ('lb01', 'LB01'),
    ('temp', 'TEMP'),
    ('ep01', 'EP01'),
    ('un01', 'UN01'),
    ('pne1', 'PNE1 - Depósito de Pneus 1'),
    ('pne2', 'PNE2 - Depósito de Pneus 2'),
]

OPCOES_CATEGORIA = [
    ('mecanicos', 'Componentes Mecânicos'),
    ('quimicos_paintura', 'Químicos e Pintura'),
    ('fluidos_lubrificantes', 'Fluidos e Lubrificantes'),
    ('uniformes_epis', 'Uniformes e EPIs'),
    ('pneu_novo', 'Pneu Novo'),
    ('pneu_recapado', 'Pneu Recapado'),
]

OPCOES_UNIDADE = [
    ('unidade', 'Unidade'),
    ('quilos', 'Quilos'),
    ('litros', 'Litros'),
]

class Peca(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código")
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    quantidade = models.IntegerField(default=0, verbose_name="Quantidade")
    unidade_medida = models.CharField(max_length=10, choices=OPCOES_UNIDADE, default='unidade', verbose_name="Unidade de Medida")
    deposito = models.CharField(max_length=10, choices=OPCOES_DEPOSITO, blank=True, null=True, verbose_name="Depósito")
    categoria = models.CharField(max_length=50, choices=OPCOES_CATEGORIA, blank=True, null=True, verbose_name="Categoria")
    locacao = models.CharField(max_length=100, blank=True, null=True, verbose_name="Locação da Peça")
    # ALTERADO: De ImageField para URLField para aceitar links da internet
    imagem = models.URLField(max_length=500, blank=True, null=True, verbose_name="Link da Imagem da Peça")
    finalidade = models.TextField(blank=True, null=True, verbose_name="Descrição Operacional e Aplicação")

    class Meta:
        verbose_name = "Peça"
        verbose_name_plural = "Peças"

    def __str__(self):
        return f"{self.codigo} - {self.descricao}"


class HistoricoMovimentacao(models.Model):
    TIPOS_MOVIMENTACAO = [
        ('adicionar', 'Entrada'),
        ('retirar', 'Saída'),
    ]

    peca = models.ForeignKey(Peca, on_delete=models.CASCADE, related_name='movimentacoes', verbose_name="Peça")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuário")
    tipo = models.CharField(max_length=10, choices=TIPOS_MOVIMENTACAO, verbose_name="Tipo de Operação")
    quantidade = models.IntegerField(verbose_name="Quantidade Movimentada")
    saldo_momento = models.IntegerField(verbose_name="Saldo no Momento")
    numero_reserva = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número da Reserva")
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")

    class Meta:
        ordering = ['-data_hora']
        verbose_name = "Histórico de Movimentação"
        verbose_name_plural = "Histórico de Movimentações"

    def __str__(self):
        user_str = self.usuario.username if self.usuario else "Sistema/Admin"
        return f"{self.get_tipo_display()} de {self.quantidade} un. - {self.peca.codigo} por {user_str}"