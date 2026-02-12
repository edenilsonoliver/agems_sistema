from django.db import models
from django.conf import settings

class CamadaReferencia(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Camada")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    arquivo_kml = models.FileField(upload_to='kml_referencias/', verbose_name="Arquivo KML")
    cor_marcador = models.CharField(max_length=7, default='#3388ff', verbose_name="Cor dos Pontos", help_text="Cor HEX (ex: #3388ff)")
    icone = models.CharField(max_length=50, default='circle', verbose_name="Ícone", help_text="Nome do ícone (ex: circle, square)")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Criado por"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Camada de Referência"
        verbose_name_plural = "Camadas de Referência"
        ordering = ['-data_criacao']

class PontoReferencia(models.Model):
    camada = models.ForeignKey(CamadaReferencia, related_name='pontos', on_delete=models.CASCADE)
    nome = models.CharField(max_length=200, verbose_name="Nome do Ponto")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    latitude = models.DecimalField(max_digits=20, decimal_places=15, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=20, decimal_places=15, verbose_name="Longitude")
    
    def __str__(self):
        return f"{self.nome} ({self.camada.nome})"

    class Meta:
        verbose_name = "Ponto de Referência"
        verbose_name_plural = "Pontos de Referência"
