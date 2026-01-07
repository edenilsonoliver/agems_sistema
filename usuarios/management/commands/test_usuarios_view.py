from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from usuarios.views import UsuarioListView

class Command(BaseCommand):
    help = 'Testa a view de listagem de usuários'
    
    def handle(self, *args, **options):
        User = get_user_model()
        
        # Pegar usuário admin
        try:
            admin = User.objects.get(username='admin')
            self.stdout.write(f"✅ Admin encontrado: {admin.username} (perfil={admin.perfil})")
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Usuário admin não encontrado!"))
            return
        
        # Simular request
        factory = RequestFactory()
        request = factory.get('/usuarios/')
        request.user = admin
        
        # Criar view
        view = UsuarioListView()
        view.request = request
        
        # Pegar queryset
        try:
            qs = view.get_queryset()
            self.stdout.write(f"\n📊 Resultado do get_queryset():")
            self.stdout.write(f"   Total de usuários: {qs.count()}")
            
            if qs.count() > 0:
                self.stdout.write(f"\n👥 Usuários retornados:")
                for u in qs:
                    self.stdout.write(f"   - {u.username} (perfil={u.perfil}, ativo={u.is_active})")
            else:
                self.stdout.write(self.style.WARNING("\n⚠️  Queryset vazio! Nenhum usuário retornado."))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Erro ao executar get_queryset(): {e}"))
            import traceback
            traceback.print_exc()

