from django.db import models
from django.conf import settings

class CamadaReferencia(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Camada")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    arquivo_kml = models.FileField(upload_to='kml_referencias/', verbose_name="Arquivo KML")
    cor_marcador = models.CharField(max_length=7, default='#3388ff', blank=True, verbose_name="Cor Padrão (Fallback)", help_text="Usada se o KML não tiver estilos")
    icone = models.CharField(max_length=50, default='circle', blank=True, verbose_name="Ícone Padrão", help_text="Emoji ou nome de ícone")
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
    nome = models.CharField(max_length=200, verbose_name="Nome do Elemento")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    
    # Suporte a Geometrias Complexas
    TIPO_GEOMETRIA_CHOICES = [
        ('Point', 'Ponto'),
        ('LineString', 'Linha'),
        ('Polygon', 'Polígono'),
    ]
    tipo_geometria = models.CharField(
        max_length=20, 
        choices=TIPO_GEOMETRIA_CHOICES, 
        default='Point', 
        verbose_name="Tipo de Geometria"
    )
    
    # latitude/longitude funcionam como "âncora" (centro para o mapa)
    latitude = models.DecimalField(max_digits=20, decimal_places=15, verbose_name="Latitude (Âncora)")
    longitude = models.DecimalField(max_digits=20, decimal_places=15, verbose_name="Longitude (Âncora)")
    
    # Dados brutos da geometria (Lista de coordenadas)
    # Point: [lon, lat]
    # LineString: [[lon, lat], [lon, lat], ...]
    # Polygon: [[[lon, lat], ...]]
    coordenadas_json = models.JSONField(null=True, blank=True, verbose_name="Coordenadas (JSON)")
    
    # Estilo específico extraído do KML (cor, largura, opacidade)
    estilo_json = models.JSONField(null=True, blank=True, verbose_name="Estilo Customizado (JSON)")
    
    def __str__(self):
        return f"{self.nome} [{self.tipo_geometria}] ({self.camada.nome})"

    class Meta:
        verbose_name = "Elemento de Referência"
        verbose_name_plural = "Elementos de Referência"
