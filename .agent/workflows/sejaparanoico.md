---
description: Como modificar código com segurança (Protocolo de Sobrevivência)
---

# 🛑 Protocolo Obrigatório - MODO PARANOICO

1. **PARE.** Leia e siga fielmente as Global Rules.
2. **CRIE BACKUPS (.bak).** Sempre, sem exceção, antes de qualquer alteração.
3. **PRECISÃO CIRÚRGICA.** Faça a modificação com acurácia, evite quebrar códigos adjacentes.
4. **PROVA DE CONCEITO (MANDATÓRIO).** NUNCA entregue uma tarefa como "pronta" ou "corrigida" sem antes:
    - Verificar fisicamente se o arquivo foi gravado no disco (`view_file`).
    - Validar a sintaxe (`python manage.py check` ou equivalente).
    - Simular a execução ou verificar logs de erro para garantir que a causa raiz foi eliminada.
5. **SCRIPTS DE PATCH.** Não use o editor para modificações complexas. Use scripts Python para garantir que a lógica, indentação (Django `==`, `endif`) e parsing estejam perfeitos.
6. **ATUE COMO DEV SENIOR.** Não aceite falhas bobas. Se o código estava funcionando e parou, você é o responsável por rastrear a regressão e restaurá-la integralmente.
7. **TRANSPARÊNCIA TOTAL.** Se algo falhar, admita, restaure o backup e tente uma abordagem mais segura.
