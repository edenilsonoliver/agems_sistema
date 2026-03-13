# PLAN: Instrumento com Múltiplas Subunidades

## Contexto e Objetivo
O modelo atual utiliza uma `ForeignKey` única para vincular um `Instrumento` a uma `Subunidade`. No entanto, na realidade do negócio da AGEMS, um instrumento (como um contrato de concessão transversal) pode ser gerido por múltiplas subunidades da mesma diretoria.

O objetivo deste plano é migrar para um relacionamento `ManyToManyField`, garantindo que o controle de acesso (RBAC) seja expandido para permitir que usuários de **qualquer** uma das subunidades vinculadas possam ver e gerenciar o instrumento e suas ações filhas.

---

## 🛑 Socratic Gate (Dúvidas de Negócio)

Para garantir que a implementação não seja outra "gambiarra", preciso da confirmação destes pontos:

1. **Restrição de Diretoria:** Todas as subunidades selecionadas para um Instrumento devem obrigatoriamente pertencer à `Diretoria` selecionada no campo acima? Ou um instrumento pode cruzar fronteiras de Diretorias (ex: CATENE da DGE e uma subunidade da DTR)?
2. **Visibilidade de Analistas:** Ao criar uma Ação para um instrumento com Subunidades A e B, o sistema deve listar usuários de *ambas* as subunidades para serem executores?
3. **Migração de Dados:** Posso converter os dados atuais (campo único) automaticamente para a nova lista mapeada?

---

## 🏗️ Mudanças Propostas

### 1. Modelagem (`instrumentos/models.py`)
- [NEW] Campo `subunidades = models.ManyToManyField('core.Subunidade', ...)`
- [DELETE] Remover ou desativar o campo `subunidade` (FK unica) após a migração de dados.

### 2. Utilitários de Filtro (`usuarios/mixins.py`)
- Atualizar `get_diretoria_filter`:
  - Para perfis 2, 3 e 4: Mudar filtro para `Q(subunidades=user.subunidade)`. No Django, isso o ORM resolve com um JOIN automático.
- Atualizar `verifica_acesso_unidade`:
  - Verificar se `user.subunidade` está contido em `obj.subunidades.all()`.

### 3. Formulários (`instrumentos/forms.py` e `acoes/forms.py`)
- `InstrumentoForm`: Mudar o widget do campo `subunidades` para um seletor múltiplo (checkboxes ou select multiple com buscador).
- `AcaoForm`: Filtrar o queryset de usuários responsáveis e executores para trazer pessoas de **todas** as subunidades vinculadas ao instrumento da ação.

---

## 🏁 Plano de Verificação

### Testes Automatizados
- Scripts de migração de dados: Verificar se o instrumento "Contrato X" que era da CATENE agora tem `catene` na sua lista M2M.
- Teste de QuerySet: Usuário da CATEGAS tentando acessar Instrumento da CATENE (deve falhar se não estiver na lista).
- Teste de QuerySet: Usuário da CATENE acessando Instrumento vinculado a [CATENE, CATEGAS] (deve permitir).

### Teste Manual
1. Criar Instrumento e selecionar 2 Subunidades.
2. Logar com usuário da Subunidade 1 -> Verificar acesso.
3. Logar com usuário da Subunidade 2 -> Verificar acesso.
4. Logar com usuário de uma Subunidade 3 (mesma diretoria) -> Verificar bloqueio.
