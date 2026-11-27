# Skill `refactor-arch` — Refatoração Arquitetural Automatizada

Entrega do desafio de Skills do MBA da Full Cycle: uma skill do Claude Code que analisa, audita e refatora um projeto para o padrão MVC, aplicada a três projetos legados.

O enunciado completo está em [desafio.md](desafio.md). Para instalar e usar a skill em outro projeto, veja [USANDO-EM-OUTROS-PROJETOS.md](USANDO-EM-OUTROS-PROJETOS.md).

## Etapas da entrega

| # | Etapa | O que é entregue | Status |
|---|---|---|---|
| 0 | Linha de base | Respostas de todos os endpoints dos 3 projetos, gravadas antes de qualquer mudança | Concluída |
| 1 | Análise manual | Problemas de cada projeto, documentados na seção "Análise Manual" | Concluída |
| 2 | Criação da skill | `SKILL.md` e arquivos de referência em `code-smells-project/.claude/skills/refactor-arch/` | Concluída |
| 3 | Execução no projeto 1 | `code-smells-project` refatorado e `reports/audit-project-1.md` | Concluída |
| 4 | Execução no projeto 2 | `ecommerce-api-legacy` refatorado e `reports/audit-project-2.md` | Concluída |
| 5 | Execução no projeto 3 | `task-manager-api` refatorado e `reports/audit-project-3.md` | Concluída |
| 6 | Documentação final | As quatro seções deste README preenchidas, no repositório público | Concluída |

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

Para cada projeto (nos projetos 2 e 3, depois de copiar a pasta da skill para dentro dele). Os três projetos cumpriram todos os itens; o detalhe está em [Resultados](#resultados).

- [x] Fase 1 detecta linguagem, framework e domínio corretamente
- [x] Fase 2 encontra no mínimo 5 findings, com pelo menos 1 CRITICAL ou HIGH
- [x] Fase 2 pausa e pede confirmação
- [x] Relatório da Fase 2 salvo em `reports/audit-project-<n>.md`
- [x] Fase 3 cria a estrutura MVC, com config extraída e error handling centralizado
- [x] Aplicação inicia sem erros e os endpoints originais respondem
- [x] Checklist de validação do [enunciado](desafio.md#validação) preenchido
- [x] Código refatorado commitado

No projeto 1, a Fase 2 também precisa encontrar pelo menos 5 dos problemas da análise manual.

### Etapa 6 — Documentação final

- [x] Seção "Análise Manual" preenchida
- [x] Seção "Construção da Skill" preenchida
- [x] Seção "Resultados" preenchida
- [x] Seção "Como Executar" preenchida
- [x] A mesma versão da skill está nos 3 projetos (as três pastas são idênticas)
- [x] Tudo publicado na branch `main` do fork público

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
| code-smells-project | 7 | 5 | 3 | 4 | 19 | 19 de 19, com Impact verificado | [audit-project-1.md](reports/audit-project-1.md) |
| ecommerce-api-legacy | 5 | 6 | 3 | 4 | 18 | 18 de 18, com Impact verificado | [audit-project-2.md](reports/audit-project-2.md) |
| task-manager-api | 5 | 2 | 6 | 4 | 17 |

### Projeto 1 — code-smells-project

Resultado da execução com a skill da iteração 3. O relatório tem 19 findings (7 CRITICAL, 5 HIGH, 3 MEDIUM, 4 LOW) e cobre os 14 problemas da análise manual. Cada finding traz uma Recommendation que elimina todo o Impact e uma linha `Verification`.

**Findings resolvidos:** 19 de 19, cada Recommendation aplicada como escrita e cada Impact verificado.

- **`/admin/query`:** removida (rota, handler e código que executava SQL recebido); responde 404.
- **Autenticação (CRITICAL):** o login devolve um token assinado (`itsdangerous`, válido por 8 horas); um guard único nega por padrão e lê o papel do banco. Públicas: `GET /`, `GET /health`, leitura e busca de produtos, cadastro e login. Dono ou admin: `GET /usuarios/<id>`, `GET /pedidos/usuario/<id>`. Usuário autenticado: `POST /pedidos`, com o dono vindo do token. Só admin: escrita de produtos, listagem de usuários e pedidos, status de pedido, relatório de vendas e reset.
- **Exclusão de produto com pedidos:** responde 409, sem apagar o histórico.
- **Validação:** `PUT /produtos` usa a mesma regra do `POST`; quantidade menor que 1, usuário inexistente e tipos errados respondem 400.
- **CORS:** só as origens de `CORS_ORIGINS`; sem a variável, nenhuma origem externa.

**Estrutura antes e depois:**

```
ANTES                         DEPOIS
app.py                        app.py                (composition root)
controllers.py                config/settings.py
models.py                     database/             connection, schema
database.py                   models/               produto, usuario, pedido, sistema, admin
                              services/             pedido, relatorio, notificacao
                              controllers/          produto, usuario, pedido, relatorio, sistema, admin, validacao
                              routes/               um blueprint por domínio
                              middlewares/          auth, erros, error_handler
                              .env.example
```

O código passou de 4 arquivos e 780 linhas para 28 módulos e cerca de 1.080 linhas.

**Validação:**

- **Boot:** `python app.py` sobe sem nenhuma variável de ambiente, com debug desligado, também com avisos de depreciação tratados como erro.
- **Smoke test da skill:** 89 requisições, com login e token; 37 respostas idênticas às originais e 52 mudanças intencionais, todas declaradas antes da comparação.
- **Linha de base independente com o token de admin** (`SMOKE_HEADERS='{"Authorization":"Bearer ${admin}"}' bash baseline/run.sh 1`): 32 de 40 respostas idênticas a [baseline/project-1.txt](baseline/project-1.txt). As 8 diferenças são as 6 marcadas como "deve mudar" e 2 consequências delas (`/admin/query` sem `sql` responde 404; o `/health` final já não expõe a chave).
- **Política de acesso e Verification:** 52 verificações com o test client do Flask, todas aprovadas. Cada rota de admin sem token responde 401, com token adulterado 401 e com token de cliente 403. As rotas de dono respondem 403 para outro usuário e 200 para o próprio. Um pedido em nome de outro usuário responde 403. As rotas públicas continuam abertas. O cadastro com `"tipo": "admin"` grava `cliente`. Os demais casos também passaram: injeção no login, `/admin/query` (404), 409 na exclusão, validação do `PUT` e CORS para origem externa.
- **Nova varredura:** nenhum `print`, nenhum `except` genérico, nenhum segredo literal, nenhuma flag que desligue a autenticação.
- **Relatório:** 128 referências de arquivo e linha. Três delas, em `database.py`, saíram com a numeração continuada de um `cat -n` de vários arquivos (por exemplo `database.py:164-166` em vez de `76-78`); foram corrigidas no relatório, e a skill passou a exigir numeração de um arquivo por vez.

Log do boot e das primeiras requisições após a refatoração:

```
INFO database.schema: Banco inicializado com dados de exemplo
INFO __main__: SERVIDOR INICIADO - rodando em http://localhost:5000
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
INFO werkzeug: "GET / HTTP/1.1" 200 -
INFO controllers.usuario_controller: Login bem-sucedido: usuario 1
INFO werkzeug: "POST /login HTTP/1.1" 200 -
INFO werkzeug: "GET /health HTTP/1.1" 200 -
INFO controllers.produto_controller: Listando 10 produtos
```

**Mudanças de comportamento**, todas anunciadas nas Recommendations:

- Rotas protegidas respondem 401 sem token e 403 sem papel suficiente; com o token certo, a resposta é a de antes. O login passa a devolver o campo `token`.
- `POST /admin/query` deixou de existir (404).
- `GET /health`, `GET /usuarios` e `GET /usuarios/<id>` deixaram de expor chave, caminho do banco e senhas.
- Login com injeção responde 401; senhas gravadas com hash.
- `DELETE /produtos/<id>` responde 409 enquanto o produto estiver em pedidos.
- Entradas inválidas respondem 400; email duplicado, 409; status de pedido inexistente, 404; erros internos, mensagem genérica.
- CORS fechado por padrão; debug desligado por padrão.

**Como chamar uma rota protegida:**

```bash
TOKEN=$(curl -s -X POST localhost:5000/login -H 'Content-Type: application/json' \
  -d '{"email":"admin@loja.com","senha":"admin123"}' | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')
curl -H "Authorization: Bearer $TOKEN" localhost:5000/usuarios
```

**Checklist de validação:**

Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente (API de e-commerce: produtos, usuários, pedidos, relatório de vendas)
- [x] Número de arquivos analisados condiz com a realidade (4 arquivos, 780 linhas, 19 rotas)

Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos (três referências corrigidas, veja acima)
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (19)
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
- [x] Endpoints originais respondem corretamente (com o token certo nas rotas protegidas)
- [x] Cada Recommendation aplicada como escrita e cada Impact verificado (19/19)

### Projeto 2 — ecommerce-api-legacy

Resultado da execução com a skill da iteração 3, copiada sem alteração do projeto 1 e rodada em Node.js/Express. O relatório tem 18 findings (5 CRITICAL, 6 HIGH, 3 MEDIUM, 4 LOW) e cobre os 15 problemas da análise manual, todos com `Verification`.

**Findings resolvidos:** 18 de 18, cada Recommendation aplicada como escrita e cada Impact verificado.

- **Exclusão de usuário (ponto da revisão):** matrículas e pagamentos são histórico financeiro, então a exclusão de usuário com matrículas responde 409 e nada fica órfão; sem matrículas, apaga como antes.
- **Autenticação:** o projeto não tem login de usuário, então relatório financeiro e exclusão de usuário exigem `X-Admin-Token` igual a `ADMIN_TOKEN` (401 sem cabeçalho, 403 com token errado ou sem a variável). O checkout continua público, mas, quando o email já existe, confere a senha da conta (401 se não bater), em vez de matricular a conta alheia.
- **Transação:** curso, usuário, senha e pagamento são conferidos antes de qualquer escrita; usuário novo, matrícula, pagamento e auditoria são gravados numa única transação. Pagamento recusado não cria mais a conta.
- **Validação:** `usr`, `eml`, `pwd` e `card` precisam ser texto e `c_id` inteiro positivo; `pwd` passou a ser obrigatório, no lugar da senha padrão `123456`.

**Estrutura antes e depois:**

```
ANTES                         DEPOIS
src/app.js                    src/app.js            (composition root)
src/AppManager.js             src/config/           index
src/utils.js                  src/database/         connection, schema
                              src/models/           user, course, enrollment, payment, auditLog, report
                              src/services/         checkout, report, user, paymentGateway
                              src/controllers/      checkout, report, user, validation
                              src/routes/           checkout, admin, user
                              src/middlewares/      asyncHandler, errorHandler, requireAdminToken
                              src/utils/            errors, logger, password
                              .env.example
```

O código passou de 3 arquivos e 180 linhas para 27 módulos e cerca de 560 linhas; a God Class `AppManager` deixou de existir e os callbacks aninhados viraram `async/await`.

**Validação:**

- **Boot:** `npm start` sobe sem nenhuma variável de ambiente, também com `--trace-deprecation` sem avisos.
- **Smoke test da skill:** 21 requisições; 10 respostas idênticas às originais e 11 mudanças anunciadas.
- **Linha de base independente com o token** (`ADMIN_TOKEN=tok SMOKE_HEADERS='{"X-Admin-Token":"tok"}' bash baseline/run.sh 2`): 7 de 11 respostas idênticas a [baseline/project-2.txt](baseline/project-2.txt). As 4 diferenças são anunciadas: checkout sem `pwd` responde 400, a exclusão de Leonan (que tem matrícula) responde 409 e, por consequência, os dois relatórios financeiros seguintes não mostram a matrícula sem senha nem o aluno `Unknown`.
- **Acesso e Verification:** relatório e exclusão sem cabeçalho respondem 401, com token errado ou sem `ADMIN_TOKEN` 403, com o token certo a resposta original; checkout de conta existente com senha errada responde 401; `card` numérico responde 400 em vez de derrubar o processo; exclusão de usuário com matrícula responde 409 e o relatório continua listando o aluno.
- **Nova varredura:** nenhum segredo literal, nenhum `console.log` fora do logger, nenhum SQL fora de `models/` e `database/`; o log mostra só os 4 últimos dígitos do cartão.
- **Relatório:** as 52 referências de arquivo e linha existem no código original; contagens e ordem conferem.
- **Correção além do relatório:** na varredura final, a skill encontrou que JSON malformado devolvia o stack trace com caminhos do servidor (também no legado) e corrigiu no handler central, que agora responde 400 `Bad Request`. Não estava em nenhuma Recommendation; a própria skill registrou isso no resumo final.

Log do boot e dos checkouts após a refatoração:

```
> node src/app.js

[INFO] Frankenstein LMS rodando na porta 3000...
[INFO] Processando cartão final 4444
[INFO] Processando cartão final 0002
```

O log original imprimia o número completo do cartão e a chave `pk_live` do gateway a cada checkout.

**Mudanças de comportamento**, todas anunciadas nas Recommendations:

- `GET /api/admin/financial-report` e `DELETE /api/users/:id`: 401 sem `X-Admin-Token`, 403 com token errado ou sem `ADMIN_TOKEN`; com o token certo, a resposta original. O relatório passa a ter ordem estável por id.
- `DELETE /api/users/:id`: 409 para usuário com matrículas; 400 para id não numérico.
- `POST /api/checkout`: 401 quando o email existe e a senha não confere; 400 sem `pwd` ou com tipos errados; pagamento recusado não cria mais a conta.
- Senhas, inclusive a do seed, gravadas com scrypt e salt; erros internos com mensagem genérica.

**Checklist de validação:**

Fase 1 — Análise
- [x] Linguagem detectada corretamente (JavaScript, Node.js)
- [x] Framework detectado corretamente (Express 4, versão do lockfile)
- [x] Domínio da aplicação descrito corretamente (API de LMS com checkout de cursos)
- [x] Número de arquivos analisados condiz com a realidade (3 arquivos, 180 linhas, 3 rotas)

Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (18)
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
- [x] Endpoints originais respondem corretamente (com o token nas rotas de admin)
- [x] Cada Recommendation aplicada como escrita e cada Impact verificado (18/18)

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
| Playbook de refatoração | `refactoring-playbook.md` | Ordem de execução, smoke test e 17 transformações com código antes e depois, inclusive autenticação e autorização por padrão |

### Decisões de design

- **`SKILL.md` curto, conhecimento nas referências.** O `SKILL.md` tem menos de 100 linhas e só descreve o que fazer em cada fase. Cada referência é lida no início da fase que a usa, então o agente não carrega o playbook de refatoração enquanto ainda está analisando o projeto.
- **Quatro compromissos explícitos, com o motivo.** Nada é alterado antes da confirmação; o que a Fase 2 recomenda é o que a Fase 3 faz; o resto do comportamento é preservado; o resultado é reportado como foi. A skill explica por que cada regra existe, em vez de só impor, para que o agente saiba decidir nos casos que o texto não prevê.
- **Fases 1 e 2 somente leitura.** Nem dependências são instaladas antes da confirmação. O relatório só é gravado em arquivo depois da resposta do usuário.
- **Pausa como fim de resposta.** A Fase 2 termina com a pergunta `Proceed with refactoring (Phase 3)? [y/n]` e o agente para. Comentário ou dúvida sobre o relatório não vale como confirmação.
- **Um finding por anti-pattern.** Todas as ocorrências ficam na linha `File:`, com as linhas conferidas por releitura numerada antes de escrever. Isso evita relatórios inflados e linhas citadas de memória.
- **Contrato HTTP preservado, exceto o que a Recommendation anuncia.** Rotas, payloads, status codes, mensagens e o comando de start não mudam, salvo as mudanças descritas nas Recommendations aprovadas (campo sensível removido, rota de SQL arbitrário removida, exclusão com dependentes recusada, entrada inválida recusada). Toda diferença aparece em `Behavior Changes` no resumo final.
- **Validação por comparação, não por inspeção.** O script `http_smoke.py` grava as respostas de todos os endpoints antes da refatoração e compara com as de depois. As mudanças esperadas são declaradas antes de rodar o "depois", para que uma regressão não seja racionalizada como intencional.
- **A aplicação sobe sem configuração nova.** Segredos saem do código, mas a ausência deles no ambiente não impede o boot: chaves efêmeras em desenvolvimento e integrações desligadas quando sem credencial.
- **A Recommendation é um contrato e fecha o Impact.** A Recommendation de cada finding descreve exatamente o que a Fase 3 vai fazer, sem alternativas, e elimina cada consequência descrita no `Impact`. A Fase 3 a aplica por inteiro e executa a linha `Verification` de cada finding para provar que o Impact não acontece mais. Segurança nunca é adiada como decisão de produto.
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

- **Preservar endpoints e corrigir falhas ao mesmo tempo.** Algumas rotas originais são a própria vulnerabilidade (SQL arbitrário, senha na resposta). A primeira versão resolveu o conflito do lado errado: preservava a rota de SQL arbitrário atrás de um token, mesmo com a Recommendation dizendo remover. A versão atual separa o que não tem versão segura (removido) do que tem (protegido), e o contrato só cede onde a Recommendation anuncia (veja "Iteração 2").
- **Servidor antigo esquecido no ar.** Ao testar o script, a segunda execução falou com o processo da primeira, porque o PID guardado era o do `npm start` e não o do servidor. O playbook passou a mandar conferir a porta antes de cada boot e encerrar o processo pela porta.
- **Troca de `datetime.utcnow()`.** O substituto direto devolve data com fuso, o que quebra comparações com o banco e muda o formato das respostas. O playbook traz um helper que mantém UTC sem fuso.
- **Banco em memória.** Conexão por requisição, a correção usual para conexão global, esvaziaria um banco `:memory:`. O playbook trata o caso: conexão única, criada na composição e injetada.
- **Contagem de arquivos.** A pasta da skill fica dentro do projeto e seria contada como código. A análise exclui `.claude/` de forma explícita.

### Ensaio das Fases 1 e 2

Antes das execuções completas, as duas fases de leitura foram ensaiadas no projeto 1 em modo não interativo (`claude -p "/refactor-arch"`). A skill foi encontrada pelo comando, detectou a stack (Python, Flask 3.1.1, SQLite, 4 arquivos, 19 rotas), gerou 20 findings no formato do template (6 CRITICAL, 6 HIGH, 4 MEDIUM, 4 LOW), cobriu os 14 problemas da análise manual, registrou `Deprecated APIs: none detected`, parou na pergunta de confirmação e não alterou nenhum arquivo.

### Iterações

**Iteração 1.** As três execuções completas passaram na primeira tentativa, com a mesma skill. O único ajuste foi no template: a execução do projeto 1 reportou findings "resolvidos com ressalva", e o resumo final ganhou a seção `Partial`.

**Iteração 2 — revisão do desafio.** A correção apontou que a Fase 3 aplicava menos do que a Fase 2 recomendava. No projeto 1, o finding CRITICAL recomendava remover `/admin/query`, e a rota ficou, executando qualquer SQL para quem tivesse o token. No projeto 2, a Recommendation de transação mandava remover matrículas e pagamentos junto com o usuário, e a exclusão continuou deixando órfãos. Conferindo os três relatórios, o mesmo desvio aparecia em outros pontos: `pwd` obrigatório e `:id` validado no projeto 2, validação compartilhada na atualização de produto no projeto 1.

A causa estava na própria skill: a nota do T-06 mandava proteger a rota e só recomendar a remoção, o playbook proibia remover rotas, a preservação do contrato vencia a Recommendation, e o template oferecia `Partial` e `Deferred` como saída. O que mudou:

- **Recommendation como escopo exato da Fase 3.** Virou compromisso no `SKILL.md` e primeira regra do playbook. A Fase 2 passa a ler o playbook para escrevê-la: ações completas, sem alternativas ("ou", "decidir depois"), anunciando a resposta da API que muda. A Fase 3 aplica cada uma por inteiro e confere ação por ação antes de concluir; se uma se mostrar inviável, pergunta em vez de amenizar.
- **Linha `Decision needed`.** O que depende de decisão do produto sai da Recommendation e fica numa linha própria do finding. Só é aplicado se o usuário incluir na confirmação.
- **T-06 — remover ou proteger.** Rota que executa SQL, comando ou código recebido na requisição é removida, porque não tem versão segura; só operações com versão segura ficam atrás de token.
- **T-10 — exclusão com dependentes.** Regra para escolher entre apagar os filhos, anular a referência ou recusar com 409 quando os filhos são histórico ou registro financeiro.
- **T-05, T-11, T-13 e T-16.** Senha padrão, validação recomendada, validações divergentes e serviços sem chamador deixaram de ter uma saída "adiada": a Recommendation escolhe, e a Fase 3 faz.
- **Resumo final sem meio-termo.** `Partial` e `Deferred` deram lugar a `Resolved`, `Not applied` (só o que o usuário excluiu) e `Decisions pending`, e a validação ganhou a linha `Recommendations applied as written`.

**Iteração 3 — conferência contra as devolutivas de outros forks.** Antes de reenviar, a execução do projeto 1 com a skill da iteração 2 foi comparada com os 289 forks públicos do repositório base que entregaram o projeto 1 completo. As mensagens de commit e os READMEs de quem reenviou depois de uma revisão mostram o critério que os corretores aplicam, e ele é mais forte que "aplicar a Recommendation":

- a Recommendation precisa eliminar **todo** o Impact do finding; um finding cujo Impact era "qualquer um lista usuários, pedidos e faturamento" foi devolvido porque só as rotas administrativas ganharam proteção;
- autenticação, autorização e escalação de privilégio não podem ser adiadas como "decisão de produto" nem ficar atrás de uma flag desligada;
- toda rota citada num finding de autenticação precisa responder 401 sem credencial;
- estado em memória sem leitor e serviços sem chamador são removidos.

A iteração 2 ainda deixava a autenticação das rotas de negócio na linha `Decision needed`, que era justamente o caso devolvido em outros forks. O que mudou:

- **Recommendation fecha o Impact inteiro, e cada finding ganha `Verification`.** A linha diz como a Fase 3 prova que o Impact sumiu (requisição e resposta esperada, ou checagem no código), e a Fase 3 a executa com a aplicação nos padrões versionados.
- **`Decision needed` removida.** Segurança é corrigida nesta refatoração, mesmo mudando o contrato; os limites da refatoração ficaram só com o que não elimina Impact (formato de resposta, nomes de campos, troca de tecnologia).
- **T-17 — autenticação e autorização por padrão.** Política para cada rota (pública, dono ou admin, admin), token assinado no login sem dependência nova (`itsdangerous` no Flask, `node:crypto` no Node), guard único que nega por padrão e lê o papel do banco, dono do recurso tirado do token e papel definido só pelo servidor.
- **AP-09 e T-08 — estado em memória.** Coleções em objetos que vivem o processo todo entram como estado global; sem leitor, são apagadas.
- **Smoke test com credencial.** `http_smoke.py` passou a capturar o token do login e reutilizá-lo nas chamadas seguintes, para provar que cada rota protegida devolve a resposta original com o token certo.

Com a skill corrigida, os três projetos voltaram mais uma vez ao código legado original e a skill foi executada de novo em cada um.

## Resultados

### Resumo dos relatórios

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Resolvidos | Relatório |
|---|---|---|---|---|---|---|---|
| code-smells-project | 6 | 5 | 4 | 4 | 19 | 19 de 19, como recomendado; 1 decisão pendente | [audit-project-1.md](reports/audit-project-1.md) |
| ecommerce-api-legacy | 5 | 6 | 4 | 4 | 19 | 19 (3 parciais), nenhum adiado | [audit-project-2.md](reports/audit-project-2.md) |
| task-manager-api | 4 | 3 | 7 | 5 | 19 | 18 (1 parcial), 1 adiado | [audit-project-3.md](reports/audit-project-3.md) |

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

### Projeto 2 — ecommerce-api-legacy

A skill foi copiada do projeto 1 sem alteração e rodou as 3 fases em uma única execução, agora em Node.js/Express. O relatório cobriu os 15 problemas da análise manual e acrescentou outros, entre eles um que derrubava o processo: `card` numérico fazia `cc.startsWith` lançar exceção dentro do callback do driver, fora do alcance do Express.

**Findings resolvidos:** 19 de 19, sendo 3 parciais.

- **Transação:** o checkout passou a gravar matrícula, pagamento e auditoria em uma transação. Apagar um usuário continua deixando matrículas e pagamentos órfãos, porque removê-los tiraria receita do relatório financeiro.
- **Autenticação:** as rotas administrativa e destrutiva exigem token. O checkout segue sem autenticação, porque exigir isso muda o contrato.
- **Validação:** tipos e formato de email são validados. `pwd` opcional e matrícula repetida no mesmo curso ficaram como antes, para não recusar chamadas hoje aceitas.

**Estrutura antes e depois:**

```
ANTES                         DEPOIS
src/app.js                    src/app.js            (composition root)
src/AppManager.js             src/config/           index
src/utils.js                  src/database/         connection, schema
                              src/models/           user, course, enrollment, payment, auditLog, report
                              src/services/         checkout, report, paymentGateway
                              src/controllers/      checkout, report, user
                              src/routes/           checkout, admin, user
                              src/middlewares/      asyncHandler, errorHandler, requireAdminToken
                              src/utils/            errors, logger, password
                              .env.example
```

O código passou de 3 arquivos e 180 linhas para 25 módulos e cerca de 570 linhas. A God Class `AppManager` deixou de existir, e os callbacks aninhados viraram `async/await` sobre uma conexão com promises e transações.

**Validação:**

- **Boot:** `npm start` sobe sem nenhuma variável de ambiente.
- **Smoke test da skill:** 20 requisições; 12 respostas idênticas às originais e 8 mudanças intencionais. Repetido com o token de administrador, 17 de 20 idênticas; as 3 restantes são as validações novas do checkout.
- **Linha de base independente** (`bash baseline/run.sh 2`): com `ADMIN_TOKEN` definido e o cabeçalho enviado, as 11 respostas são idênticas a [baseline/project-2.txt](baseline/project-2.txt). Sem o token, 6 de 11 são idênticas e as outras 5 (relatório financeiro e exclusão de usuário) respondem 403.
- **Nova varredura:** nenhum segredo literal, nenhum SQL fora de `models/` e `database/`, nenhum `req`/`res` em models e services, nenhuma variável global mutável; `console.*` só dentro do módulo de logger.

Log do boot e dos checkouts após a refatoração:

```
> node src/app.js

[INFO] Frankenstein LMS rodando na porta 3000...
[INFO] Processando 497 no cartão final 4444 (chave do gateway ausente)
[INFO] Checkout concluído: matrícula 2 em "Docker"
[INFO] Processando 997 no cartão final 4444 (chave do gateway ausente)
[INFO] Checkout concluído: matrícula 4 em "Clean Architecture"
```

O log original imprimia o número completo do cartão e a chave `pk_live` do gateway a cada checkout.

**Mudanças de comportamento:**

- `GET /api/admin/financial-report` e `DELETE /api/users/:id` exigem o cabeçalho `X-Admin-Token` igual à variável `ADMIN_TOKEN`; sem a variável, respondem 403. Com o token, as respostas são idênticas às originais.
- O relatório financeiro sai em ordem estável (por id); antes a ordem dependia de qual callback terminava primeiro.
- `POST /api/checkout` recusa com 400 campos que não são texto e email sem `@`; antes eram gravados ou derrubavam o processo.
- Checkout sem `pwd` continua respondendo 200, mas a conta é criada sem senha, em vez da senha padrão `123456`.
- As senhas, inclusive a do seed, são gravadas com hash scrypt e salt.
- Erros internos respondem 500 com mensagem genérica.

**Checklist de validação:**

Fase 1 — Análise
- [x] Linguagem detectada corretamente (JavaScript, Node.js)
- [x] Framework detectado corretamente (Express 4.22.1, lido do lockfile)
- [x] Domínio da aplicação descrito corretamente (API de LMS com checkout de cursos)
- [x] Número de arquivos analisados condiz com a realidade (3 arquivos, 180 linhas, 3 rotas)

Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (19)
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
- [x] Endpoints originais respondem corretamente (as duas rotas protegidas, com o token)

### Projeto 3 — task-manager-api

O teste com um projeto que já tinha camadas. A skill classificou a arquitetura como "parcialmente em camadas" e adaptou a estratégia: manteve as pastas existentes, criou `controllers/`, `config/` e `middlewares/`, tirou a lógica de dentro das rotas e deu a categorias e status arquivos próprios. O relatório cobriu os 17 problemas da análise manual.

**Findings resolvidos:** 18 de 19.

- **Adiado:** autenticação obrigatória e restrição do campo `role`, porque mudam o contrato da API. O `token` do login segue sendo um valor de demonstração.
- **Parcial:** o `NotificationService` foi corrigido (credenciais lidas do ambiente, desligado sem elas), mas continua sem nenhum chamador. Ligá-lo à atribuição de tarefas passaria a enviar email, o que é funcionalidade nova.

**APIs deprecated:** 3 encontradas e substituídas. `datetime.utcnow()` deu lugar a um helper que mantém UTC sem fuso; `Model.query.get()` e a interface `Model.query` deram lugar a `db.session.get()` e `db.select()`. O seed e o boot rodam sem avisos mesmo com `-W error::DeprecationWarning`.

**Estrutura antes e depois:**

```
ANTES                         DEPOIS
app.py                        app.py                (composition root)
database.py                   database.py           db, init_app, commit_session
seed.py                       seed.py
models/     task, user,       config/settings.py                                  (nova)
            category          models/               task, user, category
routes/     task, user,       services/             task, user, category, report, notification
            report            controllers/          task, user, category, report, status, validation  (nova)
services/   notification      routes/               task, user, category, report, status
utils/      helpers           middlewares/          errors, error_handler          (nova)
                              utils/helpers.py
                              .env.example
```

As rotas passaram de 733 linhas com toda a lógica para 57 linhas de mapeamento. A regra foi para os services e os models, que agora são usados: `Task.is_overdue` e as constantes de `helpers.py` existiam e ninguém chamava.

**Validação:**

- **Boot:** `python seed.py` e `python app.py` sobem sem variável de ambiente nem `.env`, com debug desligado.
- **Smoke test da skill:** 124 requisições nas 22 rotas; 100 respostas idênticas às originais e 24 mudanças intencionais.
- **Linha de base independente** (`bash baseline/run.sh 3`): 36 de 40 respostas idênticas a [baseline/project-3.txt](baseline/project-3.txt). As 4 diferentes são exatamente as marcadas como "deve mudar": o hash da senha saiu das respostas.
- **Nova varredura:** nenhum `utcnow()` do `datetime`, nenhum `Model.query`, nenhum `except:` genérico, nenhum segredo literal; rotas e controllers não tocam o ORM, e models e services não importam o Flask. O MD5 só aparece para conferir hashes antigos no login, antes de regravá-los.
- **Queries:** `GET /tasks` passou a fazer 1 query; `GET /users` e `GET /categories`, 2.

Log do boot após a refatoração:

```
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000
INFO werkzeug: "GET / HTTP/1.1" 200 -
INFO werkzeug: "GET /health HTTP/1.1" 200 -
```

**Mudanças de comportamento:**

- `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e `POST /login` deixaram de devolver o hash da senha.
- As senhas são gravadas com scrypt; hashes MD5 antigos continuam válidos e são regravados no primeiro login.
- Erros não tratados respondem 500 em JSON, no lugar da página do debugger do Werkzeug.
- Entradas que causavam erro 500 (prioridade em texto, `priority=abc` na busca, corpo que não é objeto) respondem 400.
- Entradas inválidas que eram gravadas (prioridade não inteira, nome vazio, cor fora do formato `#RRGGBB`) passam a ser recusadas com 400.
- O servidor passa a escutar em `127.0.0.1` por padrão, ajustável por `APP_HOST`.
- `marshmallow` e `requests`, declarados e nunca importados, saíram do `requirements.txt`.

**Checklist de validação:**

Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.0.0, com Flask-SQLAlchemy 3.1.1)
- [x] Domínio da aplicação descrito corretamente (API de gerenciamento de tarefas com relatórios e login)
- [x] Número de arquivos analisados condiz com a realidade (15 arquivos, cerca de 1.160 linhas, 22 rotas)

Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (19)
- [x] Detecção de APIs deprecated incluída (`Deprecated APIs: 3 encontradas`)
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

### Comportamento da skill em stacks diferentes

- **A mesma skill nos três.** As três pastas `.claude/skills/refactor-arch/` são idênticas, e nenhuma execução exigiu ajuste para a stack.
- **A estratégia seguiu o ponto de partida, não a linguagem.** No projeto 1 (camadas só no nome) e no projeto 2 (monolito), a skill criou a estrutura completa. No projeto 3, manteve o que já existia e criou só as três camadas que faltavam.
- **Mesmas camadas, mecanismos de cada framework.** Em Flask: blueprints, `errorhandler` e conexão por requisição em `flask.g`. Em Express: routers, middleware de erro, injeção por construtor e `async/await` no lugar dos callbacks.
- **Detalhes de stack foram respeitados.** O banco em memória do projeto 2 manteve uma conexão única, com fila para as transações. No projeto 3, a skill usou o ORM existente em vez de introduzir SQL, e trocou `utcnow()` sem alterar o formato das datas nas respostas.
- **Convenções de cada projeto foram mantidas.** Identificadores em português no projeto 1 e em inglês nos outros dois; `snake_case` em Python e `camelCase` em JavaScript; `src/` só onde já existia.
- **APIs deprecated só onde havia.** O relatório registrou `none detected` nos projetos 1 e 2 e 3 ocorrências no projeto 3.
- **Decisões de segurança consistentes.** Nos três, senhas passaram a usar hash com salt, segredos foram para o ambiente e respostas deixaram de vazar dados. Rotas administrativas e destrutivas ganharam token nos projetos 1 e 2; autenticação obrigatória nas rotas de negócio ficou adiada nos três, por mudar o contrato.

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

Nos projetos refatorados, rotas protegidas exigem credencial. Para compará-las com o original, mande o token: no projeto 2, o `ADMIN_TOKEN`; nos projetos 1 e 3, o token do login de admin, que a linha de base captura sozinha (`SMOKE_HEADERS='{"Authorization":"Bearer ${admin}"}'`):

```bash
ADMIN_TOKEN=meu-token SMOKE_HEADERS='{"X-Admin-Token":"meu-token"}' bash baseline/run.sh 2 /tmp/depois-2.txt
diff baseline/project-2.txt /tmp/depois-2.txt
```

Se a refatoração mudar o entry point, informe o novo comando em `START_CMD` (e `SEED_CMD`, no projeto 3):

```bash
START_CMD=".venv/bin/python src/app.py" bash baseline/run.sh 1 /tmp/depois-1.txt
```
