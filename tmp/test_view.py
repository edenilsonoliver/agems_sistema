import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from instrumentos.views import InstrumentoUpdateView
from usuarios.models import Usuario
from instrumentos.models import Instrumento

def test_view_context():
    try:
        user = Usuario.objects.get(username='tecnico1')
        inst = Instrumento.objects.get(pk=4)
        
        factory = RequestFactory()
        request = factory.get(f'/instrumentos/{inst.id}/editar/')
        request.user = user
        
        view = InstrumentoUpdateView()
        view.request = request
        view.kwargs = {'pk': inst.id}
        view.object = inst
        
        context = view.get_context_data()
        
        print(f"User: {user.username} (Perfil: {user.perfil})")
        print(f"Instrument: {inst.numero} (ID: {inst.id})")
        print(f"Readonly in context: {context.get('readonly')}")
        
        formset = context.get('formset')
        if formset:
            print(f"Formset records: {len(formset.forms)}")
            if len(formset.forms) > 0:
                first_form = formset.forms[0]
                print(f"First form 'titulo' disabled: {first_form.fields['titulo'].disabled}")
                print(f"First form instance: {first_form.instance}")
        else:
            print("Formset not found in context!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_view_context()
