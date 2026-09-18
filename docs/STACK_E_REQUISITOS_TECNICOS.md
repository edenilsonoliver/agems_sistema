# AGEMS Next — Stack e Requisitos Técnicos

**Status:** Normativo  
**Público:** agentes de desenvolvimento, desenvolvedores, revisores, QA e DevOps  
**Escopo:** reconstrução do AGEMS a partir do zero  
**Última revisão:** 2026-09-18

Este documento define a arquitetura, a stack, os requisitos técnicos e os critérios mínimos de qualidade do novo AGEMS. Todo agente deve lê-lo antes de propor ou implementar mudanças.

As palavras **DEVE**, **NÃO DEVE**, **OBRIGATÓRIO**, **RECOMENDADO** e **OPCIONAL** expressam o nível de exigência. Mudanças nas decisões marcadas como obrigatórias exigem um ADR aprovado em docs/adr.

---

## 1. Objetivos da reconstrução

O novo sistema deve:

1. preservar as capacidades regulatórias relevantes do sistema atual;
2. reduzir acoplamento, duplicação e lógica espalhada entre views, templates, sinais e modelos;
3. tornar autorização, auditoria, importações, notificações e integrações previsíveis e testáveis;
4. usar o mesmo mecanismo de banco de dados no desenvolvimento, teste e produção;
5. suportar evolução incremental sem introduzir microserviços prematuramente;
6. oferecer experiência responsiva, acessível e adequada a usuários administrativos;
7. possuir API versionada para integrações;
8. operar com segurança, observabilidade, backup e recuperação documentados;
9. permitir que agentes trabalhem com regras claras e verificações automatizadas.

## 2. Decisões arquiteturais

### 2.1 Estilo principal

O sistema será um **monólito modular Django**.

Cada módulo de domínio terá modelos, serviços, consultas, formulários/serializers, views, URLs e testes próprios. Módulos podem conversar por interfaces públicas explícitas, nunca por importações circulares ou acesso informal a detalhes internos.

Microserviços, filas adicionais, bancos alternativos ou um frontend SPA completo só podem ser introduzidos por ADR contendo problema, alternativas, custos operacionais, estratégia de migração e aprovação.

### 2.2 Renderização e interação

A interface principal será renderizada no servidor com Django Templates. Interações parciais usarão HTMX e pequenos controladores Alpine.js ou JavaScript modular.

React, Vue, Angular, Next.js ou outro framework SPA não fazem parte da stack padrão. Uma exceção exige caso de uso comprovado e ADR.

### 2.3 Banco único

PostgreSQL com PostGIS será usado em desenvolvimento, testes, homologação e produção. SQLite não deve ser usado como banco padrão, pois diferenças de tipos, concorrência, constraints e SQL mascaram falhas.

### 2.4 Serviços de domínio

Fluxos com regras de negócio devem ser implementados em serviços de aplicação. Views, endpoints, comandos e tarefas assíncronas apenas validam a entrada, verificam autorização, chamam o serviço e formatam a resposta.

Consultas complexas ou reutilizadas devem ficar em selectors/query services. Regras invariantes também devem possuir constraints no banco quando tecnicamente possível.

---

## 3. Stack aprovada

Versões exatas de patch devem ser registradas em arquivos de lock. A tabela define a linha principal suportada.

| Camada | Tecnologia | Linha aprovada | Responsabilidade |
|---|---|---:|---|
| Linguagem | Python | 3.13 | Backend, regras de domínio, tarefas, importações e testes |
| Framework | Django | 5.2 LTS | Aplicação web, ORM, autenticação, templates e administração |
| API | Django REST Framework | 3.16.x | APIs versionadas e integrações |
| OpenAPI | drf-spectacular | versão compatível bloqueada | Esquema, documentação e contrato da API |
| Banco | PostgreSQL | 17.x | Persistência transacional principal |
| Geoespacial | PostGIS + GeoDjango | compatível com PostgreSQL 17 | Pontos, linhas, polígonos, KML e consultas espaciais |
| Driver | psycopg | 3.x | Conexão Django/PostgreSQL |
| Tarefas | Celery | 5.x | Notificações, importações, relatórios e processamentos demorados |
| Broker/cache | Redis Open Source | 8.2 Extended | Broker Celery, cache e locks distribuídos limitados |
| Agendamento | django-celery-beat | compatível | Agenda persistida de tarefas periódicas |
| Templates | Django Templates | Django 5.2 | HTML renderizado no servidor |
| CSS | Bootstrap | 5.3.x | Grid, componentes, acessibilidade e responsividade |
| Interação | HTMX | 2.x | Atualizações parciais sem SPA |
| Interação local | Alpine.js | 3.x | Estado local pequeno e comportamento de componentes |
| Build frontend | Vite | versão estável bloqueada | Empacotamento, hashes e otimização dos assets |
| Runtime frontend | Node.js | 24 LTS | Apenas ferramentas de build e testes frontend |
| Gráficos | Chart.js | 4.x | Dashboards e indicadores |
| Mapas | Leaflet | 1.9.x | Visualização cartográfica |
| Calendário | FullCalendar | 6.x | Agenda de ações e prazos |
| Drag and drop | SortableJS | 1.x | Kanban e reordenação |
| Servidor app | Gunicorn | versão estável bloqueada | Execução WSGI em produção |
| Proxy | Nginx | versão estável suportada | TLS, proxy, compressão e entrega de assets |
| Arquivos | S3 compatível | API S3 | Documentos e evidências; MinIO no ambiente local |
| Containers | Docker + Compose | versões suportadas | Ambientes reproduzíveis |
| Dependências Python | uv | versão bloqueada na automação | Lock, instalação e execução |
| Lint/format | Ruff | versão bloqueada | Formatação e lint Python |
| Tipagem | mypy + django-stubs | versões compatíveis | Verificação estática nas áreas tipadas |
| Testes backend | pytest + pytest-django | versões bloqueadas | Testes unitários e de integração |
| Testes navegador | Playwright | versão bloqueada | Fluxos críticos ponta a ponta |
| Cobertura | coverage.py/pytest-cov | versão bloqueada | Medição de cobertura |
| Segurança | pip-audit, Bandit, Gitleaks e Trivy | versões bloqueadas na CI | Dependências, código, segredos e imagens |
| Observabilidade | OpenTelemetry | versões compatíveis | Logs correlacionados, métricas e traces |

Django 5.2 foi escolhido por ser LTS e suportar Python 3.13. PostgreSQL 17 foi escolhido por maturidade e suporte upstream até novembro de 2029. Redis 8.2 foi escolhido por ser uma linha Extended.

### 3.1 Tecnologias não aprovadas por padrão

Não adicionar sem necessidade comprovada e ADR:

- Flask ou outro wrapper ao redor do Django;
- SQLite como ambiente oficial;
- múltiplos frameworks frontend;
- jQuery;
- acesso direto a CDN em produção;
- Elasticsearch/OpenSearch antes de esgotar busca e índices do PostgreSQL;
- microserviços;
- filas diferentes de Celery/Redis;
- lógica de negócio em stored procedures;
- dependências declaradas sem uso no código ou na infraestrutura.

---

## 4. Escopo funcional mínimo

A reconstrução deve cobrir os seguintes contextos de domínio.

### 4.1 Identidade e organização

- usuários ativos e inativos;
- diretorias e subunidades;
- autenticação;
- recuperação e alteração de credenciais;
- perfis e permissões;
- escopo de acesso por diretoria/subunidade;
- trilha de acessos e alterações relevantes;
- preparação para integração OIDC, caso exista provedor corporativo.

### 4.2 Entidades reguladas

- cadastro e situação cadastral;
- classificação e serviços associados;
- contatos e identificadores;
- histórico de alterações;
- validação de documentos nacionais sem persistir valores inválidos.

### 4.3 Instrumentos jurídicos

- contratos, convênios, acordos, aditivos e tipos configuráveis;
- entidades relacionadas;
- vigência, status e responsáveis;
- documentos e versões;
- histórico e auditoria;
- filtros por estrutura organizacional.

### 4.4 Obrigações

- vínculo obrigatório com instrumento;
- cláusula, descrição, prazo, recorrência, criticidade e responsável;
- percentual de atendimento;
- regras explícitas de mudança de status;
- histórico de avaliações;
- importação validada com prévia e relatório de erros.

### 4.5 Ações e fiscalização

- vínculo com obrigação;
- responsável e executores;
- prioridade, status, progresso e datas;
- predecessoras e bloqueios;
- checklists;
- comentários e histórico;
- visualização em lista, calendário e Kanban;
- fiscalização de campo;
- evidências fotográficas, documentos e localização;
- consistência transacional entre ação, evidência e marcador geográfico.

### 4.6 Indicadores

- definição, unidade, fórmula, periodicidade e metas;
- séries históricas;
- coleta manual e importação;
- validação e rastreabilidade da origem;
- painéis por instrumento, entidade e período.

### 4.7 Alertas e notificações

- alertas internos;
- notificações por e-mail;
- preferências por usuário;
- tarefas periódicas idempotentes;
- tentativas, falhas e reprocessamento;
- prevenção de notificações duplicadas.

### 4.8 Documentos e evidências

- armazenamento fora do container da aplicação;
- metadados, categoria, autor, data e vínculo de domínio;
- hash SHA-256;
- tamanho e MIME permitidos;
- varredura antimalware antes da disponibilização;
- nomes físicos não derivados diretamente do nome enviado;
- URLs assinadas ou acesso autenticado;
- versionamento quando o documento tiver valor regulatório.

### 4.9 Georreferenciamento

- armazenamento nativo PostGIS;
- suporte a Point, LineString, Polygon e coleções necessárias;
- importação KML com validação estrutural;
- normalização de SRID para 4326;
- registro de elementos rejeitados;
- camadas configuráveis;
- extração controlada de coordenadas EXIF;
- mapas Leaflet sem expor informações não autorizadas.

### 4.10 Dashboards e integrações

- indicadores consolidados respeitando o escopo de autorização;
- consultas agregadas eficientes;
- exportações assíncronas quando demoradas;
- API REST versionada;
- credenciais externas criptografadas e nunca exibidas novamente;
- timeouts, retentativas, circuit breaker quando aplicável e logs sem segredos.

---

## 5. Organização recomendada do repositório

    .
    ├── backend/
    │   ├── config/
    │   ├── apps/
    │   │   ├── common/
    │   │   ├── identity/
    │   │   ├── organizations/
    │   │   ├── entities/
    │   │   ├── instruments/
    │   │   ├── obligations/
    │   │   ├── actions/
    │   │   ├── inspections/
    │   │   ├── indicators/
    │   │   ├── notifications/
    │   │   ├── documents/
    │   │   ├── geo/
    │   │   ├── dashboards/
    │   │   └── integrations/
    │   ├── templates/
    │   └── static_src/
    ├── frontend/
    │   ├── js/
    │   ├── styles/
    │   └── tests/
    ├── tests/
    │   ├── factories/
    │   ├── integration/
    │   └── e2e/
    ├── docs/
    │   ├── adr/
    │   ├── api/
    │   └── runbooks/
    ├── infra/
    │   ├── docker/
    │   └── nginx/
    ├── compose.yaml
    ├── pyproject.toml
    ├── uv.lock
    ├── package.json
    └── README.md

Cada app de domínio deve, quando aplicável, conter:

    app/
    ├── models/
    ├── services/
    ├── selectors/
    ├── api/
    ├── forms/
    ├── views/
    ├── urls.py
    ├── admin.py
    └── tests/

A estrutura pode ser simplificada para módulos pequenos, mas as responsabilidades não devem ser misturadas.

---

## 6. Regras obrigatórias de implementação

### 6.1 Domínio e persistência

- Views e serializers devem ser finos.
- Operações que alteram mais de um agregado devem usar transação explícita.
- Efeitos posteriores ao commit devem usar transaction.on_commit.
- Signals não devem esconder fluxos principais de negócio.
- Toda migration deve ser revisável, determinística e segura para o volume esperado.
- Campos obrigatórios devem possuir constraints de banco.
- Unicidade deve ser protegida por UniqueConstraint, não apenas por validação da interface.
- Status devem usar enums explícitos e transições testadas.
- Valores monetários e percentuais usam Decimal, nunca float.
- Datas de negócio usam date; instantes usam datetime com timezone.
- Instantes são armazenados em UTC e apresentados em America/Campo_Grande.
- Exclusão lógica só deve ser usada quando exigida por auditoria ou regra de negócio.
- Consultas de lista devem evitar N+1 por select_related/prefetch_related.
- Índices devem acompanhar filtros e ordenações frequentes.

### 6.2 Autorização

- Autenticação não substitui autorização.
- Todo acesso deve validar ação, objeto e escopo organizacional.
- O escopo por diretoria/subunidade deve ser aplicado no servidor.
- IDs recebidos do cliente nunca constituem prova de acesso.
- Downloads também devem validar permissão.
- Endpoints HTMX, JSON e tarefas Celery seguem as mesmas regras das views completas.
- O comportamento deve ser deny by default.
- Mudanças de perfil e permissões devem ser auditadas.

### 6.3 API

- Prefixo obrigatório: /api/v1/.
- OpenAPI deve ser gerado e validado na CI.
- Serializers validam formato; serviços validam regra de negócio.
- Erros devem possuir código estável, mensagem legível e detalhes de campo quando aplicável.
- Listagens devem ser paginadas.
- Filtros devem ser documentados e limitados.
- Operações potencialmente repetidas devem possuir idempotência.
- APIs não devem retornar stack trace, segredo ou dado fora do escopo.
- Alterações incompatíveis exigem nova versão ou período formal de depreciação.

### 6.4 Frontend

- Componentes Bootstrap devem ser reutilizados antes de criar equivalentes.
- Não inserir bibliotecas por CDN em produção.
- JavaScript novo deve usar módulos e passar por lint/testes.
- HTMX deve receber fragmentos próprios, não páginas completas.
- Alpine.js fica restrito a estado local de componentes.
- Textos visíveis devem estar preparados para tradução.
- Formulários devem exibir erros próximos aos campos e resumo acessível.
- A navegação deve funcionar por teclado.
- Contraste e componentes devem atender WCAG 2.2 AA.
- Não depender exclusivamente de cor para transmitir estado.
- Dashboards devem possuir alternativa textual ou tabular aos gráficos.

### 6.5 Arquivos

- Uploads devem ter limite de tamanho configurável.
- Validar extensão, MIME detectado e conteúdo esperado.
- Rejeitar path traversal, arquivos executáveis e formatos não autorizados.
- Imagens devem ser reprocessadas quando necessário, sem confiar nos metadados originais.
- KML/XML deve usar parser protegido contra entidades externas e ataques de expansão.
- Arquivos suspeitos permanecem em quarentena.

### 6.6 Dependências

- Toda dependência deve ter propósito documentado.
- Dependência sem uso deve ser removida.
- Versões devem ser bloqueadas em uv.lock ou lockfile npm.
- Atualizações automáticas devem executar testes e scans.
- Não adicionar pacote apenas para substituir poucas linhas simples e seguras.
- Licença deve ser compatível com o projeto.

---

## 7. Segurança

O baseline mínimo inclui:

- HTTPS obrigatório fora do ambiente local;
- cookies Secure, HttpOnly e SameSite adequados;
- CSRF habilitado para sessão e HTMX;
- Content-Security-Policy progressiva;
- HSTS após confirmação do domínio e TLS;
- X-Content-Type-Options, Referrer-Policy e frame-ancestors;
- segredos somente por variáveis ou secret manager;
- nenhuma credencial em repositório, imagem, log ou fixture;
- rotação de segredos e chaves documentada;
- rate limiting em autenticação, recuperação de senha e endpoints caros;
- proteção contra enumeração de usuários;
- logs sem senhas, tokens, cookies, documentos ou dados pessoais desnecessários;
- criptografia de credenciais de integração em repouso;
- backup criptografado;
- princípio do menor privilégio no banco, storage e containers;
- containers executados como usuário não root;
- imagens mínimas e atualizadas;
- scans de dependências, segredos, código e imagem em toda pull request;
- threat model atualizado para autenticação, autorização, uploads, integrações e geodados.

Requisitos da LGPD devem ser detalhados com o responsável de negócio: finalidade, base legal, retenção, acesso, exportação, correção, anonimização e descarte.

---

## 8. Auditoria

Eventos auditáveis devem registrar:

- quem executou;
- quando;
- origem da requisição;
- ação;
- tipo e identificador do objeto;
- resultado;
- campos alterados em formato seguro;
- justificativa quando exigida.

A auditoria não deve armazenar senhas, tokens, conteúdo integral de documentos ou outros segredos. Registros de auditoria não devem ser editáveis pela interface comum.

A criação de logs não substitui histórico de domínio. Mudanças regulatórias relevantes devem possuir modelo de histórico próprio ou versão imutável.

---

## 9. Tarefas assíncronas

Devem ser assíncronos quando ultrapassarem o tempo confortável da requisição:

- envio de notificações;
- importações volumosas;
- geração de relatórios;
- processamento de fotos;
- antivírus;
- sincronizações externas;
- recomputações extensas.

Toda tarefa deve:

- ser idempotente;
- ter timeout;
- definir política de retry;
- registrar correlação e resultado;
- não receber objetos Python serializados; usar IDs e dados JSON mínimos;
- revalidar autorização/contexto quando apropriado;
- possuir tratamento de dead letter ou rotina operacional equivalente;
- ter teste unitário e, para fluxos críticos, teste de integração com broker.

---

## 10. Testes e qualidade

### 10.1 Pirâmide mínima

- testes unitários para regras e transições;
- testes de integração para ORM, serviços, autorização, storage, tarefas e API;
- testes de contrato para OpenAPI e integrações externas;
- testes E2E para fluxos críticos;
- testes de importação com arquivos válidos, inválidos e maliciosos;
- testes de concorrência para operações sensíveis;
- testes de restauração de backup em rotina agendada.

### 10.2 Fluxos E2E obrigatórios

1. autenticação e encerramento de sessão;
2. criação de entidade;
3. criação de instrumento e obrigação;
4. criação, atribuição e conclusão de ação;
5. bloqueio de acesso entre unidades;
6. upload e download autorizado de evidência;
7. importação KML;
8. visualização de mapa;
9. alerta de prazo sem duplicação;
10. dashboard respeitando o escopo do usuário.

### 10.3 Portões de qualidade

Toda pull request deve passar por:

- formatação e lint;
- checagem de tipos definida para o escopo;
- django check;
- validação de migrations pendentes;
- testes unitários e de integração;
- cobertura;
- build frontend;
- validação OpenAPI;
- scan de segredos;
- scan de dependências;
- scan de imagem quando houver mudança no container.

Cobertura global inicial mínima: **80%**. Serviços de domínio, autorização e transições críticas: **90%**. Cobertura não substitui qualidade dos cenários.

---

## 11. Desempenho, disponibilidade e capacidade

Metas iniciais, a revisar com dados reais:

- respostas HTML/API comuns: p95 menor que 500 ms no ambiente de referência;
- dashboard principal: p95 menor que 2 s;
- primeira renderização útil em rede corporativa: menor que 2,5 s;
- listagens sempre paginadas, padrão 25 e máximo 100 itens;
- consultas síncronas devem possuir timeout;
- exportações/importações demoradas executadas em background;
- health checks separados para liveness e readiness;
- aplicação stateless, exceto banco, Redis e storage externo;
- deploy com migrações compatíveis com rollback da aplicação sempre que possível.

Toda otimização deve ser guiada por medição. Cache não pode ser usado para ocultar consulta incorreta ou autorização cara.

---

## 12. Backup e recuperação

Baseline inicial:

- backup diário completo;
- recuperação ponto no tempo do PostgreSQL quando a infraestrutura permitir;
- retenção diária, semanal e mensal definida pelo responsável de dados;
- cópia fora do host principal;
- backup do storage de documentos;
- criptografia em trânsito e repouso;
- restauração testada e registrada;
- RPO alvo de até 24 horas;
- RTO alvo de até 4 horas.

RPO e RTO finais precisam de aprovação do negócio e infraestrutura.

---

## 13. Observabilidade

A aplicação deve produzir logs estruturados JSON em produção contendo:

- timestamp;
- nível;
- serviço;
- ambiente;
- request/correlation ID;
- usuário apenas por identificador interno quando necessário;
- rota ou tarefa;
- duração;
- status;
- erro normalizado.

Métricas mínimas:

- latência, throughput e erros HTTP;
- conexões e consultas lentas do banco;
- tamanho e atraso das filas;
- sucesso e falha de tarefas;
- importações processadas/rejeitadas;
- uso do storage;
- autenticações falhas;
- notificações enviadas/falhas.

Erros devem ser correlacionáveis entre Nginx, Django e Celery. Alertas precisam apontar para runbooks em docs/runbooks.

---

## 14. Ambientes

### Desenvolvimento

Compose deve iniciar no mínimo:

- web;
- PostgreSQL/PostGIS;
- Redis;
- worker Celery;
- beat quando necessário;
- MinIO;
- serviço de e-mail local;
- antivírus quando o fluxo de arquivos for implementado.

Dados de desenvolvimento devem ser sintéticos. Nenhum dump de produção pode ser usado sem anonimização formal.

### Teste

A suíte usa PostgreSQL/PostGIS real. Serviços externos devem ser substituídos por fakes controlados, exceto nos testes de integração dedicados.

### Homologação

Deve ser equivalente à produção em topologia e configurações de segurança, com dados próprios.

### Produção

DEBUG desabilitado, TLS ativo, secrets externos, usuário não root, volumes e backups monitorados, logs centralizados e endpoints administrativos restritos.

---

## 15. CI/CD e fluxo Git

- branches de curta duração;
- pull request obrigatória;
- pelo menos uma revisão humana para mudanças de domínio, segurança ou dados;
- commits e títulos descritivos;
- migrations acompanhadas do código que as usa;
- deploy automatizado e reproduzível;
- promoção do mesmo artefato entre ambientes;
- rollback documentado;
- mudanças de banco com estratégia expand/migrate/contract quando houver risco;
- tags e changelog por versão.

Não fazer deploy direto a partir da árvore de trabalho de um desenvolvedor.

---

## 16. Definition of Done

Uma entrega só está concluída quando:

- requisito e critérios de aceite estão claros;
- autorização foi analisada;
- implementação respeita os limites de módulo;
- migrations foram revisadas;
- testes relevantes foram adicionados;
- portões da CI passaram;
- interface foi verificada em teclado e viewport móvel;
- logs e métricas necessários existem;
- documentação e OpenAPI foram atualizadas;
- não há segredo, TODO crítico ou dependência sem uso;
- impacto em backup, dados e rollback foi considerado;
- o revisor consegue reproduzir a mudança.

---

## 17. Instruções específicas para agentes

Antes de modificar código, o agente deve:

1. identificar o módulo proprietário da regra;
2. ler este documento, o README do módulo e ADRs relacionados;
3. inspecionar modelos, serviços, constraints, autorização e testes existentes;
4. declarar suposições quando o requisito não estiver explícito;
5. preservar alterações não relacionadas;
6. implementar a menor mudança coerente com a arquitetura;
7. executar verificações proporcionais ao risco;
8. relatar arquivos alterados, testes executados e riscos restantes.

O agente não deve:

- inventar permissão ou regra regulatória;
- contornar testes para obter resultado verde;
- remover constraint ou validação sem justificar;
- colocar regra de domínio em template;
- acessar model de outro módulo de forma circular;
- criar segunda implementação para uma capacidade já existente;
- introduzir dependência, serviço ou padrão arquitetural sem explicar a necessidade;
- marcar trabalho como concluído sem verificação;
- editar dados de produção;
- registrar ou exibir segredo.

Quando houver ambiguidade que altere comportamento regulatório, autorização, retenção de dados ou cálculo de indicador, o agente deve parar e solicitar decisão humana.

---

## 18. Decisões ainda pendentes

Devem ser resolvidas antes da respectiva implementação:

1. provedor de identidade e necessidade de OIDC/SSO;
2. matriz final de perfis, ações e escopos;
3. classificação dos dados pessoais e prazos de retenção;
4. storage S3 de produção;
5. serviço de e-mail;
6. domínio, TLS e rede de publicação;
7. volume esperado de usuários, instrumentos, ações, evidências e KML;
8. RPO/RTO definitivos;
9. necessidade de assinatura digital ou integração com processo eletrônico;
10. sistemas externos e contratos de integração;
11. política oficial de versionamento documental;
12. identidade visual definitiva.

Até a decisão, agentes devem criar interfaces adaptáveis e não assumir fornecedores.

---

## 19. Referências técnicas

- Django 5.2 LTS: https://docs.djangoproject.com/en/5.2/releases/5.2/
- Compatibilidade Python/Django: https://docs.djangoproject.com/en/5.2/faq/install/
- Política de versões PostgreSQL: https://www.postgresql.org/support/versioning/
- Gestão de versões Redis: https://redis.io/docs/latest/operate/oss_and_stack/install/version-mgmt/
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- OpenTelemetry: https://opentelemetry.io/docs/

Este documento deve evoluir por revisão explícita. Decisões específicas devem ser registradas como ADRs, sem transformar o documento em histórico de implementação.
