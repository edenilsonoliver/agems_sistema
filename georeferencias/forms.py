from django import forms
from .models import CamadaReferencia
from .kml_validator import validate_kml_file

class CamadaReferenciaForm(forms.ModelForm):
    class Meta:
        model = CamadaReferencia
        fields = ['nome', 'descricao', 'arquivo_kml', 'ativo']

    def clean_arquivo_kml(self):
        arquivo = self.cleaned_data.get('arquivo_kml')
        if not arquivo:
            return arquivo

        # 1. Validar extensão
        if not arquivo.name.lower().endswith('.kml'):
            raise forms.ValidationError("Apenas arquivos .kml são suportados.")

        # 2. Validar tamanho máximo (10MB)
        limit_mb = 10
        if arquivo.size > limit_mb * 1024 * 1024:
            raise forms.ValidationError(f"O tamanho máximo do arquivo é {limit_mb}MB.")

        # 3. Validar MIME / Magic Type anti-spoofing
        try:
            import magic
            initial_pos = arquivo.tell()
            arquivo.seek(0)
            mime_type = magic.from_buffer(arquivo.read(2048), mime=True)
            arquivo.seek(initial_pos)

            valid_mimes = [
                'application/vnd.google-earth.kml+xml',
                'application/xml',
                'text/xml',
                'application/octet-stream'
            ]
            if mime_type not in valid_mimes:
                raise forms.ValidationError(f"Tipo de arquivo inválido ({mime_type}). Esperado arquivo KML/XML.")
        except Exception as e:
            if isinstance(e, forms.ValidationError):
                raise e
            pass

        # 4. Pré-validação com o módulo KMLValidator
        validation_result = validate_kml_file(arquivo)
        if not validation_result['is_valid']:
            raise forms.ValidationError(
                validation_result['error_message'] or "O arquivo KML é inválido ou não possui elementos válidos."
            )

        # Anexar resultado da validação ao objeto de arquivo para ser consumido na View
        arquivo.validation_summary = validation_result
        return arquivo
