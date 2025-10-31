# Generated migration for Notificacao and PreferenciaNotificacao models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('tarefa_atrasada', 'Tarefa Atrasada'), ('tarefa_vencendo_hoje', 'Tarefa Vencendo Hoje'), ('tarefa_a_vencer', 'Tarefa a Vencer'), ('tarefa_nova', 'Nova Tarefa'), ('obrigacao_vencendo', 'Obrigação Vencendo'), ('instrumento_expirando', 'Instrumento Expirando'), ('comentario', 'Novo Comentário'), ('atribuicao', 'Tarefa Atribuída'), ('mudanca_status', 'Mudança de Status')], max_length=50, verbose_name='Tipo')),
                ('prioridade', models.CharField(choices=[('baixa', 'Baixa'), ('media', 'Média'), ('alta', 'Alta'), ('urgente', 'Urgente')], default='media', max_length=20, verbose_name='Prioridade')),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('mensagem', models.TextField(blank=True, verbose_name='Mensagem')),
                ('link', models.CharField(help_text='URL para onde a notificação leva', max_length=200, verbose_name='Link')),
                ('tarefa_id', models.IntegerField(blank=True, null=True, verbose_name='ID da Tarefa')),
                ('obrigacao_id', models.IntegerField(blank=True, null=True, verbose_name='ID da Obrigação')),
                ('instrumento_id', models.IntegerField(blank=True, null=True, verbose_name='ID do Instrumento')),
                ('lida', models.BooleanField(default=False, verbose_name='Lida')),
                ('data_leitura', models.DateTimeField(blank=True, null=True, verbose_name='Data de Leitura')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')),
                ('data_expiracao', models.DateTimeField(blank=True, help_text='Notificação será removida após esta data', null=True, verbose_name='Data de Expiração')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificacoes', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Notificação',
                'verbose_name_plural': 'Notificações',
                'ordering': ['-data_criacao'],
            },
        ),
        migrations.CreateModel(
            name='PreferenciaNotificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notificar_tarefa_atrasada', models.BooleanField(default=True, verbose_name='Notificar Tarefa Atrasada')),
                ('notificar_tarefa_vencendo', models.BooleanField(default=True, verbose_name='Notificar Tarefa Vencendo')),
                ('notificar_tarefa_nova', models.BooleanField(default=True, verbose_name='Notificar Nova Tarefa')),
                ('notificar_obrigacao', models.BooleanField(default=True, verbose_name='Notificar Obrigação')),
                ('notificar_comentario', models.BooleanField(default=True, verbose_name='Notificar Comentário')),
                ('enviar_email', models.BooleanField(default=False, help_text='Receber notificações por e-mail', verbose_name='Enviar E-mail')),
                ('frequencia_email', models.CharField(choices=[('imediato', 'Imediato'), ('diario', 'Resumo Diário'), ('semanal', 'Resumo Semanal')], default='diario', max_length=20, verbose_name='Frequência de E-mail')),
                ('tocar_som', models.BooleanField(default=True, help_text='Tocar som ao receber notificação', verbose_name='Tocar Som')),
                ('mostrar_toast', models.BooleanField(default=True, help_text='Mostrar notificação visual (toast)', verbose_name='Mostrar Toast')),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferencia_notificacao', to=settings.AUTH_USER_MODEL, verbose_name='Usuário')),
            ],
            options={
                'verbose_name': 'Preferência de Notificação',
                'verbose_name_plural': 'Preferências de Notificação',
            },
        ),
        migrations.AddIndex(
            model_name='notificacao',
            index=models.Index(fields=['usuario', 'lida'], name='alertas_not_usuario_lida_idx'),
        ),
        migrations.AddIndex(
            model_name='notificacao',
            index=models.Index(fields=['usuario', 'data_criacao'], name='alertas_not_usuario_data_idx'),
        ),
        migrations.AddIndex(
            model_name='notificacao',
            index=models.Index(fields=['tipo', 'usuario'], name='alertas_not_tipo_usuario_idx'),
        ),
    ]

