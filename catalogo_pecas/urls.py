from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.core.management import call_command

# --- TRUQUE PARA CRIAR AS TABELAS AUTOMATICAMENTE NA VERCEL ---
try:
    print("Criando tabelas no banco temporario da Vercel...")
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Erro ao rodar as migracoes: {e}")
# --------------------------------------------------------------

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pecas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)