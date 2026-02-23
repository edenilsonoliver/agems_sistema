# Especificação Funcional — Aba "Conformidades" como Especialização de Ação do tipo Fiscalização

## 1. Objetivo

Criar uma nova aba chamada **"Conformidades"** dentro da entidade existente **Ação**, como uma especialização exclusiva para ações cujo tipo seja **Fiscalização**.

Este recurso NÃO é um novo módulo do sistema e NÃO deve ser implementado como um novo app Django independente.

Trata-se de uma extensão funcional e relacional da entidade já existente **Ação**.

---

## 2. Regra de Ativação

A aba **Conformidades** deve ser exibida somente quando o tipo da Ação for igual a:

**Fiscalização**

Se o tipo da Ação for qualquer outro, a aba não deve ser exibida e o recurso não deve estar acessível.

---

## 3. Posicionamento da Aba na Interface

A aba **Conformidades** deve aparecer na interface dentro da página de Ação.

Sua posição deve ser imediatamente antes da aba existente:

**Documentos/Evidências**

A ordem correta das abas deve respeitar a sequência lógica já existente no sistema, apenas inserindo Conformidades antes de Documentos/Evidências.

---

## 4. Estrutura da Aba Conformidades

A aba Conformidades representa um conjunto de grupos de verificação associados à Ação.

Cada Conformidade deve possuir:

- Um identificador único gerado automaticamente pelo sistema
- Um nome descritivo da Conformidade
- Uma lista de itens verificáveis (checklist)

Cada Conformidade pertence exclusivamente a uma única Ação.

---

## 5. Estrutura dos Itens de Conformidade

Cada Conformidade pode possuir um ou mais itens.

Cada item representa um elemento verificável dentro da Conformidade.

Cada item deve possuir:

- Identificador único gerado automaticamente
- Nome ou descrição do item
- Um estado de verificação (checkbox tri-estado)

---

## 6. Comportamento do Checkbox (Tri-State)

O checkbox de cada item deve possuir três estados possíveis:

Estado 1:
- Valor interno: 0
- Representação visual: caixa vazia (neutro)
- Significado: item ainda não verificado

Estado 2:
- Valor interno: 1
- Representação visual: caixa verde com símbolo de check (✅)
- Significado: item conforme

Estado 3:
- Valor interno: -1
- Representação visual: caixa vermelha com símbolo de X (❌)
- Significado: item não conforme

O comportamento deve seguir o ciclo abaixo a cada clique do usuário:

Neutro → Conforme → Não conforme → Neutro → (repetir ciclo)

Este comportamento deve ocorrer sem recarregar a página.

---

## 7. Constatações

Cada item de Conformidade pode possuir uma ou mais Constatações.

Uma Constatação é um registro textual descritivo que detalha observações relacionadas ao item.

Características das Constatações:

- Associadas a um único item
- Um item pode possuir várias constatações
- Cada constatação contém apenas texto descritivo
- Devem ser exibidas dentro do contexto do item correspondente

---

## 8. Integração com Fotos

Cada item de Conformidade pode possuir uma ou mais fotos associadas.

O sistema já possui um recurso de fotos vinculado à Ação, e este recurso deve ser reutilizado.

O usuário deve poder:

- Selecionar fotos já existentes associadas à Ação
- Ou adicionar uma nova foto diretamente dentro do contexto do item

Quando uma nova foto for adicionada:

- Ela deve ser associada à Ação
- Ela deve ser associada ao item de Conformidade
- Ela deve aparecer automaticamente na aba existente de Fotos da Ação

Não deve haver duplicação desnecessária de fotos.

As fotos devem permanecer como recurso centralizado da Ação.

---

## 9. Comportamento Geral do Recurso

Fluxo esperado:

Quando o usuário acessa uma Ação cujo tipo é Fiscalização:

- A aba Conformidades deve estar visível
- O usuário pode criar uma ou mais Conformidades
- Dentro de cada Conformidade, o usuário pode criar um ou mais itens
- O usuário pode alterar o estado dos itens clicando no checkbox
- O usuário pode adicionar constatações a cada item
- O usuário pode associar fotos existentes ou adicionar novas fotos
- Todas as interações devem ocorrer sem recarregar a página completamente

Quando o tipo da Ação NÃO for Fiscalização:

- A aba Conformidades não deve existir visualmente
- Nenhuma funcionalidade relacionada deve estar disponível

---

## 10. Regras de Arquitetura

Este recurso é uma especialização da entidade Ação existente.

Portanto:

- Não deve ser criado um novo módulo independente
- Não deve ser criado um novo tipo de entidade paralela à Ação
- Não deve duplicar a lógica da Ação existente
- Deve reutilizar a estrutura e arquitetura já existente

Todo o recurso deve existir como extensão relacional da Ação.

---

## 11. Requisitos de Experiência do Usuário

O sistema deve permitir:

- Criação dinâmica de Conformidades
- Criação dinâmica de itens
- Alteração de status de forma rápida e intuitiva
- Inclusão de constatações diretamente no item
- Associação e inclusão de fotos sem navegação para outra página
- Interface fluida e responsiva

Não deve exigir recarregamento completo da página para interações comuns.

---

## 12. Resultado Esperado

O sistema passará a possuir um recurso completo de registro de Conformidades vinculado exclusivamente a ações do tipo Fiscalização.

Este recurso permitirá registrar:

- Estrutura de verificação
- Estado de conformidade
- Observações detalhadas
- Evidências fotográficas

Tudo integrado à entidade Ação já existente no sistema.

---

Fim da especificação.