from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from .models import CamadaReferencia, PontoReferencia
from .forms import CamadaReferenciaForm

class CamadaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CamadaReferencia
    permission_required = 'georeferencias.view_camadareferencia'
    template_name = 'georeferencias/camada_list.html'
    context_object_name = 'camadas'
    paginate_by = 10
    extra_context = {
        'title': 'Camadas de Referência',
        'subtitle': 'Gerencie arquivos KML para visualização no mapa',
        'create_url': 'georeferencias:camada_create',
        'singular_name': 'Camada',
        'icon': 'bi-layers'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Recuperar resumo da sessão se houver resultado recente de importação KML
        if 'kml_import_resumo' in self.request.session:
            context['kml_import_resumo'] = self.request.session.pop('kml_import_resumo')
        return context

class CamadaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = CamadaReferencia
    permission_required = 'georeferencias.add_camadareferencia'
    template_name = 'georeferencias/camada_form.html'
    form_class = CamadaReferenciaForm
    success_url = reverse_lazy('georeferencias:camada_list')

    def form_valid(self, form):
        from .kml_parser import parse_kml

        form.instance.criado_por = self.request.user
        try:
            with transaction.atomic():
                response = super().form_valid(form)  # Salva o arquivo primeiro

                # Parsear KML
                parse_result = parse_kml(self.object.arquivo_kml.path)
                elementos = parse_result.get('elementos', [])
                descartados = parse_result.get('descartados', [])

                if not elementos:
                    messages.warning(
                        self.request,
                        "O arquivo KML foi salvo, mas nenhum elemento válido foi encontrado para importação."
                    )
                else:
                    elementos_objs = [
                        PontoReferencia(
                            camada=self.object,
                            nome=p.get('nome', 'Sem Nome')[:200],
                            descricao=p.get('descricao', ''),
                            tipo_geometria=p.get('tipo_geometria', 'Point'),
                            latitude=p['latitude'],
                            longitude=p['longitude'],
                            coordenadas_json=p.get('coordenadas'),
                            estilo_json=p.get('estilo')
                        ) for p in elementos
                    ]
                    PontoReferencia.objects.bulk_create(elementos_objs)

                    # Registrar resumo de importação na sessão para exibição no Modal
                    self.request.session['kml_import_resumo'] = {
                        'camada_nome': self.object.nome,
                        'total_importados': len(elementos),
                        'total_descartados': len(descartados),
                        'descartados_detalhes': descartados
                    }

                    if descartados:
                        messages.warning(
                            self.request,
                            f"Camada criada com sucesso! {len(elementos)} elementos importados e {len(descartados)} elementos descartados por inconsistência."
                        )
                    else:
                        messages.success(
                            self.request,
                            f"Camada de referência processada com sucesso! {len(elementos)} elementos importados."
                        )

        except Exception as e:
            messages.error(self.request, f"Falha ao processar o arquivo KML: {e}")
            return self.form_invalid(form)

        return response

class CamadaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = CamadaReferencia
    permission_required = 'georeferencias.change_camadareferencia'
    template_name = 'georeferencias/camada_form.html'
    fields = ['nome', 'descricao', 'ativo']  # Removidos cor_marcador e icone
    success_url = reverse_lazy('georeferencias:camada_list')

    def form_valid(self, form):
        messages.success(self.request, "Camada atualizada com sucesso.")
        return super().form_valid(form)

class CamadaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = CamadaReferencia
    permission_required = 'georeferencias.delete_camadareferencia'
    success_url = reverse_lazy('georeferencias:camada_list')
    template_name = 'georeferencias/camada_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Camada de referência excluída com sucesso.")
        return super().delete(request, *args, **kwargs)

# --- API Endpoints ---

@login_required
@require_GET
def api_list_camadas(request):
    """Retorna lista de camadas ativas para o frontend"""
    camadas = CamadaReferencia.objects.filter(ativo=True).values(
        'id', 'nome', 'descricao'
    )
    return JsonResponse({'camadas': list(camadas)})

@login_required
@require_GET
def api_get_pontos_camada(request, camada_id):
    """Retorna os pontos e geometrias de uma camada específica com seus estilos nativos KML"""
    try:
        camada = CamadaReferencia.objects.get(id=camada_id, ativo=True)
        pontos = camada.pontos.values(
            'nome', 'descricao', 'latitude', 'longitude',
            'tipo_geometria', 'coordenadas_json', 'estilo_json'
        )
        return JsonResponse({
            'camada_id': camada.id,
            'camada_nome': camada.nome,
            'pontos': list(pontos)
        })
    except CamadaReferencia.DoesNotExist:
        return JsonResponse({'error': 'Camada não encontrada ou inativa'}, status=404)
