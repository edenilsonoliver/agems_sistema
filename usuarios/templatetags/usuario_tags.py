from django import template

register = template.Library()

@register.filter
def can_edit(user, target_user):
    """
    Verifica se o usuário logado (user) tem permissão para editar o usuário alvo (target_user).
    Uso no template: {% if user|can_edit:target_user %}
    """
    if not hasattr(user, 'pode_editar_usuario'):
        return False
    return user.pode_editar_usuario(target_user)
