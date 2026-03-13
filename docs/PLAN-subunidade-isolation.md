# PLAN: Isolamento Rigoroso por Subunidade

## 🚨 O Problema Atual (Vazamento Intra-Diretoria)
O usuário relatou a seguinte falha crítica de negócio:
> "uma pessoa da CATENE (subunidade) em DGE (Diretoria) está vendo coisas da CATEGAS (subunidade da DGE)"

**Análise da Causa Raiz:**
1. O modelo `Instrumento` possui apenas o campo `diretoria`. O banco de dados **não sabe** a qual subunidade o Instrumento pertence.
2. Como reflexo do banco, o utilitário `get_diretoria_filter` para os perfis 2, 3 e 4 pega a subunidade do usuário e extrai a diretoria (`user.subunidade.diretoria`). 
3. O filtro aplicado na listagem é literalmente: `Traga tudo da Diretoria DGE`. Portanto, Técnicos/Coordenadores da CATENE recebem todos os dados da DGE, sobrepondo os dados da CATEGAS.

---

## 🏗️ A Solução Estrutural (Migração de Banco)

Para que o sistema **separe e saiba** o que é da CATENE e o que é da CATEGAS, a entidade raiz (`Instrumento`) precisa de um "Dono" em nível de Subunidade.

### Fase 1: Atualização dos Models (`instrumentos/models.py`)
- Adicionar o campo `subunidade` ao Model `Instrumento`:
  ```python
  subunidade = models.ForeignKey(
      'core.Subunidade',
      on_delete=models.PROTECT,
      verbose_name='Subunidade Responsável',
      related_name='instrumentos',
      null=True,  # Para retrocompatibilidade inicial com os dados antigos
      blank=True
  )
  ```
- Gerar e rodar o `makemigrations` e `migrate`.

### Fase 2: O Novo Filtro de Contexto (`usuarios/mixins.py`)
- O `get_diretoria_filter` não pode mais olhar apenas para a Diretoria, ele tem que ser atualizado para um conceito de **`get_unidade_filter`**.
- O Admin (0) e Diretor (1) continuam vendo tudo da Diretoria (DGE como um todo).
- Os Perfis 2 e 3 (Assessoria e Coordenação) devem retornar a clausula `Q(subunidade=user.subunidade)`.
- O Perfil 4 deve obedecer a mesma regra.

### Fase 3: Formulários Seguros (`instrumentos/forms.py` e `acoes/forms.py`)
- O `InstrumentoForm` passará a ter o campo `subunidade` (visível para o Admin e Diretor para distribuir os processos; fixado/disabled para o Coordenador criar algo já amarrado na sua própria).
- No momento da Criação (`InstrumentoCreateView`), interceptar o objeto e setar: `instrumento.subunidade = request.user.subunidade`.

### Fase 4: O Escudo Dinâmico (`AcaoForm`)
- Ajustar a rotina de filtro dinâmico de `Responsável` e `Executores` na criação da Ação.
- O Coordenador da CATENE agora selecionará Instrumentos que pertencem à sua Subunidade e só verá usuários **que também sejam** da sua Subunidade.

---

## 🕵️ Socratic Gate (Dúvidas de Negócio)

Antes de gerar os códigos e sujar a base de dados com uma Migration, preciso que o Gestor do Produto responda **OBRIGATORIAMENTE** a essas duas questões cruciais:

1. **Retroatividade:** Você terá dezenas de `Instrumentos` no banco que hoje marcam `DGE` mas o campo novo `subunidade` nascerá vazio (Null). Como faremos com os antigos? O Diretor ou Admin vai passar um a um vinculando-os à CATENE / CATEGAS, ou você quer um script que tente "adivinhar" baseado nos responsáveis pelas ações filhas?
2. **Visualização Direcional:** O Diretor da DGE (Perfil 1) pode enxergar tanto CATENE quanto CATEGAS. Mas o Assessor (Perfil 2) da categoria inteira DGE (sem subunidade específica) deve enxergar tudo ou o Assessor (2) também tem uma Subunidade cravada no perfil dele?

**Aguardo o "OK" para essas regras e iniciarei a reestruturação dos dados.**
