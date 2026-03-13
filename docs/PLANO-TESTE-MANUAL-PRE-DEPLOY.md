# Plano de Testes Manual e Validação Pré-Produção 🚀

Este checklist foi desenhado para você validar pessoalmente as regras de negócio construídas em torno do Isolamento de Dados (RBAC) e das Restrições de Edição do Executor, garantindo que tudo funcione impecavelmente antes do deploy para produção.

---

## 🗂️ Preparação do Ambiente

Antes de iniciar os testes, garanta que você possui os seguintes usuários configurados localmente ou na base de staging:
- [X] **Admin** (Perfil `0`)
- [X] **Diretor D1** (Perfil `1`, vinculado à Diretoria "A")
- [X] **Diretor D2** (Perfil `1`, vinculado à Diretoria "B")
- [X] **Assessor/Coordenador C1** (Perfil `2` ou `3`, vinculado a uma Subunidade da Diretoria "A")
- [X] **Técnico T1** (Perfil `4`, vinculado à Diretoria "A", apenas Executor)
- [X] **Técnico T2** (Perfil `4`, vinculado à Diretoria "A", Executor, mas colocado como Responsável em uma Ação)

> **Dica:** Utilize navegadores diferentes (ou Abas Anônimas) para logar com dois usuários ao mesmo tempo e constatar os filtros ativando e desativando dinamicamente.

---

## ✅ Módulo 1: Isolamento de Visualização por Diretoria (RBAC)

### 1.1 Teste de Visibilidade do Diretor e Assessor (Perfil 1, 2, 3)
- [X] Logue com **Diretor D1**.
- [X] No Dashboard, certifique-se de que os números sumariados (Total de Instrumentos, Entidades, Ações, Obrigações) refletem apenas o que pertence à **Diretoria A**.
- [X] Acesse a listagem de *Instrumentos*. Você **NÃO** deve ver instrumentos que pertençam à Diretoria B.
- [X] Acesse a listagem de *Ações*. Você **NÃO** deve ver ações derivadas de instrumentos da Diretoria B.
- [X] Vá ao *Calendário de Ações*. Os marcos visíveis devem corresponder apenas à Diretoria A.

### 1.2 Teste de Barreira e Segurança de Acesso
- [X] Logue com **Admin (0)**. Copie a URL de edição de um Instrumento ou Ação que pertença exclusivamente à *Diretoria B*.
- [X] Deslogue.
- [X] Logue com **Diretor D1**.
- [X] Cole a URL na barra de endereços (tentativa forçada de acesso). O sistema **DEVE** bloqueá-lo com a mensagem de erro: `"Você não tem permissão para editar instrumentos/ações de outra diretoria."` e redirecionar para a lista.

## ✅ Módulo 2: Restrições de Ações para Executores (UX & Form)

### 2.1 Visão Restrita do Apenas Executor (Perfil 4)
- [X] Crie (com Coordenador C1) uma *Nova Ação* e atribua a mesma ao **Técnico T1** no campo `Executores`. Configure um outro usuário qualquer como `Responsável`.
- [X] Logue com **Técnico T1**.
- [X] Abra a Ação recém-atribuída para edição.
- [X] **Verificação Mestra:** Tente editar campos essenciais. O *Nome*, *Descrição*, *Datas de Início/Fim*, *Múltipla escolha de Executores* e a *Obrigação* devem estar estáticos e cinzas (`disabled`).
- [X] Adicione uma *Observação*, altere o *Status* para "Em Progresso" e clique no Switch de um *Checklist*.
- [X] Salve. 
- [X] Volte à ação e confirme que: a) Os dados de feedback foram gravados. b) O formulário manteve seguro e inalterado o resto (Nome, Instrumento de origem, etc).

### 2.2 Visão Irrestrita do Dono (Responsável)
- [X] Crie (com Coordenador C1) uma segunda *Nova Ação* e atribua ao **Técnico T2**, mas agora coloque **Técnico T2** explicitamente no campo `Responsável`.
- [X] Logue com **Técnico T2**.
- [X] Acesse a mesma Ação.
- [X] **Verificação Mestra:** Confirme que **TUDO** está habilitado para edição. Como Responsável, o Técnico T2 é o dono da ação e possui pleno domínio do formulário.


### 2.3 Tentativa de Inspeção (Hack HTML)
- [X] Logue novamente como o **Técnico T1** (restrito).
- [X] Use o botão direito -> *Inspecionar Elemento* no campo `Nome da Ação`. Remova manualmente o atributo `disabled="disabled"` do código HTML da página.
- [X] Digite e altere o nome da Ação para outro nome absurdo ("Ação Hackeada"). 
- [X] Salve o formulário.
- [X] Verifique no banco ou na lista: O nome da Ação **NÃO DEVE** ter sido alterado (o backend ignora o POST de campos bloqueados). O preenchimento deve voltar magicamente ao que era originalmente no banco de dados.

---

## ✅ Módulo 3: Notificação de Atribuição Constante (Signal)

### 3.1 Disparo Automático (Campainha)
- [X] Abra qualquer Ação já existente em modo edição.
- [X] Vá na caixa de "Executores" (teclando CTRL para selecionar múltiplos) e adicione o **Técnico T1** e salve.
- [X] Logue com o **Técnico T1**.
- [X] Verifique a "Sininha" / Tela de Notificações (`/alertas/` ou equivalente visual do sistema). 
- [X] Confirme a chegada do alerta do tipo `atribuicao` com o título: *"Nova Ação Atribuída: [nome da ação]"* com o link funcional clicável que leva pra página de edição.

### 3.2 O "Debounce" Lógico (Anti-Flood Trolls)
- [X] Logue como **Coordenador C1**.
- [X] Volte à última Ação que editou. Repita o processo: Remova o Técnico T1, salve. Edite novamente. Adicione o Técnico T1, salve. Edite novamente. Faça isso 3 ou 4 vezes seguidas dentro da mesma janela de poucos minutos.
- [X] Logue como **Técnico T1**.
- [-] Verifique sua central de notificações. Deve haver **Apenas 1** alerta daquela Ação. O código não envia repetidos quando o intervalo é inferior a 1 hora. {--  está zerado!!! --}

---

## ✅ Módulo 4: Restrição Global para Entidades, Instrumentos e Obrigações

### 4.1 Teste de Bloqueio em Nível de UX
- [X] Entre com o **Técnico T1**.
- [X] Navegue pelos menus laterais onde ficam `Entidades` (Concessionárias, Prefeituras) e `Instrumentos`.
- [-] Confirme que os botões de "+ Criar" e "Editar/Lápis" ou estão completamente visíveis apenas como "Ver" (`readonly=True`) na lista ou não existem para ele. {-- está aparecendo o botão de editar, porém não há campos editaveis e gera uma msg "modo visualização" mas tudo bem! --}

### 4.2 Teste de Segurança em Nível Endpoint
- [X] Com o mesmo usuário **Técnico T1** logado, "tente" violar a barra de navegação direto na URL exata: cole `/entidades/criar/` ou localize o ID e jogue `/entidades/1/editar/`.
- [X] A tela **DEVE** travar com redirecionamento contendo a mensagem "Você não tem permissão para salvar / acessar". O Django não processará NADA submetido.

---
Se todas as caixinhas acima baterem positivamente — e eu desenhei o código de forma que devem bater —, você pode puxar as atualizações da branch principal (`main`) para seu Servidor e dar reinício no **Docker** da nuvem com a paz de espírito absoluta de um bom sysadmin. 🥂
