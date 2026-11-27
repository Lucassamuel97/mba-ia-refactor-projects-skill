# Auditoria de arquitetura — ecommerce-api-legacy

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js; runtime local v26.2.0, sem "engines" declarado)
Framework:     Express 4.22.1 (package.json: ^4.18.2)
Dependencies:  sqlite3 5.1.7 (nenhuma outra dependência direta)
Database:      SQLite em memória (':memory:') via sqlite3, callbacks, sem ORM; conexão única criada no construtor do AppManager; schema e seed recriados a cada boot
Domain:        LMS com checkout de cursos (usuários, cursos, matrículas, pagamentos, log de auditoria)
Architecture:  Monolítica: rotas, regra de negócio, SQL, schema e seed em uma única classe AppManager (141 linhas), mais um utils.js com config, cache e "hash"
Entry point:   src/app.js (npm start → node src/app.js, porta 3000)
Source files:  3 files analyzed | ~180 lines of code
Endpoints:     3 routes
DB tables:     users, courses, enrollments, payments, audit_logs
================================
```

Inventário de rotas (contrato):

| Método | Caminho | Handler |
|---|---|---|
| POST | /api/checkout | `AppManager.setupRoutes`, closure em src/AppManager.js:28 |
| GET | /api/admin/financial-report | closure em src/AppManager.js:80 |
| DELETE | /api/users/:id | closure em src/AppManager.js:131 |

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4.22.1
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 5 | HIGH: 6 | MEDIUM: 3 | LOW: 4
Deprecated APIs: none detected

## Findings

### [CRITICAL] Operação perigosa exposta sem proteção
File: src/AppManager.js:80-129, src/AppManager.js:131-137
Description: `GET /api/admin/financial-report` devolve receita por curso e o nome e o valor pago de cada aluno sem nenhuma verificação de identidade, apesar do prefixo `admin`. `DELETE /api/users/:id` apaga qualquer usuário (`DELETE FROM users WHERE id = ?`) para qualquer cliente.
Impact: Qualquer cliente anônimo lê o faturamento e os dados de pagamento de todos os alunos e apaga a conta de qualquer usuário.
Recommendation: O projeto não tem login, então as duas rotas ficam atrás de um guard de administrador (`middlewares/requireAdminToken.js`) que compara o cabeçalho `X-Admin-Token` com `ADMIN_TOKEN`, lido do ambiente pela config, usando `crypto.timingSafeEqual`. Sem o cabeçalho, a resposta é 401 com o texto `Autenticação necessária`. Com token errado, ou sem `ADMIN_TOKEN` definido no ambiente, a resposta é 403 com o texto `Acesso negado` (texto puro, como o resto da API). O guard fica sempre ligado: sem `ADMIN_TOKEN`, as duas rotas recusam todos os pedidos. Com o token certo, a resposta não muda. O README passa a explicar como definir `ADMIN_TOKEN` e enviar o cabeçalho, e `.env.example` ganha a variável.
Verification: Com a app nos padrões, `GET /api/admin/financial-report` e `DELETE /api/users/2` sem cabeçalho → 401, e com `X-Admin-Token: errado` → 403. Com `ADMIN_TOKEN` definido e o cabeçalho correto → as respostas da gravação original.

### [CRITICAL] Credenciais e segredos hardcoded
File: src/utils.js:2-5
Description: O objeto `config` contém literais versionados: `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` e `smtpUser`. A única leitura de qualquer um deles é a de `paymentGatewayKey`, no log de src/AppManager.js:45. `dbUser`, `dbPass` e `smtpUser` nunca são lidos.
Impact: Quem lê o repositório tem a senha de banco e a chave live do gateway de pagamento. Trocar qualquer uma exige editar código e republicar.
Recommendation: Criar `src/config/index.js`, que lê o ambiente uma vez: `PORT` (padrão 3000) e `ADMIN_TOKEN` (ausente desliga as rotas de admin; veja o finding anterior). Os quatro literais são apagados do código: `dbUser`, `dbPass` e `smtpUser` porque nada os usa, e `paymentGatewayKey` porque seu único uso é o log que o vaza (veja "Exposição de dados sensíveis"). Criar `.env.example` só com nomes e valores fictícios e um `.gitignore` com `.env`. O boot continua sem nenhuma variável obrigatória. O resumo final avisa que esses segredos estão no histórico do git e precisam ser rotacionados.
Verification: Um `grep -rn "senha_super_secreta\|pk_live_\|admin_master" src` sem ocorrências. `npm start` sem variáveis de ambiente sobe na porta 3000.

### [CRITICAL] Armazenamento inseguro de senhas
File: src/utils.js:17-23, src/AppManager.js:68, src/AppManager.js:18
Description: `badCrypto` "criptografa" a senha repetindo os 2 primeiros caracteres do base64 e truncando em 10 caracteres, sem salt. É reversível e senhas diferentes colidem (todas as que começam com as mesmas letras). Quando `pwd` não vem no corpo, `badCrypto(p || "123456")` grava uma senha padrão conhecida. O seed grava a senha de Leonan em texto puro (`'123'`).
Impact: Um vazamento do banco entrega as senhas de todos os usuários, e toda conta criada sem `pwd` tem a senha `123456`.
Recommendation: Criar `src/utils/password.js` com `hashPassword` e `verifyPassword` sobre `scrypt` de `node:crypto`, com salt aleatório por senha, no formato `scrypt$salt$hash`. A criação de usuário no checkout grava esse hash. O seed grava o hash de `'123'` para Leonan, mantendo id, nome e email. `badCrypto` é apagado. A senha padrão deixa de existir: `pwd` passa a ser obrigatório no checkout, e sem ele a resposta é 400 `Bad Request` (antes era 200 com a senha `123456`).
Verification: `grep -rn "badCrypto\|123456" src` sem ocorrências. A coluna `pass` do seed e dos usuários criados começa com `scrypt$`. `POST /api/checkout` sem `pwd` → 400 `Bad Request`.

### [CRITICAL] Exposição de dados sensíveis
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` grava em log, a cada checkout, o número completo do cartão e a chave live do gateway.
Impact: Quem acessa os logs do servidor obtém os cartões completos de todos os compradores e a chave de pagamento.
Recommendation: A linha passa a registrar, pelo logger, só os 4 últimos dígitos (`Processando cartão final 4444`), sem nenhuma chave. Nenhum outro log registra o cartão, a senha ou o corpo da requisição.
Verification: Depois de um `POST /api/checkout` com o cartão `4111222233334444`, o log do servidor não contém `4111222233334444` nem `pk_live`. Um `grep` por `cc}` e `paymentGatewayKey` em src sem ocorrências.

### [CRITICAL] God Class
File: src/AppManager.js:1-141
Description: `AppManager` abre a conexão (linha 7), cria o schema e o seed (`initDb`, 10-23), registra as três rotas e implementa nelas validação, regra de pagamento, criação de usuário, matrícula, auditoria, agregação do relatório financeiro e exclusão de usuário (`setupRoutes`, 25-138). O handler de checkout sozinho tem 50 linhas.
Impact: Nenhum fluxo pode ser testado ou alterado isoladamente. Qualquer mudança no checkout arrisca o relatório e a exclusão, porque tudo compartilha a mesma classe e a mesma conexão.
Recommendation: Dividir em MVC e apagar `AppManager.js` e `utils.js`. A nova estrutura: `config/index.js`; `database/connection.js` (promises sobre o sqlite3, mais um helper de transação); `database/schema.js` (tabelas e seed idênticos); um model por tabela (`userModel`, `courseModel`, `enrollmentModel`, `paymentModel`, `auditLogModel`) e um `reportModel`; `services/checkoutService.js`, `services/paymentGateway.js` e `services/reportService.js`; `controllers/checkoutController.js`, `reportController.js` e `userController.js`; `routes/checkoutRoutes.js`, `adminRoutes.js` e `userRoutes.js`; `middlewares/` (erro, asyncHandler, guard de admin); `utils/` (erros, logger, senha). `app.js` passa a ser o composition root e liga as camadas por injeção. Caminhos, status e textos continuam os mesmos, exceto nas mudanças declaradas nos outros findings.
Verification: `src/AppManager.js` e `src/utils.js` não existem mais. Nenhum arquivo de `controllers/` ou `routes/` contém SQL (`grep -n "SELECT\|INSERT\|DELETE FROM" src/controllers src/routes` vazio). O smoke test não mostra mudanças inesperadas.

### [HIGH] Operação com várias escritas sem transação
File: src/AppManager.js:50-63, src/AppManager.js:69-72, src/AppManager.js:131-137
Description: O checkout faz até quatro escritas encadeadas em callbacks (`INSERT INTO users`, `enrollments`, `payments`, `audit_logs`) sem transação. Se o pagamento falha, a matrícula já gravada fica sem pagamento. O `DELETE FROM users` apaga o usuário e deixa suas matrículas e pagamentos apontando para um id inexistente, e a própria resposta admite isso. A severidade subiu um nível porque o caminho envolve dinheiro.
Impact: Uma falha no meio do checkout deixa matrícula sem pagamento ou usuário criado sem matrícula. A exclusão de um usuário com compras deixa matrículas e pagamentos órfãos, que o relatório financeiro passa a mostrar como aluno `Unknown`.
Recommendation: O caso de uso de checkout executa todas as escritas (criação do usuário, matrícula, pagamento e auditoria) dentro de uma transação (`BEGIN`/`COMMIT`, com `ROLLBACK` em qualquer erro), serializada na conexão compartilhada para que checkouts concorrentes não se misturem. A cobrança simulada acontece antes da transação. Matrículas e pagamentos são histórico financeiro que o relatório lê, então a exclusão de usuário passa a ser recusada com 409 e o texto `Usuário possui matrículas registradas` enquanto ele tiver matrículas. A checagem e o `DELETE` ficam na mesma transação. Usuário sem matrículas continua sendo apagado com a resposta original (200, mesmo texto).
Verification: `DELETE /api/users/1` (Leonan, com matrícula), com o token de admin → 409 `Usuário possui matrículas registradas`, e o relatório seguinte continua mostrando `Leonan` (antes mostrava `Unknown`). `DELETE` de um usuário sem matrículas → 200 com o texto original. Um teste em código que força a falha do `INSERT INTO payments` não deixa nenhuma matrícula nova.

### [HIGH] Validação de entrada ausente ou incompleta
File: src/AppManager.js:29-35, src/AppManager.js:46, src/AppManager.js:132
Description: O checkout só verifica se `usr`, `eml`, `c_id` e `card` são truthy. Não verifica tipos: `card` numérico (`"card": 4111...`) chega a `cc.startsWith("4")` e lança `TypeError` dentro do callback do sqlite, uma exceção não capturada que derruba o processo. `pwd` não é exigido. `c_id` não tem tipo checado. Em `DELETE /api/users/:id`, o `id` vai ao banco sem validação. A severidade subiu um nível porque o problema derruba a aplicação inteira e está no caminho de pagamento.
Impact: Um único `POST /api/checkout` com `card` numérico encerra o servidor para todos os clientes. Uma conta é criada sem senha informada.
Recommendation: Criar `controllers/validation.js` e validar antes de qualquer acesso ao banco. `usr`, `eml`, `pwd` e `card` precisam ser strings não vazias, e `c_id` um inteiro positivo (número ou string de dígitos). Qualquer falha responde 400 `Bad Request`, o texto que já existe. O `:id` de `DELETE /api/users/:id` precisa ser inteiro positivo, senão 400 `Bad Request`. Respostas novas: `card` não-string → 400 (antes derrubava o processo); `pwd` ausente → 400 (antes 200); id não numérico → 400 (antes 200).
Verification: `POST /api/checkout` com `"card": 4111222233334444` (número) → 400 `Bad Request`, e a requisição seguinte ainda é atendida. Sem `pwd` → 400. `DELETE /api/users/abc` com token de admin → 400.

### [HIGH] Autenticação ou autorização ausente
File: src/AppManager.js:40-75, src/AppManager.js:80, src/AppManager.js:131
Description: O checkout identifica o comprador só pelo `eml` do corpo. Se o email já existe, `processPaymentAndEnroll(user.id)` matricula essa conta e grava a auditoria em nome dela sem conferir `pwd`. As rotas de admin e de exclusão não têm guard (veja o finding de operação perigosa). Não existe login, então nenhuma rota emite credencial.
Impact: Qualquer pessoa que saiba o email de um aluno faz compras e matrículas na conta dele, e a trilha de auditoria atribui a ação ao dono da conta.
Recommendation: Política por rota. `POST /api/checkout` continua pública, mas quando o email já existe, `pwd` é conferido com `verifyPassword` contra o hash gravado; senha errada → 401 com o texto `Credenciais inválidas`, sem matrícula nem pagamento. Email novo cria a conta como hoje, com a senha em scrypt. `GET /api/admin/financial-report` e `DELETE /api/users/:id` ficam só para admin, pelo guard `X-Admin-Token`/`ADMIN_TOKEN` (401 sem cabeçalho, 403 com token errado ou sem `ADMIN_TOKEN` configurado). Nenhuma rota fica sem política.
Verification: `POST /api/checkout` com `eml: leonan@fullcycle.com.br` e `pwd: errada` → 401 `Credenciais inválidas`, sem matrícula nova no relatório. Com `pwd: "123"` → 200. As rotas de admin verificadas como no finding de operação perigosa.

### [HIGH] Regra de negócio na rota
File: src/AppManager.js:28-78, src/AppManager.js:80-129, src/AppManager.js:131-137
Description: Os handlers fazem SQL direto (`this.db.get/run/all`), decidem a aprovação do pagamento (`cc.startsWith("4")`, linha 46), criam usuário, matriculam, auditam e agregam a receita por curso (`courseData.revenue += payment.amount`, linha 109) dentro das próprias closures de rota.
Impact: Checkout e relatório só podem ser exercitados por HTTP e não podem ser reutilizados nem testados sem subir o servidor.
Recommendation: As regras saem das rotas. O fluxo de checkout vai para `checkoutService.checkout`, a aprovação para `paymentGateway.charge`, a agregação para `reportService.financialReport` e a exclusão para um método de service com a regra de dependentes. Os controllers só leem `req`, chamam o service e escolhem status e corpo. O SQL fica só nos models. Erros de domínio viram exceções (`NotFoundError` 404, `BusinessRuleError` 400 etc.) com os textos atuais.
Verification: `grep -n "db\.\|SELECT\|INSERT" src/controllers src/routes` sem ocorrências. O smoke test não mostra mudanças inesperadas no checkout de sucesso, no recusado e no de curso inexistente.

### [HIGH] Acoplamento forte, sem injeção de dependência
File: src/AppManager.js:7, src/AppManager.js:46
Description: O construtor instancia a própria conexão (`this.db = new sqlite3.Database(':memory:')`). A cobrança é uma expressão inline (`cc.startsWith("4") ? "PAID" : "DENIED"`) no meio do fluxo, sem nenhuma abstração de gateway.
Impact: Não dá para testar o checkout com outro banco ou com um gateway falso, nem trocar o gateway sem editar a regra de matrícula.
Recommendation: `database/connection.js` exporta `createConnection(path)`, chamada uma única vez em `app.js` com `':memory:'` vindo da config. A conexão é injetada nos models pelo construtor. `services/paymentGateway.js` implementa `charge({ card, amount })` com a mesma regra (prefixo `4` aprovado) e é injetado no `CheckoutService`. Nenhum model, service ou controller faz `require` do sqlite3 ou do gateway concreto.
Verification: `grep -rn "require('sqlite3')" src` só aparece em `database/connection.js`. `grep -rn "new sqlite3" src` só aparece dentro de `createConnection`. O `CheckoutService` recebe `paymentGateway` no construtor.

### [HIGH] Estado global mutável
File: src/utils.js:9, src/utils.js:12-15, src/AppManager.js:59
Description: `globalCache` é um objeto de módulo que `logAndCache` preenche com `last_checkout_${userId}` a cada checkout, sem limite nem expiração. Nenhum código lê esse cache.
Impact: A memória do processo cresce com cada comprador novo, sem que ninguém se beneficie disso. O estado varia com o histórico do processo.
Recommendation: Como nada lê o cache, `globalCache`, `logAndCache` e a chamada da linha 59 são apagados. Nenhuma estrutura em memória substitui o cache. A resposta do checkout não muda.
Verification: `grep -rn "globalCache\|logAndCache" src` sem ocorrências. O checkout de sucesso responde igual à gravação original.

### [MEDIUM] Tratamento de erro local, repetido ou engolido
File: src/AppManager.js:38, src/AppManager.js:57, src/AppManager.js:92-93, src/AppManager.js:104, src/AppManager.js:106, src/AppManager.js:133-135
Description: O erro do `INSERT INTO audit_logs` é ignorado e o checkout responde sucesso mesmo assim (57). Os callbacks de enrollments, users e payments do relatório ignoram `err`: com erro, `enrollments.length` lança `TypeError` e derruba o processo (92-93). A exclusão responde sucesso mesmo quando o `DELETE` falha (133-135). Um erro de banco na busca do curso vira 404 `Curso não encontrado` (38). Não há handler central.
Impact: Erros de banco derrubam o servidor ou são respondidos como sucesso ou como "não encontrado", sem registro em log.
Recommendation: Criar `utils/errors.js` (`AppError`, `ValidationError` 400, `BusinessRuleError` 400, `UnauthorizedError` 401, `ForbiddenError` 403, `NotFoundError` 404, `ConflictError` 409), `middlewares/asyncHandler.js` e `middlewares/errorHandler.js`. O handler responde `AppError` com `res.status(code).send(message)` em texto puro, como a API faz hoje. Qualquer outro erro vai ao log e recebe 500 `Erro interno do servidor`. Nenhum erro de banco é ignorado: toda rejeição chega ao handler. Erro de banco na busca do curso passa a ser 500, não mais 404. O `/api/checkout` mantém as mensagens 500 atuais nos pontos em que elas existem (`Erro DB`, `Erro Matrícula`, `Erro Pagamento`, `Erro ao criar usuário`).
Verification: `grep -n "(err" src` só aparece no wrapper de promises de `database/connection.js`. Um teste em código com um model que rejeita mostra 500 e o processo continua no ar. O smoke test não mostra mudanças inesperadas.

### [MEDIUM] Queries N+1
File: src/AppManager.js:83, src/AppManager.js:92, src/AppManager.js:104, src/AppManager.js:106
Description: O relatório financeiro faz 1 query de cursos, mais 1 de matrículas por curso, mais 2 queries (usuário e pagamento) por matrícula.
Impact: O número de consultas cresce com as vendas: 100 matrículas geram mais de 200 queries por chamada ao relatório.
Recommendation: `reportModel.financialRows()` faz uma única query: `courses LEFT JOIN enrollments LEFT JOIN users LEFT JOIN payments`, com o primeiro pagamento de cada matrícula (`p.id = (SELECT MIN(id) ...)`, mesma semântica do `db.get`), ordenada por `c.id, e.id`. O service monta `{ course, revenue, students[] }` em memória, com os mesmos defaults: `student: 'Unknown'` para usuário ausente, `paid: 0` sem pagamento e receita só de pagamentos `PAID`. A ordem passa a ser estável por id de curso e de matrícula.
Verification: `reportModel` contém uma única chamada `db.all`, sem query em laço (`grep -n "forEach\|for (" src/models` sem query dentro). `GET /api/admin/financial-report` com o token de admin devolve o mesmo JSON da gravação original.

### [MEDIUM] Fluxo assíncrono desestruturado
File: src/AppManager.js:37-77, src/AppManager.js:83-128
Description: O checkout aninha seis callbacks (`db.get` → `db.get` → `db.run` → `db.run` → `db.run` → `db.run`) e mistura `this` e `self` para preservar o contexto. O relatório usa os contadores manuais `coursesPending`/`enrPending` para saber quando responder, e a ordem do array depende de qual callback termina primeiro.
Impact: O tratamento de erro falha em vários níveis, a ordem do relatório não é garantida e o fluxo é difícil de seguir e de alterar.
Recommendation: `database/connection.js` embrulha `run`/`get`/`all` em promises (`run` devolve `{ lastID, changes }`). Todo o código de models, services e controllers usa `async/await` de ponta a ponta, sem callbacks nem contadores. A ordem do relatório passa a ser definida pelo `ORDER BY` do finding de N+1.
Verification: `grep -rn "Pending\|function(err\|self\." src` sem ocorrências fora de `database/connection.js`.

### [LOW] Magic numbers e strings
File: src/AppManager.js:21, src/AppManager.js:46, src/AppManager.js:48, src/AppManager.js:108, src/utils.js:6
Description: Os status `"PAID"` e `"DENIED"` aparecem como literais em quatro pontos. O prefixo de aprovação `"4"` está inline na condição. A porta `3000` está fixa no objeto de config.
Impact: A regra de aprovação e os status ficam sem nome, e mudar qualquer um exige caçar literais pelo código.
Recommendation: Criar as constantes `PAYMENT_STATUS = { PAID: 'PAID', DENIED: 'DENIED' }` (em `models/paymentModel.js`, usadas pelo gateway, pelo seed e pelo relatório) e `APPROVED_CARD_PREFIX = '4'` (em `paymentGateway.js`). A porta vem de `config.port`, com padrão 3000 por `PORT`.
Verification: `grep -rn "'PAID'\|\"PAID\"\|'DENIED'\|\"DENIED\"" src` só aparece na definição da constante. `grep -n "startsWith(\"4\")" src` sem ocorrências.

### [LOW] Nomenclatura ruim
File: src/AppManager.js:26, src/AppManager.js:29-33, src/AppManager.js:89, src/utils.js:17
Description: Variáveis `u`, `e`, `p`, `cid`, `cc`; `self` como alias de `this`; `c` para curso; `badCrypto` nomeia uma função que não é criptografia.
Impact: É preciso ler a implementação para saber o que cada nome guarda.
Recommendation: Os nomes internos passam a ser `name`, `email`, `password`, `courseId`, `card`, `course`. `self` desaparece com o async/await, e `badCrypto` é substituída por `hashPassword`. Os campos do contrato (`usr`, `eml`, `pwd`, `c_id`, `card`, `msg`, `enrollment_id`) ficam como estão.
Verification: `grep -rnE "\blet (u|e|p|cc|cid)\b|const self|badCrypto" src` sem ocorrências.

### [LOW] console.log como log
File: src/AppManager.js:45, src/utils.js:13, src/app.js:13
Description: `console.log` é usado para o processamento de cartão, para a escrita no cache e para a mensagem de boot.
Impact: Não há nível nem destino configurável, e o mesmo canal hoje carrega dados sensíveis.
Recommendation: Criar `src/utils/logger.js` (`info`/`warn`/`error` com nível e timestamp, sem dependência nova) e usá-lo em todos os pontos. A mensagem de boot mantém o texto `Frankenstein LMS rodando na porta 3000...`. O log da linha 13 de utils.js é apagado junto com o cache. Nenhum `console.*` fica fora do logger.
Verification: `grep -rn "console\." src` só aparece em `src/utils/logger.js`.

### [LOW] Código morto
File: src/utils.js:10, src/utils.js:25, src/AppManager.js:2
Description: `totalRevenue` é declarado, exportado e importado em AppManager.js:2, mas nunca é lido nem alterado. `globalCache` é exportado sem nenhum importador.
Impact: Sugere um acumulador de receita que não existe e aumenta o custo de leitura.
Recommendation: Apagar `totalRevenue` e as exportações e importações sem uso (o arquivo `utils.js` inteiro deixa de existir, conforme o finding de God Class).
Verification: `grep -rn "totalRevenue" src` sem ocorrências. `src/utils.js` não existe.

================================
Total: 18 findings
================================
```
