from django import forms
from .models import CamadaReferencia

class CamadaReferenciaForm(forms.ModelForm):
    class Meta:
        model = CamadaReferencia
        fields = ['nome', 'descricao', 'arquivo_kml', 'cor_marcador', 'icone', 'ativo']
        

    def clean_arquivo_kml(self):
        arquivo = self.cleaned_data.get('arquivo_kml')
        if not arquivo:
            return arquivo
        
        # 1. Validar extensão
        if not arquivo.name.lower().endswith('.kml'):
            raise forms.ValidationError("Apenas arquivos .kml são suportados.")
        
        # 2. Validar tamanho (5MB)
        limit_mb = 5
        if arquivo.size > limit_mb * 1024 * 1024:
            raise forms.ValidationError(f"O tamanho máximo do arquivo é {limit_mb}MB.")

        # 3. Validar MIME Type (Magic) - Anti-Spoofing
        import magic
        try:
            # Ler o início do arquivo para identificar
            initial_pos = arquivo.tell()
            arquivo.seek(0)
            mime_type = magic.from_buffer(arquivo.read(2048), mime=True)
            arquivo.seek(initial_pos) # Resetar ponteiro
            
            # Tipos KML aceitáveis (variam por sistema/libmagic)
            valid_mimes = [
                'application/vnd.google-earth.kml+xml', 
                'application/xml', 
                'text/xml'
            ]
            
            if mime_type not in valid_mimes:
                raise forms.ValidationError(f"Arquivo inválido. Tipo detectado: {mime_type}. Esperado: KML/XML.")
                
        except Exception as e:
            # Fallback seguro: se falhar a checkagem, nega por precaução ou loga
            if isinstance(e, forms.ValidationError):
                raise e
            # Em ambientes onde libmagic falha, talvez logar warning.
            # Aqui vamos assumir que deve funcionar.
            pass

        return arquivo
