# PLAN: Restrições de Edição para Executores e Notificações

## Contexto

**1. Restrição de Edição (Somente para "Executores" em Ações):**
O "Responsável" (geralmente o Coordenador, mas pode ser um Técnico) é o **dono** da Ação, portanto, **pode editar TUDO** nela.
A restrição aplica-se **apenas** aos usuários que são *apenas* "Executores" (listados no campo M2M `executores`) e não são os responsáveis nem perfis superiores (Admin/Diretor/Assessor).
Esse "Apenas Executor" deve poder editar SOOMENTE os seguintes campos de feedback:
- Status
- Data de conclusão
- Observações
- Resultados (resultado, justiticativa, entidade)
- Checklists (Sub-tarefas) e Fotos.

Os demais campos devem aparecer bloqueados (disabled).

**2. Restrição Global para Executores (Instrumentos, Obrigações e Entidades):**
Usuários com perfil de Executor (Perfil 4) ou Coordenador (Perfil 3) - dependendo do requisito de negócio, mas focaremos nos Executores - **não podem criar nem editar Entidades, Instrumentos ou Obrigações**. 
Isso exige garantir que os métodos `get_readonly()` ou `dispatch()` dessas views bloqueiem ativamente o acesso de edição para esses perfis. (Atualmente, `InstrumentoUpdateView.get_readonly()` já bloqueia os perfis 3 e 4, mas validaremos/reforçaremos isso também para as Entidades).

**3. Notificações ("Sininho"):**
O sistema já possui o módulo `alertas` com o model `Notificacao`. Quando uma ação for atribuída a um novo executor, ele deve receber uma notificação do tipo `atribuicao` e título "Nova Ação Atribuída".

---

## 1. Implementação das Restrições (Formulário e Views)

### Validação de Instrumentos e Entidades (`instrumentos/views.py` e `entidades/views.py`)
- Em `instrumentos/views.py` e `entidades/views.py`, certificar que `get_readonly()` retorna `True` ou `dispatch()` bloqueia (redireciona com Erro 403 / Mensagem) a criação e edição para usuários de perfil `4` (Executor). No caso de `readonly=True`, os forms aparecem, mas a view deve barrar as operações de salvamento de fato.

### `acoes/forms.py`
Adicionar um novo parâmetro `executor_readonly=False` no `__init__` do `AcaoForm`.
```python
self.executor_readonly = kwargs.pop('executor_readonly', False)
if self.executor_readonly:
    allowed_fields = ['status', 'data_conclusao', 'observacoes', 'resultado', 'entidade', 'justificativa_resultado']
    for field_name, field in self.fields.items():
        if field_name not in allowed_fields:
            field.disabled = True
```
> **Por que `disabled`?** Campos disabled no Django form não são alterados no POST, garantindo segurança contra manipulação de payload, já que o ModelForm pega o dado direto da `.instance`.

### `acoes/views.py` (AcaoUpdateView)
Calcular se o usuário logado é um "Apenas Executor":
```python
def get_form_kwargs(self):
    kwargs = super().get_form_kwargs()
    obj = self.get_object()
    user = self.request.user
    
    # Se NÃO é o responsável E NÃO é Admin/Diretor/Assessor
    # E ESTÁ na lista de executores -> então é apenas executor
    is_apenas_executor = False
    if user != obj.responsavel and user.perfil not in [0, 1, 2]:
        if user in obj.executores.all():
            is_apenas_executor = True
            
    kwargs['executor_readonly'] = is_apenas_executor
    return kwargs
```

---

## 2. Implementação das Notificações (Sinais)

A tabela `alertas_notificacao` e o manager (`Notificacao.criar_notificacao`) já existem.

**Desafio:** O campo `executores` é um `ManyToManyField`. Não é possível rastreá-lo no `post_save` curinga. Precisamos usar o sinal `m2m_changed`.

### Criar `acoes/signals.py`
Registrar o receiver para `m2m_changed` no modelo `Acao.executores.through`.
Ação a mapear:
Quando `m2m_changed` despachar a `action == "post_add"`:
- Pegar os IDs recém-adicionados (`kwargs.get('pk_set')`)
- Gerar uma Notificação para cada um usando `Notificacao.criar_notificacao()`.
- Tipo: `atribuicao`
- Título: "Nova Ação Atribuída"
- Link: URL de detalhes/edição da ação.

*Nota:* Precisamos também garantir que a App `acoes/apps.py` esteja importando os signals no `ready()`.

---

## 3. Análise de Risco e Mitigação (Protocolo Sejaparanoico)

### Formulário da Ação (`AcaoForm` com `executor_readonly`)
- **Risco:** O usuário pode inspecionar o HTML e remover a tag `disabled` dos inputs.
- **Mitigação Embutida:** No Django `ModelForm`, campos marcados como `disabled=True` são explicitamente **ignorados** na reconstrução do `cleaned_data` a partir do POST payload. O form preenche o dado da própria instância do banco (`self.instance`). É 100% seguro.

### Restrição Global (Entidades, Instrumentos, Obrigações)
- **Risco:** Técnicos continuarem acessando as rotas de criar/editar desses módulos via URL direta.
- **Mitigação Embutida:** As views já estão (ou serão garantidas em código) utilizando `get_readonly()` para os perfis não-gerenciais, que além de apresentar a interface congelada, barram a validação na rota `form_valid()` enviando o usuário redirecionado com Mensagem de Erro e não alterando nada no DB.

### Notificações via Signal M2M
- **Risco:** Flood no banco de dados. Um coordenador pode adicionar e remover o mesmo técnico várias vezes seguidas enquanto edita a Ação. Cada `post_add` vai inserir um alerta igual e encher a área de notificações.
- **Mitigação Planejada (Obrigatória no signal):**
  1. Processar apenas `action == "post_add"`.
  2. Executar um _Debounce_ Lógico: Antes de salvar o `Notificacao.criar_notificacao()`, verificar se na última **1 hora** já existe uma notificação do tipo `atribuicao` para essa `Acao` e esse `Usuario`. Se sim, ignorar.
  3. Evitar _Circular Imports_. Fazer a conexão do _receiver_ especificando a tabela sender `Acao.executores.through`.
