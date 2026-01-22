---
description: Protocolo de Segurança, Rollback e Codificação AGEMS
---

# 🛡️ Protocolo de Segurança e Rollback AGEMS

Este workflow DEVE ser seguido em todas as tarefas que envolvam modificação de arquivos de código ou templates.

## 0. Prerequisito Obrigatório
**Antes de codar, você deve declarar para o usuário:**
- Exatamente qual arquivo você vai editar.
- Onde está (ou será criado) o backup dele (ex: `caminho/arquivo.ext.bak`).
- Qual a sua estratégia de verificação final (ex: abrir URL X, verificar log Y).

## 1. Preparação e Backup
- [ ] Verifique se o ambiente está estável.
- [ ] **Sempre** crie um backup físico antes de qualquer alteração:
  `cp caminho/do/arquivo.ext caminho/do/arquivo.ext.bak`

## 2. Codificação e Idioma (PT-BR)
- [ ] Garanta que o arquivo seja salvo em **UTF-8 (sem BOM)**.
- [ ] **NUNCA** remova acentos ou use entidades HTML para contornar problemas de encoding.
- [ ] Use português correto nos templates e mensagens.

## 3. Desenvolvimento e Sintaxe
- [ ] Siga as boas práticas de Django e Python.
- [ ] Garanta espaços em tags de template: `{% if val == 'exemplo' %}` (espaços ao redor de `==`).
- [ ] Valide a sintaxe antes de considerar a tarefa "em teste".

## 4. Verificação Final (Obrigatória)
- [ ] Use o `browser_subagent` ou `run_command` para validar o resultado.
- [ ] A tarefa só está concluída se a página renderizar sem Erro 500 e a funcionalidade desejada for confirmada visualmente ou por logs.

## 5. Rollback em Caso de Falha
- [ ] Se um erro persistente (Erro 500, SyntaxError) não for resolvido em 2 tentativas, você **DEVE** restaurar o backup original imediatamente:
  `cp caminho/do/arquivo.ext.bak caminho/do/arquivo.ext`
- [ ] Informe ao usuário sobre o rollback e analise o erro no backup antes de tentar novamente.

---
// turbo-all
