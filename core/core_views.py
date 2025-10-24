from .views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView
from .models import Diretoria, TipoEntidade, TipoServico, TipoInstrumento, TipoObrigacao, TipoAcao
from django.urls import reverse_lazy
from django.urls import reverse_lazy
from core.models import Subunidade
from core.views import ModernListView, ModernCreateView, ModernUpdateView, ModernDeleteView

# Diretoria
class DiretoriaListView(ModernListView):
    model = Diretoria
    icon = "bi bi-building"
    create_url = 'diretoria_create'

class DiretoriaCreateView(ModernCreateView):
    model = Diretoria
    fields = '__all__'
    success_url = reverse_lazy('diretoria_list')

class DiretoriaUpdateView(ModernUpdateView):
    model = Diretoria
    fields = '__all__'
    success_url = reverse_lazy('diretoria_list')

class DiretoriaDeleteView(ModernDeleteView):
    model = Diretoria
    success_url = reverse_lazy('diretoria_list')

# TipoEntidade
class TipoEntidadeListView(ModernListView):
    model = TipoEntidade
    icon = "bi bi-tag"
    create_url = 'tipoentidade_create'

class TipoEntidadeCreateView(ModernCreateView):
    model = TipoEntidade
    fields = '__all__'
    success_url = reverse_lazy('tipoentidade_list')

class TipoEntidadeUpdateView(ModernUpdateView):
    model = TipoEntidade
    fields = '__all__'
    success_url = reverse_lazy('tipoentidade_list')

class TipoEntidadeDeleteView(ModernDeleteView):
    model = TipoEntidade
    success_url = reverse_lazy('tipoentidade_list')

# TipoServico
class TipoServicoListView(ModernListView):
    model = TipoServico
    icon = "bi bi-wrench"
    create_url = 'tiposervico_create'

class TipoServicoCreateView(ModernCreateView):
    model = TipoServico
    fields = '__all__'
    success_url = reverse_lazy('tiposervico_list')

class TipoServicoUpdateView(ModernUpdateView):
    model = TipoServico
    fields = '__all__'
    success_url = reverse_lazy('tiposervico_list')

class TipoServicoDeleteView(ModernDeleteView):
    model = TipoServico
    success_url = reverse_lazy('tiposervico_list')

# TipoInstrumento
class TipoInstrumentoListView(ModernListView):
    model = TipoInstrumento
    icon = "bi bi-file-earmark"
    create_url = 'tipoinstrumento_create'

class TipoInstrumentoCreateView(ModernCreateView):
    model = TipoInstrumento
    fields = '__all__'
    success_url = reverse_lazy('tipoinstrumento_list')

class TipoInstrumentoUpdateView(ModernUpdateView):
    model = TipoInstrumento
    fields = '__all__'
    success_url = reverse_lazy('tipoinstrumento_list')

class TipoInstrumentoDeleteView(ModernDeleteView):
    model = TipoInstrumento
    success_url = reverse_lazy('tipoinstrumento_list')

# TipoObrigacao
class TipoObrigacaoListView(ModernListView):
    model = TipoObrigacao
    icon = "bi bi-list-check"
    create_url = 'tipoobrigacao_create'

class TipoObrigacaoCreateView(ModernCreateView):
    model = TipoObrigacao
    fields = '__all__'
    success_url = reverse_lazy('tipoobrigacao_list')

class TipoObrigacaoUpdateView(ModernUpdateView):
    model = TipoObrigacao
    fields = '__all__'
    success_url = reverse_lazy('tipoobrigacao_list')

class TipoObrigacaoDeleteView(ModernDeleteView):
    model = TipoObrigacao
    success_url = reverse_lazy('tipoobrigacao_list')

# TipoAcao
class TipoAcaoListView(ModernListView):
    model = TipoAcao
    icon = "bi bi-lightning"
    create_url = 'tipoacao_create'

class TipoAcaoCreateView(ModernCreateView):
    model = TipoAcao
    fields = '__all__'
    success_url = reverse_lazy('tipoacao_list')

class TipoAcaoUpdateView(ModernUpdateView):
    model = TipoAcao
    fields = '__all__'
    success_url = reverse_lazy('tipoacao_list')

class TipoAcaoDeleteView(ModernDeleteView):
    model = TipoAcao
    success_url = reverse_lazy('tipoacao_list')

class SubunidadeListView(ModernListView):
    model = Subunidade
    title = 'Subunidades'
    subtitle = 'Gerencie as subunidades vinculadas às diretorias'
    icon = 'bi bi-diagram-3'
    search_fields = ['nome', 'sigla', 'diretoria__nome']
    create_url = 'subunidade_create'


class SubunidadeCreateView(ModernCreateView):
    model = Subunidade
    fields = ['nome', 'sigla', 'diretoria', 'responsavel', 'ativa']
    success_url = reverse_lazy('subunidade_list')
    icon = 'bi bi-plus-circle'


class SubunidadeUpdateView(ModernUpdateView):
    model = Subunidade
    fields = ['nome', 'sigla', 'diretoria', 'responsavel', 'ativa']
    success_url = reverse_lazy('subunidade_list')
    icon = 'bi bi-pencil-square'


class SubunidadeDeleteView(ModernDeleteView):
    model = Subunidade
    success_url = reverse_lazy('subunidade_list')
