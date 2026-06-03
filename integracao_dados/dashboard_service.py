from django.utils import timezone
from .models import Dashboard, CompartilhamentoAnalitico

class DashboardAcessoService:
    """
    Serviço que consolida a lógica de controle de acesso (RBAC) 
    para visualização e edição de Dashboards (RF010.4).
    """

    @staticmethod
    def pode_acessar(user, dashboard):
        """Verifica se o usuário tem permissão de leitura."""
        if not user or not user.is_authenticated:
            return False

        # Admin tem acesso total
        if user.perfil == 0:
            return True

        # Se for o criador, tem acesso
        if dashboard.criador_id == user.id:
            return True

        # Se for da mesma diretoria proprietária
        # Nota: Assume que perfis 1-4 possuem atributo `diretoria` configurado
        user_diretoria = getattr(user, 'diretoria', None)
        if user_diretoria and dashboard.diretoria_proprietaria_id == user_diretoria.id:
            return True

        # Verifica compartilhamentos explícitos
        if user_diretoria:
            compartilhamento = CompartilhamentoAnalitico.objects.filter(
                dashboard=dashboard,
                diretoria_destino=user_diretoria
            ).first()
            
            if compartilhamento:
                # Verifica se não expirou
                if compartilhamento.data_expiracao and compartilhamento.data_expiracao < timezone.now().date():
                    return False
                return True

        return False

    @staticmethod
    def pode_editar(user, dashboard):
        """Verifica se o usuário tem permissão de edição/colaboração."""
        if not user or not user.is_authenticated:
            return False

        if getattr(user, 'is_dataset_manager', False) or user.perfil == 0:
            return True

        # O criador pode editar
        if dashboard.criador_id == user.id:
            return True

        # Verifica se há compartilhamento explícito de colaboração
        user_diretoria = getattr(user, 'diretoria', None)
        if user_diretoria:
            compartilhamento = CompartilhamentoAnalitico.objects.filter(
                dashboard=dashboard,
                diretoria_destino=user_diretoria,
                nivel_acesso='colaboracao'
            ).first()

            if compartilhamento:
                if compartilhamento.data_expiracao and compartilhamento.data_expiracao < timezone.now().date():
                    return False
                return True

        return False
