import logging
import time

logger = logging.getLogger('audit')

class AuditMiddleware:
    """
    Middleware para auditoria simplificada de ações de modificação (POST, PUT, DELETE).
    Registra quem fez o quê, onde e quando.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Processa a requisição
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        # Verifica se é uma requisição de modificação ou login/logout
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            user = request.user
            user_ident = user.username if user.is_authenticated else 'Anonymous'
            
            # Formata log
            ip = self.get_client_ip(request)
            status = response.status_code
            path = request.path
            
            log_message = (
                f"AUDIT | User: {user_ident} | IP: {ip} | Method: {request.method} | "
                f"Path: {path} | Status: {status} | Duration: {duration:.3f}s"
            )
            
            # Loga com nível INFO (configurar logger depois)
            # Por enquanto, logamos no logger padrão se 'audit' não estiver configurado
            if status >= 400:
                logger.warning(log_message)
            else:
                logger.info(log_message)

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
