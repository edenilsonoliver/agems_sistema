# Generated migration for updating Usuario model with new profiles and fields

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('usuarios', '0002_usuario_subunidade'),
    ]

    operations = [
        # Alterar campo perfil de CharField para IntegerField
        migrations.AlterField(
            model_name='usuario',
            name='perfil',
            field=models.IntegerField(
                choices=[
                    (0, 'Admin'),
                    (1, 'Diretoria'),
                    (2, 'Assessoria'),
                    (3, 'Coordenação'),
                    (4, 'Usuário Comum'),
                    (5, 'Visualizador')
                ],
                default=4,
                help_text='Define o nível de acesso e permissões do usuário',
                verbose_name='Perfil de Acesso'
            ),
        ),
        
        # Adicionar campo diretoria
        migrations.AddField(
            model_name='usuario',
            name='diretoria',
            field=models.ForeignKey(
                blank=True,
                help_text='Diretoria principal do usuário (obrigatório para perfis 1-5)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='usuarios_diretoria',
                to='core.diretoria',
                verbose_name='Diretoria'
            ),
        ),
        
        # Adicionar campo senha_temporaria
        migrations.AddField(
            model_name='usuario',
            name='senha_temporaria',
            field=models.BooleanField(
                default=False,
                help_text='Se True, usuário será forçado a trocar senha no próximo login',
                verbose_name='Senha Temporária'
            ),
        ),
        
        # Adicionar campo ManyToMany diretorias_visualizacao
        migrations.AddField(
            model_name='usuario',
            name='diretorias_visualizacao',
            field=models.ManyToManyField(
                blank=True,
                help_text='Diretorias que o visualizador pode acessar (apenas para perfil 5)',
                related_name='visualizadores',
                to='core.diretoria',
                verbose_name='Diretorias para Visualização'
            ),
        ),
        
        # Adicionar índices para performance
        migrations.AddIndex(
            model_name='usuario',
            index=models.Index(fields=['perfil'], name='usuarios_us_perfil_idx'),
        ),
        migrations.AddIndex(
            model_name='usuario',
            index=models.Index(fields=['diretoria'], name='usuarios_us_direto_idx'),
        ),
        migrations.AddIndex(
            model_name='usuario',
            index=models.Index(fields=['subunidade'], name='usuarios_us_subuni_idx'),
        ),
    ]

