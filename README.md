# Skill `refactor-arch` — Refatoração Arquitetural Automatizada

Entrega do desafio de Skills do MBA da Full Cycle: uma skill do Claude Code que analisa, audita e refatora um projeto para o padrão MVC, aplicada a três projetos legados.

O enunciado completo está em [desafio.md](desafio.md).

## Etapas da entrega

| # | Etapa | O que é entregue | Status |
|---|---|---|---|
| 0 | Linha de base | Respostas de todos os endpoints dos 3 projetos, gravadas antes de qualquer mudança | Concluída |
| 1 | Análise manual | Problemas de cada projeto, documentados na seção "Análise Manual" | Concluída |
| 2 | Criação da skill | `SKILL.md` e arquivos de referência em `code-smells-project/.claude/skills/refactor-arch/` | Concluída |
| 3 | Execução no projeto 1 | `code-smells-project` refatorado e `reports/audit-project-1.md` | Concluída |
| 4 | Execução no projeto 2 | `ecommerce-api-legacy` refatorado e `reports/audit-project-2.md` | Pendente |
| 5 | Execução no projeto 3 | `task-manager-api` refatorado e `reports/audit-project-3.md` | Pendente |
| 6 | Documentação final | As quatro seções deste README preenchidas, no repositório público | Pendente |

### Etapa 0 — Linha de base

- [x] Os 3 projetos sobem sem erro no estado original
- [x] Respostas de todos os endpoints gravadas em [baseline/](baseline/) (40, 11 e 40 requisições)
- [x] Segunda execução com banco zerado produz saída idêntica

### Etapa 1 — Análise manual

Para cada um dos 3 projetos:

- [x] No mínimo 5 problemas documentados (14, 15 e 17)
- [x] Pelo menos 1 de severidade CRITICAL ou HIGH
- [x] Pelo menos 2 de severidade MEDIUM
- [x] Pelo menos 2 de severidade LOW
- [x] Cada problema com arquivo, linha e justificativa de por que é relevante

### Etapa 2 — Criação da skill

- [x] `SKILL.md` com 3 fases sequenciais: Análise, Auditoria e Refatoração
- [x] Referência de análise de projeto: heurísticas para linguagem, framework, banco de dados e arquitetura
- [x] Catálogo com no mínimo 8 anti-patterns, com sinais de detecção e severidade distribuída entre CRITICAL, HIGH, MEDIUM e LOW (22: 6, 5, 7 e 4)
- [x] Catálogo cobre APIs deprecated e recomenda o equivalente moderno
- [x] Template do relatório de auditoria
- [x] Guidelines do MVC alvo: responsabilidades de Models, Views/Routes e Controllers
- [x] Playbook com no mínimo 8 transformações, com código antes e depois (16)
- [x] A Fase 2 pausa e pede confirmação antes de modificar qualquer arquivo (verificado no ensaio)
- [x] A Fase 3 valida o resultado: boot da aplicação e endpoints respondendo (definido na skill; será exercitado na etapa 3)
- [x] A skill é agnóstica de tecnologia: nada nela depende de um projeto específico

### Etapas 3, 4 e 5 — Execução nos projetos

Para cada projeto (nos projetos 2 e 3, depois de copiar a pasta da skill para dentro dele):

- [ ] Fase 1 detecta linguagem, framework e domínio corretamente
- [ ] Fase 2 encontra no mínimo 5 findings, com pelo menos 1 CRITICAL ou HIGH
- [ ] Fase 2 pausa e pede confirmação
- [ ] Relatório da Fase 2 salvo em `reports/audit-project-<n>.md`
- [ ] Fase 3 cria a estrutura MVC, com config extraída e error handling centralizado
- [ ] Aplicação inicia sem erros e os endpoints originais respondem
- [ ] Checklist de validação do [enunciado](desafio.md#validação) preenchido
- [ ] Código refatorado commitado

No projeto 1, a Fase 2 também precisa encontrar pelo menos 5 dos problemas da análise manual.

### Etapa 6 — Documentação final

- [ ] Seção "Análise Manual" preenchida
- [ ] Seção "Construção da Skill" preenchida
- [ ] Seção "Resultados" preenchida
- [ ] Seção "Como Executar" preenchida
- [ ] A mesma versão da skill está nos 3 projetos
- [ ] Tudo publicado no fork público

### Critérios de aceite

Todos valem para os 3 projetos:

| Critério | Requisito |
|---|---|
| Fase 1 detecta a stack corretamente | Obrigatório (3/3) |
| Fase 2 encontra 5 ou mais findings | Obrigatório (3/3) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | Obrigatório (3/3) |
| Aplicação funciona após a Fase 3 | Obrigatório (3/3) |

## Análise Manual

Os três projetos foram lidos por inteiro e executados antes de qualquer mudança. Os arquivos e linhas abaixo se referem ao código original (commit `6d1ce62`). Onde a tabela diz "confirmado", o problema foi reproduzido na aplicação rodando, e não só lido no código.

A severidade segue a escala do [enunciado](desafio.md#definição-de-severidades).

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| code-smells-project | 4 | 2 | 5 | 3 | 14 |
| ecommerce-api-legacy | 4 | 3 | 5 | 3 | 15 |
| task-manager-api | 5 | 2 | 6 | 4 | 17 |

### Projeto 1 — code-smells-project (Python/Flask)

API de e-commerce em 4 arquivos. Os nomes `controllers.py` e `models.py` sugerem camadas, mas cada um é um arquivo único para todos os domínios, e as responsabilidades estão misturadas.

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | SQL injection por concatenação de strings | `models.py`, em toda query com parâmetro (ex.: `28`, `47-50`, `109-111`, `289-299`) | Qualquer campo de entrada altera o SQL. Confirmado: login com email `admin@loja.com' --` autentica como admin sem senha. |
| 2 | CRITICAL | Rotas administrativas sem autenticação | `app.py:47-57` (reset do banco), `app.py:59-78` (SQL arbitrário) | Uma única requisição anônima lê, altera ou apaga o banco inteiro. |
| 3 | CRITICAL | Segredos hardcoded e expostos | `app.py:7` (`SECRET_KEY`), `controllers.py:289` (`/health` devolve a chave), `app.py:8, 88` (debug ligado em `0.0.0.0`) | A chave está no repositório e também é entregue a qualquer cliente que chame `/health`. |
| 4 | CRITICAL | Senhas em texto puro, devolvidas pela API | `database.py:75-79`, `models.py:83, 99, 109-111, 126-129` | `GET /usuarios` lista a senha de todos os usuários; um vazamento do banco expõe todas as contas. |
| 5 | HIGH | Regra de negócio na camada de dados | `models.py:133-169` (valida estoque, calcula total e baixa estoque), `models.py:256-262` (faixas de desconto) | Não dá para testar a regra sem banco, nem trocar a persistência sem reescrever a regra. |
| 6 | HIGH | Estado global mutável: uma conexão para toda a aplicação | `database.py:4-10`; schema e seed dentro de `get_db` (`database.py:14-84`) | Todas as requisições compartilham a mesma conexão e a mesma transação, com `check_same_thread=False`. |
| 7 | MEDIUM | Queries N+1 na listagem de pedidos | `models.py:171-201`, `models.py:203-233` | Uma query por pedido e outra por item; o custo cresce com o volume de pedidos. |
| 8 | MEDIUM | Validação ausente | `models.py:144-166`, `controllers.py:43, 169-170, 195-203`, `database.py:30` (email sem `UNIQUE`) | Confirmado: pedido com quantidade `-5` gera total negativo e aumenta o estoque; usuário inexistente cria pedido; email duplicado é aceito; preço como texto devolve 500. |
| 9 | MEDIUM | Pedido gravado sem transação nem rollback | `models.py:148-168` | Se uma escrita falhar no meio, as anteriores ficam pendentes na conexão global e são gravadas pelo próximo `commit`. |
| 10 | MEDIUM | Tratamento de erro repetido e vazando detalhes internos | `controllers.py`, `try/except Exception` nas 16 funções (ex.: `10-12`, `60-62`) | Não há handler central, e a mensagem interna vai para o cliente. Confirmado: uma busca com aspas devolve o erro de sintaxe do SQLite. |
| 11 | MEDIUM | Código duplicado | `models.py:12-21, 31-40, 304-313` (linha para dicionário), `models.py:171-201` e `203-233`, `controllers.py:28-46` e `72-90` | Cada correção precisa ser repetida em vários lugares, e as cópias já divergem (a atualização de produto não valida nome nem categoria). |
| 12 | LOW | `print` como log e notificações simuladas | `controllers.py:8, 57, 208-210, 248-250`, `app.py:56, 83-86` | Sem níveis nem destino configurável; email, SMS e push são apenas `print` dentro do controller. |
| 13 | LOW | Magic numbers e listas soltas | `models.py:257-262` (faixas de desconto), `controllers.py:47-52, 242` (limites, categorias, status) | As regras ficam escondidas em literais, sem nome e sem um lugar único para alterar. |
| 14 | LOW | Nomes que sombreiam built-ins e import sem uso | `id` como parâmetro (`controllers.py:14, 64, 98, 136`, `models.py:24, 54, 65, 89`), `import sqlite3` (`models.py:2`) | Ruído de leitura e risco de erro sutil ao usar `id()` dentro dessas funções. |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

API de LMS com checkout em 3 arquivos. Praticamente tudo está na classe `AppManager`.

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | God Class `AppManager` | `AppManager.js:4-139` | Conexão, schema, seed, rotas, checkout, pagamento e relatório na mesma classe; nada pode ser testado ou alterado em isolamento. |
| 2 | CRITICAL | Credenciais hardcoded | `utils.js:1-7` | Senha do banco e chave `pk_live` do gateway de pagamento versionadas no código. |
| 3 | CRITICAL | Dados sensíveis no log | `AppManager.js:45` | Confirmado no log do servidor: o número completo do cartão e a chave do gateway são impressos a cada checkout. |
| 4 | CRITICAL | "Hash" de senha caseiro | `utils.js:17-23`, `AppManager.js:68` (senha padrão `123456`), `AppManager.js:18` (seed em texto puro) | Confirmado: o resultado depende só do início da senha; `senhaforte` e `se` geram o mesmo valor (`c2c2c2c2c2`). |
| 5 | HIGH | Rotas administrativa e destrutiva sem autenticação | `AppManager.js:80`, `AppManager.js:131` | Qualquer cliente lê o relatório financeiro e apaga usuários. |
| 6 | HIGH | Estado global mutável | `utils.js:9-15, 25` | O cache global cresce sem limite e nunca é lido; `totalRevenue` é exportado e nunca atualizado. |
| 7 | HIGH | Acoplamento forte, sem injeção de dependência | `AppManager.js:7`, `app.js:8-10` | O banco é criado dentro do construtor e as rotas dependem de `this.db`; não há como substituir a persistência em um teste. |
| 8 | MEDIUM | Queries N+1 no relatório financeiro | `AppManager.js:83-126` | Uma query por curso e duas por matrícula, com contadores manuais de callbacks pendentes. Confirmado: a ordem da resposta muda entre execuções. |
| 9 | MEDIUM | Callback hell | `AppManager.js:37-76` | Cinco callbacks aninhados no checkout; o fluxo e o tratamento de erro ficam difíceis de seguir. |
| 10 | MEDIUM | Erros de banco ignorados | `AppManager.js:57, 92, 104, 106, 133` | Uma falha de query derruba a requisição ou a deixa sem resposta. Confirmado: apagar um usuário inexistente devolve 200. |
| 11 | MEDIUM | Checkout sem transação e exclusão sem integridade | `AppManager.js:50-61` (3 inserts independentes), `AppManager.js:12-16` (sem chaves estrangeiras), `AppManager.js:131-137` | Uma falha parcial deixa matrícula sem pagamento. Confirmado: após apagar um usuário, o relatório mostra o aluno como `Unknown`. |
| 12 | MEDIUM | Validação fraca e respostas inconsistentes | `AppManager.js:35` (só verifica presença), respostas em texto puro (`35, 38, 48, 135`) e em JSON (`60`) | Email e cartão não têm formato validado, e o cliente precisa tratar dois formatos de resposta. |
| 13 | LOW | Nomes ruins | `AppManager.js:29-33` (`u`, `e`, `p`, `cid`, `cc`) e os campos `usr`, `eml`, `pwd`, `c_id` da API | É preciso ler o fluxo inteiro para saber o que cada variável guarda. |
| 14 | LOW | Magic strings e numbers | `AppManager.js:46` (`"4"`, `PAID`, `DENIED`), `utils.js:19, 22` (`10000`, `10`), `utils.js:6` (porta) | A regra de aprovação do pagamento e os status ficam em literais espalhados. |
| 15 | LOW | Código morto e `console.log` como log | `AppManager.js:2` (`totalRevenue` importado sem uso), `utils.js:9` (cache nunca lido), `utils.js:13`, `app.js:13` | Código que parece ter função e não tem; logs sem nível nem destino configurável. |

### Projeto 3 — task-manager-api (Python/Flask)

API de tarefas que já tem `models/`, `routes/`, `services/` e `utils/`. A estrutura existe, mas as rotas concentram toda a lógica e as outras camadas são, em boa parte, ignoradas.

| # | Severidade | Problema | Onde | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | Senhas com MD5 sem salt | `models/user.py:29, 32` | MD5 é quebrado por tabelas prontas; senhas iguais geram hashes iguais. |
| 2 | CRITICAL | Hash da senha devolvido pela API | `models/user.py:21`, usado em `routes/user_routes.py:33, 85, 129, 209` | Confirmado: `GET /users/1`, a criação, a edição e o login devolvem o hash. |
| 3 | CRITICAL | Segredos hardcoded | `app.py:13` (`SECRET_KEY`), `services/notification_service.py:7-10` (usuário e senha SMTP) | Credenciais versionadas no código, sem configuração por ambiente. |
| 4 | CRITICAL | Autenticação inexistente e escalada de privilégio | `routes/user_routes.py:210` (token falso), `routes/user_routes.py:52, 71-72` (`role` vem do corpo) | Nenhuma rota exige token. Confirmado: uma requisição anônima cria um usuário `admin`. |
| 5 | CRITICAL | Debugger interativo exposto | `app.py:34` (`debug=True` em `0.0.0.0`) | Confirmado: um erro não tratado devolve a página do debugger do Werkzeug, com stack trace e código-fonte. |
| 6 | HIGH | Regra de negócio dentro das rotas | `routes/task_routes.py:11-63, 85-154, 156-223`, `routes/report_routes.py:12-101`, `routes/user_routes.py:42-90` | Cada rota valida, consulta, calcula e serializa; não existe camada de controller ou service para testar ou reusar. |
| 7 | HIGH | Responsabilidades fora do lugar e camadas ignoradas | CRUD de categorias em `routes/report_routes.py:157-223`; sem uso: `Task.is_overdue` (`models/task.py:50-60`), `process_task_data` (`utils/helpers.py:57-106`), `NotificationService`, constantes de `utils/helpers.py:110-116` | A estrutura de pastas promete uma separação que o código não cumpre, e a lógica acabou reescrita dentro das rotas. |
| 8 | MEDIUM | Queries N+1 | `routes/task_routes.py:41-57`, `routes/report_routes.py:55-56, 161-163`, `routes/user_routes.py:22` | Duas queries extras por tarefa na listagem e uma por usuário ou categoria nos relatórios. |
| 9 | MEDIUM | Agregações em memória e contagens repetidas | `routes/report_routes.py:19-43`, `routes/task_routes.py:275-287` | Nove `COUNT` separados e todas as tarefas carregadas só para contar as atrasadas. |
| 10 | MEDIUM | Código duplicado | Cálculo de atraso em 6 lugares (`task_routes.py:30-39, 71-80, 284-287`, `user_routes.py:171-180`, `report_routes.py:34-36, 132-135`); regex de email (`user_routes.py:61, 106`, `helpers.py:21`); lista de status (`task_routes.py:110, 177`, `task.py:39`, `helpers.py:75, 110`) | A mesma regra existe em várias cópias, embora já haja um método e constantes prontos para isso. |
| 11 | MEDIUM | `except:` genérico e sem handler central | `task_routes.py:62, 137, 204, 236`, `user_routes.py:130, 149`, `report_routes.py:186, 207, 221`, `helpers.py:46, 49, 88` | Qualquer erro, inclusive de programação, vira uma mensagem genérica, sem registro da causa. |
| 12 | MEDIUM | Validação de tipos ausente | `task_routes.py:96, 113, 261, 264`, `report_routes.py:196-197` | Confirmado: prioridade como texto, título numérico, `priority=abc` na busca e corpo `null` devolvem 500. |
| 13 | MEDIUM | APIs deprecated | `datetime.utcnow()`: 22 usos em 9 arquivos (ex.: `models/task.py:15-16`, `task_routes.py:31`, `report_routes.py:35`); `Model.query.get()`: 16 usos (ex.: `task_routes.py:42`, `user_routes.py:29`, `report_routes.py:105`) | `utcnow()` está deprecated desde o Python 3.12 (o aviso aparece ao rodar o seed); o moderno é `datetime.now(timezone.utc)`. `Query.get()` é legado desde o SQLAlchemy 2.0; o moderno é `db.session.get()`. |
| 14 | LOW | Imports sem uso | `app.py:7`, `task_routes.py:7`, `user_routes.py:6`, `report_routes.py:7-8`, `helpers.py:3-7`, `models/task.py:3` | Sugerem dependências que não existem. |
| 15 | LOW | Magic numbers | `task_routes.py:96-99, 113`, `user_routes.py:64, 115`, `report_routes.py:45, 129` | Limites de título, prioridade, senha e período ficam em literais, com as constantes de `helpers.py` sem uso. |
| 16 | LOW | `print` como log | `task_routes.py:149, 153, 219, 234`, `user_routes.py:83, 89, 147` | Sem níveis nem destino configurável. |
| 17 | LOW | Código verboso e nomes ruins | `models/user.py:34-38`, `models/task.py:38-48` (`if` que devolve `True`/`False`), `task_routes.py:141` (`type(tags) == list`), `report_routes.py:24-28` (`p1` a `p5`) | Mais linhas para ler sem ganho de clareza. |

### Padrões que a skill precisa detectar

Os mesmos problemas aparecem nas duas stacks, o que orienta o catálogo da skill:

- **Nos três projetos:** segredos hardcoded, senha mal protegida, rotas sem autenticação, validação ausente, N+1, erro tratado de forma local e repetida, `print`/`console.log` como log e magic numbers.
- **Injeção e exposição de dados:** SQL concatenado (projeto 1), dados sensíveis em resposta ou log (os três).
- **Violação de camadas:** God Class (projeto 2), regra de negócio no model (projeto 1) e na rota (projeto 3).
- **Estado e acoplamento:** conexão ou cache global mutável e ausência de injeção de dependência (projetos 1 e 2).
- **APIs deprecated:** só o projeto 3 tem ocorrências, então a detecção precisa ser condicional.
- **Projeto parcialmente organizado:** no projeto 3 a pasta certa existe e é ignorada; a skill precisa olhar o conteúdo dos arquivos, não só a estrutura de diretórios.

## Construção da Skill

### Estrutura

```
.claude/skills/refactor-arch/
├── SKILL.md                          roteiro das 3 fases
├── references/
│   ├── project-analysis.md           análise de projeto
│   ├── anti-patterns-catalog.md      catálogo de anti-patterns
│   ├── report-template.md            template de relatório
│   ├── mvc-guidelines.md             guidelines de arquitetura
│   └── refactoring-playbook.md       playbook de refatoração
└── scripts/
    └── http_smoke.py                 grava e compara respostas dos endpoints
```

| Área de conhecimento exigida | Arquivo | Conteúdo |
|---|---|---|
| Análise de projeto | `project-analysis.md` | Detecção de linguagem (8 stacks), framework, banco e tabelas; inventário de rotas; mapa de responsabilidades; 4 níveis de arquitetura; formato do resumo da Fase 1 |
| Catálogo de anti-patterns | `anti-patterns-catalog.md` | 22 anti-patterns com sinais de detecção, severidade e a transformação que resolve cada um; tabela de APIs deprecated |
| Template de relatório | `report-template.md` | Formato do relatório da Fase 2 e do resumo da Fase 3, com regras de preenchimento |
| Guidelines de arquitetura | `mvc-guidelines.md` | Camadas do MVC alvo, responsabilidade de cada uma, regra de dependência, contrato HTTP a preservar |
| Playbook de refatoração | `refactoring-playbook.md` | Ordem de execução, smoke test e 16 transformações com código antes e depois |

### Decisões de design

- **`SKILL.md` curto, conhecimento nas referências.** O `SKILL.md` tem menos de 100 linhas e só descreve o que fazer em cada fase. Cada referência é lida no início da fase que a usa, então o agente não carrega o playbook de refatoração enquanto ainda está analisando o projeto.
- **Três compromissos explícitos, com o motivo.** Nada é alterado antes da confirmação; o comportamento é preservado; o resultado é reportado como foi. A skill explica por que cada regra existe, em vez de só impor, para que o agente saiba decidir nos casos que o texto não prevê.
- **Fases 1 e 2 somente leitura.** Nem dependências são instaladas antes da confirmação. O relatório só é gravado em arquivo depois da resposta do usuário.
- **Pausa como fim de resposta.** A Fase 2 termina com a pergunta `Proceed with refactoring (Phase 3)? [y/n]` e o agente para. Comentário ou dúvida sobre o relatório não vale como confirmação.
- **Um finding por anti-pattern.** Todas as ocorrências ficam na linha `File:`, com as linhas conferidas por releitura numerada antes de escrever. Isso evita relatórios inflados e linhas citadas de memória.
- **Contrato HTTP preservado.** Rotas, payloads, status codes, mensagens e o comando de start não mudam. As exceções são correções de segurança, e toda diferença aparece em `Behavior Changes` no resumo final.
- **Validação por comparação, não por inspeção.** O script `http_smoke.py` grava as respostas de todos os endpoints antes da refatoração e compara com as de depois. As mudanças esperadas são declaradas antes de rodar o "depois", para que uma regressão não seja racionalizada como intencional.
- **A aplicação sobe sem configuração nova.** Segredos saem do código, mas a ausência deles no ambiente não impede o boot: chaves efêmeras em desenvolvimento e integrações desligadas quando sem credencial.
- **Lista do que não aplicar sozinha.** Autenticação obrigatória em todas as rotas, mudança de formato de resposta e remoção de rotas quebrariam os clientes. Esses findings entram no relatório e ficam em `Deferred`, com o motivo.
- **`✓` só com prova.** O resumo final marca `✓` apenas no que foi verificado na execução; o que falhou aparece como `✗`.

### Anti-patterns do catálogo

Os 22 itens vieram dos padrões encontrados na análise manual, generalizados para qualquer stack.

| Severidade | Anti-patterns | Por que entraram |
|---|---|---|
| CRITICAL | Injeção por query montada com entrada; credenciais hardcoded; God Class; exposição de dados sensíveis; armazenamento inseguro de senhas; operação perigosa exposta sem proteção | Cobrem os exemplos de CRITICAL do enunciado, e todos apareceram na análise manual |
| HIGH | Regra de negócio no controller ou na rota; camadas misturadas; estado global mutável; acoplamento sem injeção de dependência; autenticação ou autorização ausente | São as violações de MVC e SOLID que a refatoração existe para corrigir |
| MEDIUM | Queries N+1; escritas sem transação; validação ausente; tratamento de erro local ou engolido; código duplicado; API deprecated; fluxo assíncrono desestruturado | Problemas de padronização e performance que se repetem entre os projetos; API deprecated é exigência do enunciado |
| LOW | Magic numbers; nomenclatura ruim; `print` como log; código morto e ruído | Custo de leitura, presente em todos os projetos |

Cada entrada traz sinais concretos ("query dentro de laço que percorre o resultado de outra query"), uma seção "não confundir com" quando há falso positivo comum, e regras para subir ou descer a severidade conforme o contexto.

### Como a skill ficou agnóstica de tecnologia

- **Sinais descritos pelo comportamento do código**, com exemplos de sintaxe em mais de uma linguagem.
- **Tabelas de detecção para várias stacks:** 8 linguagens pelo manifesto, 11 famílias de framework, padrões de rota de 10 frameworks, drivers e ORMs.
- **Exemplos fictícios.** Os exemplos das referências usam um domínio de biblioteca, e nenhum arquivo, rota ou tabela dos três projetos é citado. A skill não "conhece" as respostas.
- **Playbook alternando Python e JavaScript**, com uma tabela de convenções por framework (como registrar rotas, onde fica o erro central, como obter um recurso por requisição).
- **Estratégia definida pelo ponto de partida, não pela stack:** monolito, camadas nominais, parcialmente em camadas ou MVC adequado.
- **Validação no nível HTTP.** O smoke test não depende da linguagem da aplicação.

### Desafios encontrados

- **Preservar endpoints e corrigir falhas ao mesmo tempo.** Algumas rotas originais são a própria vulnerabilidade (SQL arbitrário, senha na resposta). A solução foi separar "contrato a preservar" de "mudanças de segurança permitidas", manter rotas perigosas respondendo com 403 por padrão e exigir que cada mudança seja declarada antes da validação.
- **Servidor antigo esquecido no ar.** Ao testar o script, a segunda execução falou com o processo da primeira, porque o PID guardado era o do `npm start` e não o do servidor. O playbook passou a mandar conferir a porta antes de cada boot e encerrar o processo pela porta.
- **Troca de `datetime.utcnow()`.** O substituto direto devolve data com fuso, o que quebra comparações com o banco e muda o formato das respostas. O playbook traz um helper que mantém UTC sem fuso.
- **Banco em memória.** Conexão por requisição, a correção usual para conexão global, esvaziaria um banco `:memory:`. O playbook trata o caso: conexão única, criada na composição e injetada.
- **Contagem de arquivos.** A pasta da skill fica dentro do projeto e seria contada como código. A análise exclui `.claude/` de forma explícita.

### Ensaio das Fases 1 e 2

Antes das execuções completas, as duas fases de leitura foram ensaiadas no projeto 1 em modo não interativo (`claude -p "/refactor-arch"`). A skill foi encontrada pelo comando, detectou a stack (Python, Flask 3.1.1, SQLite, 4 arquivos, 19 rotas), gerou 20 findings no formato do template (6 CRITICAL, 6 HIGH, 4 MEDIUM, 4 LOW), cobriu os 14 problemas da análise manual, registrou `Deprecated APIs: none detected`, parou na pergunta de confirmação e não alterou nenhum arquivo.

### Iterações

- **Projeto 1:** a execução completa funcionou na primeira tentativa. O único ajuste na skill veio do resumo final: a execução reportou três findings "resolvidos com ressalva", categoria que o template não previa, e o template ganhou a seção `Partial`.
- **Projetos 2 e 3:** a registrar nas etapas 4 e 5.

## Resultados

### Resumo dos relatórios

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Resolvidos | Relatório |
|---|---|---|---|---|---|---|---|
| code-smells-project | 6 | 6 | 4 | 4 | 20 | 19 (3 parciais), 1 adiado | [audit-project-1.md](reports/audit-project-1.md) |
| ecommerce-api-legacy | | | | | | pendente (etapa 4) | |
| task-manager-api | | | | | | pendente (etapa 5) | |

### Projeto 1 — code-smells-project

A skill rodou as 3 fases em uma única execução, sem ajuste nos arquivos de referência. O relatório cobriu os 14 problemas da análise manual e acrescentou outros 6 (God File, exposição de dados em erros, acoplamento sem injeção de dependência, autenticação ausente, código morto e nomes numerados).

**Findings resolvidos:** 19 de 20.

- **Adiado:** autenticação obrigatória nas rotas de negócio e restrição de CORS, porque quebrariam os clientes atuais. Só as rotas `/admin/*` foram protegidas.
- **Parciais:** `/admin/query` foi mantida, protegida por token, com recomendação de remoção; excluir um produto continua deixando itens de pedido órfãos; a atualização de produto continua sem validar tamanho do nome e categoria, para não recusar chamadas hoje aceitas.

**Estrutura antes e depois:**

```
ANTES                         DEPOIS
app.py                        app.py                (composition root)
controllers.py                config/settings.py
models.py                     database/             connection, schema, seed
database.py                   models/               produto, usuario, pedido, admin
                              services/             pedido, usuario, relatorio, notificacao, senha
                              controllers/          produto, usuario, pedido, relatorio, sistema, admin, validacao
                              routes/               um blueprint por domínio
                              middlewares/          erros, error_handler, auth
                              .env.example
```

O código passou de 4 arquivos e 780 linhas para 30 módulos e cerca de 1.200 linhas, com um módulo por domínio em cada camada.

**Validação:**

- **Boot:** `python app.py` sobe sem nenhuma variável de ambiente, com debug desligado.
- **Smoke test da skill:** 86 requisições; 64 respostas idênticas às originais e 22 mudanças intencionais, todas declaradas.
- **Linha de base independente** (`bash baseline/run.sh 1`): 31 de 40 respostas idênticas a [baseline/project-1.txt](baseline/project-1.txt). As 9 diferenças são as 7 marcadas como "deve mudar" e 2 consequências do guard administrativo (`/admin/query` sem `sql` responde 403, e o `/health` final mostra os dados preservados porque o reset foi bloqueado).
- **Nova varredura:** nenhuma query concatenada com entrada, nenhum segredo literal, nenhum `print`, nenhum `except` genérico; models e services não importam objetos de requisição.
- **Linhas do relatório:** as 136 referências de arquivo e linha existem no código original.

Log do boot e das primeiras requisições após a refatoração:

```
INFO __main__: Servidor iniciado em http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
INFO werkzeug: "GET / HTTP/1.1" 200 -
INFO werkzeug: "GET /health HTTP/1.1" 200 -
INFO controllers.produto_controller: Listando 10 produtos
INFO werkzeug: "GET /produtos HTTP/1.1" 200 -
INFO werkzeug: "GET /produtos/busca?q=d'agua HTTP/1.1" 200 -
INFO werkzeug: "POST /produtos HTTP/1.1" 201 -
```

**Mudanças de comportamento**, todas de segurança ou validação:

- `GET /health`, `GET /usuarios` e `GET /usuarios/<id>` deixaram de devolver chave, caminho do banco e senhas.
- `POST /login` com injeção de SQL responde 401; as senhas passaram a ser gravadas com hash, e senhas em texto puro de um banco antigo são convertidas no boot.
- `/admin/query` e `/admin/reset-db` respondem 403 sem o cabeçalho `X-Admin-Token`; sem `ADMIN_TOKEN` no ambiente, ficam desligadas.
- Entradas inválidas que causavam erro 500 respondem 400; erros internos devolvem mensagem genérica.
- Pedido com quantidade zero ou negativa, usuário inexistente ou email duplicado passa a ser recusado com 400; alterar o status de pedido inexistente responde 404.
- O servidor passa a escutar em `127.0.0.1` por padrão, ajustável por `APP_HOST`.

**Checklist de validação:**

Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente (API de e-commerce: produtos, usuários, pedidos, relatório de vendas)
- [x] Número de arquivos analisados condiz com a realidade (4 arquivos, 780 linhas, 19 rotas)

Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (20)
- [x] Detecção de APIs deprecated incluída (`Deprecated APIs: none detected`)
- [x] Skill pausa e pede confirmação antes da Fase 3

Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

### Projetos 2 e 3

Pendentes (etapas 4 e 5). As observações sobre o comportamento da skill em stacks diferentes entram depois dessas execuções.

## Como Executar

### Pré-requisitos

- Claude Code instalado e configurado
- Python 3 e Node.js (o Python 3 também é usado pelo smoke test da skill)
- Dependências de cada projeto instaladas:

```bash
cd code-smells-project && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ..
cd task-manager-api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ..
cd ecommerce-api-legacy && npm install && cd ..
```

### Executar a skill

A skill é de projeto: o Claude Code a encontra quando é iniciado dentro da pasta que contém `.claude/skills/refactor-arch/`. Rode em modo interativo, porque a Fase 2 pausa e espera a sua resposta.

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch ../reports/audit-project-1.md"

# Projeto 2 (depois de copiar a skill: cp -r code-smells-project/.claude ecommerce-api-legacy/)
cd ../ecommerce-api-legacy
claude "/refactor-arch ../reports/audit-project-2.md"

# Projeto 3 (depois de copiar a skill: cp -r code-smells-project/.claude task-manager-api/)
cd ../task-manager-api
claude "/refactor-arch ../reports/audit-project-3.md"
```

O argumento é opcional e indica onde salvar o relatório de auditoria. Sem ele, o relatório vai para `reports/audit-report.md` dentro do projeto.

O que esperar:

1. **Fase 1:** o bloco `PHASE 1: PROJECT ANALYSIS`, com stack, banco, domínio, arquitetura e número de rotas.
2. **Fase 2:** o `ARCHITECTURE AUDIT REPORT`, seguido da pergunta `Proceed with refactoring (Phase 3)? [y/n]`. Nada é alterado até você responder.
3. **Fase 3:** depois do `y`, a skill salva o relatório, grava as respostas dos endpoints, refatora, sobe a aplicação de novo, compara as respostas e imprime `PHASE 3: REFACTORING COMPLETE`.

### Validar que a refatoração não quebrou os endpoints

A skill faz a própria validação na Fase 3. A linha de base deste repositório é uma conferência independente, feita antes de a skill existir.

`bash baseline/run.sh <n>` zera o banco do projeto `n`, sobe a aplicação, executa as requisições de `baseline/requests-project-<n>.json` e derruba o processo. Para comparar com o comportamento original:

```bash
bash baseline/run.sh 1 /tmp/depois-1.txt
diff baseline/project-1.txt /tmp/depois-1.txt
```

As únicas diferenças esperadas são nas requisições marcadas com "deve mudar", que cobrem falhas de segurança corrigidas pela refatoração (senhas expostas, SQL injection, rotas administrativas sem autenticação).

Se a refatoração mudar o entry point, informe o novo comando em `START_CMD` (e `SEED_CMD`, no projeto 3):

```bash
START_CMD=".venv/bin/python src/app.py" bash baseline/run.sh 1 /tmp/depois-1.txt
```
