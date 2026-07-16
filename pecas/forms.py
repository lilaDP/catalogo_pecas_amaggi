from django import forms
from .models import Peca

class PecaForm(forms.ModelForm):
    class Meta:
        model = Peca
        fields = '__all__'
        
        # Injeta classes Tailwind diretamente nos elementos gerados pelo Django
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white transition-all',
                'placeholder': 'Ex: POS-102030'
            }),

            'descricao': forms.TextInput(attrs={
                'class': 'w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white transition-all',
                'placeholder': 'Ex: Alternador de arranque Volvo FH'
            }),

            'quantidade': forms.NumberInput(attrs={
                'class': 'w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white transition-all',
                'placeholder': '0',
                'min': '0'
            }),

            'categoria': forms.Select(attrs={
                'class': 'w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white transition-all cursor-pointer'
            }),

            'deposito': forms.Select(attrs={
                'class': 'w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white transition-all cursor-pointer uppercase font-mono'
            }),

            # NOVO WIDGET ADICIONADO: LOCAÇÃO FÍSICA
            'locacao': forms.TextInput(attrs={
                'class': 'w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white transition-all',
                'placeholder': 'Ex: Corredor A - Prateleira 3 - Gaveta B'
            }),

            'finalidade': forms.Textarea(attrs={
                'class': 'w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white transition-all resize-y min-h-[100px]',
                'placeholder': 'Insira as especificações ou aplicações técnicas da peça...'
            }),

            # ALTERADO: De ClearableFileInput para URLInput para receber links da internet no cadastro do site
            'imagem': forms.URLInput(attrs={
                'class': 'w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white transition-all',
                'placeholder': 'Ex: https://exemplo.com/imagem-da-peca.jpg'
            }),
        }