from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.core.management import call_command
from django.contrib.auth import get_user_model

# --- TRUQUE PARA CRIAR AS TABELAS E O ADMIN AUTOMATICAMENTE NA VERCEL ---
try:
    print("Criando tabelas no banco temporario da Vercel...")
    call_command('migrate', interactive=False)
    
    # Configuração do novo administrador
    USER_ADMIN = 'dalila'
    PASSWORD_ADMIN = 'adm123'  # <-- Altere aqui para a senha que você preferir!
    
    User = get_user_model()
    if not User.objects.filter(username=USER_ADMIN).exists():
        print(f"Criando usuario administrador: {USER_ADMIN}...")
        User.objects.create_superuser(username=USER_ADMIN, email=EMAIL_ADMIN, password=PASSWORD_ADMIN)
        print("Administrador criado com sucesso!")
except Exception as e:
    print(f"Erro no script automatico: {e}")
# -----------------------------------------------------------------------

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pecas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)