# Auditoria de arquitetura — ecommerce-api-legacy

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js; versão não declarada no projeto — sem engines/.nvmrc; a máquina local usa v26.2.0)
Framework:     Express 4.22.1 (lockfile; manifesto declara ^4.18.2)
Dependencies:  sqlite3 5.1.7
Database:      SQLite em memória (:memory:) via sqlite3, sem ORM — conexão única criada no construtor de AppManager; schema e seed recriados a cada boot
Domain:        API de LMS com checkout de cursos (usuários, cursos, matrículas, pagamentos, logs de auditoria)
Architecture:  Monolítica — a classe AppManager (141 linhas) concentra conexão, schema, seed, as 3 rotas, regras e SQL; utils.js mistura config, cache e "criptografia"
Entry point:   src/app.js (npm start → node src/app.js), porta 3000
Source files:  3 files analyzed | ~180 lines of code
Endpoints:     3 routes
DB tables:     users, courses, enrollments, payments, audit_logs
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4.22.1
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 5 | HIGH: 6 | MEDIUM: 4 | LOW: 4
Deprecated APIs: none detected

## Findings

### [CRITICAL] Credenciais e segredos hardcoded
File: src/utils.js:2-4
Description: O objeto `config` traz literais versionados: `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"` e `paymentGatewayKey: "pk_live_1234567890abcdef"` (prefixo de chave de produção).
Impact: Quem lê o repositório tem a senha de banco e a chave do gateway de pagamento; trocar qualquer uma exige alterar código e republicar.
Recommendation: Mover para um módulo de configuração que lê `process.env` (`PAYMENT_GATEWAY_KEY`, `DB_USER`, `DB_PASS`), sem valor real como padrão; documentar em `.env.example` e rotacionar as chaves expostas.

### [CRITICAL] Exposição de dados sensíveis
File: src/AppManager.js:45
Description: O checkout executa `console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`)`: grava no log o número completo do cartão recebido em `req.body.card` e a chave do gateway.
Impact: Qualquer pessoa ou sistema com acesso aos logs obtém números de cartão de clientes e a credencial de pagamento.
Recommendation: Remover o cartão e a chave do log; registrar no máximo os 4 últimos dígitos, por um logger com nível.

### [CRITICAL] Armazenamento inseguro de senhas
File: src/utils.js:17-23, src/AppManager.js:68, src/AppManager.js:18
Description: `badCrypto` concatena 10000 vezes os 2 primeiros caracteres do base64 da senha e corta em 10: o "hash" depende só do início da senha, sem salt. O checkout aplica a senha padrão `"123456"` quando `pwd` não vem (`badCrypto(p || "123456")`). O seed grava o usuário `Leonan` com `pass` `'123'` em texto puro.
Impact: Senhas diferentes com o mesmo início geram o mesmo valor; um vazamento da tabela `users` entrega as senhas, e contas criadas sem `pwd` têm senha conhecida.
Recommendation: Trocar por KDF com salt (`crypto.scrypt` nativo), exigir `pwd` na criação de usuário e gravar o seed já com hash.

### [CRITICAL] Operação perigosa exposta sem proteção
File: src/AppManager.js:80-129
Description: `GET /api/admin/financial-report` tem prefixo `admin` e devolve a receita por curso e o nome de cada aluno com o valor pago, sem nenhuma verificação de identidade.
Impact: Qualquer cliente anônimo lê o faturamento e a lista de alunos pagantes.
Recommendation: Proteger a rota com middleware de token de administrador lido do ambiente, negando acesso quando o token não está configurado.

### [CRITICAL] God Class ou God File
File: src/AppManager.js:4-139, src/AppManager.js:28-78, src/utils.js:1-25
Description: `AppManager` abre a conexão (construtor), cria schema e seed (`initDb`), registra as 3 rotas (`setupRoutes`) e, dentro delas, valida, aplica regra de pagamento, executa SQL e monta a resposta. Só o handler de checkout tem 51 linhas. `utils.js` reúne configuração, cache global e função de senha.
Impact: Nenhuma regra pode ser testada ou alterada em isolamento; mexer no relatório arrisca o checkout e vice-versa.
Recommendation: Dividir em config, database (conexão, schema, seed), models por entidade, services (checkout, relatório, usuários), controllers e routes, com `src/app.js` como composition root.

### [HIGH] Operação com várias escritas sem transação
File: src/AppManager.js:50-57, src/AppManager.js:69, src/AppManager.js:133-135, src/AppManager.js:12-16
Description: O checkout encadeia até quatro escritas em callbacks (`INSERT` em `users`, `enrollments`, `payments`, `audit_logs`) sem transação nem rollback. `DELETE /api/users/:id` apaga só a linha de `users` e a própria resposta admite que "as matrículas e pagamentos ficaram sujos no banco"; o schema não tem chaves estrangeiras. Severidade elevada de MEDIUM para HIGH por estar no caminho de dinheiro.
Impact: Falha no `INSERT` de `payments` deixa aluno matriculado sem pagamento registrado; excluir um usuário deixa matrículas e pagamentos órfãos, que aparecem no relatório como `Unknown`.
Recommendation: Envolver as escritas do checkout em `BEGIN`/`COMMIT` com `ROLLBACK` em erro; na exclusão, remover pagamentos e matrículas do usuário na mesma transação.

### [HIGH] Autenticação ou autorização ausente
File: src/app.js:5-10, src/AppManager.js:131-137, src/AppManager.js:40, src/AppManager.js:73-75
Description: `app.js` registra apenas `express.json()` e as rotas, sem middleware de autenticação. `DELETE /api/users/:id` apaga qualquer usuário pelo id. No checkout, quando o email já existe, a matrícula é feita na conta encontrada sem conferir `pwd`.
Impact: Qualquer cliente apaga contas de terceiros e matricula cursos na conta de outra pessoa informando só o email.
Recommendation: Proteger a rota destrutiva com o mesmo middleware de token de administrador. Autenticação obrigatória nas demais rotas muda o contrato da API e fica registrada para decisão do time.

### [HIGH] Regra de negócio no controller ou na rota
File: src/AppManager.js:28-78, src/AppManager.js:80-129
Description: O handler de checkout decide o status do pagamento (`cc.startsWith("4") ? "PAID" : "DENIED"`), cria usuário, matricula, registra pagamento e auditoria, tudo com SQL direto. O handler do relatório percorre cursos e matrículas somando `revenue` dentro da rota.
Impact: As regras de pagamento e de receita só podem ser exercitadas por HTTP e não são reutilizáveis.
Recommendation: Mover para `CheckoutService` e `ReportService`; os controllers ficam com leitura da requisição, validação de formato e status code; o SQL vai para os models.

### [HIGH] Estado global mutável
File: src/utils.js:9-10, src/utils.js:14
Description: `let globalCache = {}` é variável de módulo alterada a cada checkout por `logAndCache` (`globalCache[key] = data`), sem limite nem expiração, e nunca é lida. `let totalRevenue = 0` é um acumulador global exportado.
Impact: O cache cresce sem limite durante a vida do processo e o estado é compartilhado entre todas as requisições e testes.
Recommendation: Remover o cache (nunca é lido) e o acumulador; se um cache for necessário, criá-lo na composição com limite e injetá-lo.

### [HIGH] Acoplamento forte, sem injeção de dependência
File: src/AppManager.js:7, src/AppManager.js:2, src/AppManager.js:45-46
Description: O construtor instancia a própria dependência (`this.db = new sqlite3.Database(':memory:')`), a classe importa direto `config`, `logAndCache` e `badCrypto`, e o "gateway" de pagamento é uma linha embutida no fluxo, sem interface que permita substituí-lo.
Impact: Não há como testar o checkout sem o banco real nem trocar o gateway sem editar o handler.
Recommendation: Criar a conexão na composição (`src/app.js`) e injetá-la nos models; injetar models, gateway de pagamento e hasher de senha nos services.

### [HIGH] Camadas misturadas ou responsabilidade no lugar errado
File: src/AppManager.js:10-23, src/AppManager.js:66-72, src/utils.js:12-23
Description: Schema e seed são criados por `initDb` na mesma classe que atende HTTP; a criação de usuário (`INSERT INTO users`) vive dentro da rota de checkout; `utils.js` abriga `logAndCache` e `badCrypto`, que são infraestrutura e segurança, ao lado da configuração.
Impact: Trocar a persistência ou reutilizar a criação de usuário exige editar o fluxo de checkout.
Recommendation: Schema e seed em módulo de banco; criação de usuário em `UserModel`/service; hash de senha em módulo próprio.

### [MEDIUM] Validação de entrada ausente ou incompleta
File: src/AppManager.js:35, src/AppManager.js:46, src/AppManager.js:132, src/AppManager.js:12, src/AppManager.js:50
Description: O checkout só checa presença de `usr`, `eml`, `c_id` e `card`. `card` numérico faz `cc.startsWith` lançar `TypeError` dentro do callback do driver, fora do alcance do Express (exceção não capturada). `pwd` não é exigido, `eml` não tem checagem de formato, `users.email` não tem constraint de unicidade, a mesma matrícula pode ser repetida e `req.params.id` do DELETE não é validado.
Impact: Uma requisição com `"card": 4111` pode derrubar o processo; entradas inválidas são gravadas e geram usuários e matrículas duplicados.
Recommendation: Validar tipo e formato no controller (strings não vazias, `c_id` e `:id` inteiros positivos) e responder 400 antes de qualquer acesso ao banco.

### [MEDIUM] Tratamento de erro local, repetido ou engolido
File: src/AppManager.js:38, src/AppManager.js:57, src/AppManager.js:92-93, src/AppManager.js:104, src/AppManager.js:106, src/AppManager.js:133, src/app.js:5-14
Description: Erro de banco no `SELECT` de cursos vira 404 (`if (err || !course)`); o `err` do `INSERT` em `audit_logs` e dos `SELECT` de usuário e pagamento é ignorado; no relatório, `enrollments.length` é lido sem olhar `err`; o DELETE responde sucesso mesmo com erro. Não há middleware de erro central.
Impact: Falhas de banco somem sem registro ou viram resposta errada; no relatório, um erro de query lança exceção não capturada.
Recommendation: Models baseados em promise, erros de domínio tipados lançados pelos services e um middleware de erro único registrado no `app.js`.

### [MEDIUM] Fluxo assíncrono desestruturado
File: src/AppManager.js:37-77, src/AppManager.js:83-128, src/AppManager.js:26
Description: O checkout aninha 5 níveis de callback e precisa de `const self = this` para alternar entre `function` e arrow. O relatório aninha 4 níveis e usa os contadores manuais `coursesPending` e `enrPending` para saber quando terminar; `report.push` e `students.push` ocorrem na ordem em que os callbacks chegam.
Impact: A ordem dos cursos e alunos no relatório não é garantida e o tratamento de erro falha em vários ramos.
Recommendation: Encapsular o driver em promises e reescrever os fluxos com `async/await`, com ordenação explícita no resultado.

### [MEDIUM] Queries N+1
File: src/AppManager.js:89-106
Description: Para cada curso há um `SELECT` de matrículas (linha 92) e, para cada matrícula, um `SELECT` de usuário (104) e outro de pagamento (106), dentro de `forEach`.
Impact: O relatório faz 1 + cursos + 2 × matrículas consultas; o tempo cresce com o número de alunos.
Recommendation: Uma única query com `LEFT JOIN` entre `courses`, `enrollments`, `users` e `payments`, agrupando em memória no service.

### [LOW] Código morto e ruído
File: src/AppManager.js:2, src/utils.js:10, src/utils.js:2-3, src/utils.js:5, src/utils.js:25, src/AppManager.js:104
Description: `totalRevenue` é importado em `AppManager.js` e nunca usado nem atualizado; `config.dbUser`, `config.dbPass` e `config.smtpUser` nunca são lidos; `globalCache` é exportado e ninguém o lê; a coluna `email` é selecionada no relatório e descartada.
Impact: Sugere integrações (banco com usuário e senha, SMTP, cache) que não existem.
Recommendation: Remover imports, variáveis e chaves de configuração sem uso.

### [LOW] Magic numbers e strings
File: src/AppManager.js:46, src/AppManager.js:48, src/AppManager.js:108, src/AppManager.js:68, src/utils.js:6, src/utils.js:19, src/utils.js:22
Description: Os status `"PAID"` e `"DENIED"` se repetem como literais; a regra de aprovação é o literal `"4"`; a senha padrão `"123456"`, a porta `3000` e os números `10000` e `10` de `badCrypto` estão soltos no código.
Impact: A regra de aprovação de pagamento não tem nome e os status precisam ser alterados em vários lugares.
Recommendation: Constantes nomeadas (`PAYMENT_STATUS`, prefixo de cartão aprovado) e porta lida da configuração.

### [LOW] Nomenclatura ruim
File: src/AppManager.js:29-33, src/AppManager.js:52, src/AppManager.js:89, src/AppManager.js:4, src/utils.js:12, src/utils.js:17
Description: Variáveis `u`, `e`, `p`, `cid`, `cc`, `enrId` e `c`; a classe `AppManager` não diz o que gerencia; `logAndCache` faz duas coisas; `badCrypto` admite o defeito no nome. Os campos do contrato (`usr`, `eml`, `pwd`, `c_id`, `card`) ficam fora deste finding.
Impact: É preciso ler a implementação para saber o que cada nome guarda.
Recommendation: Nomes descritivos internamente (`name`, `email`, `password`, `courseId`, `cardNumber`), preservando os nomes dos campos da API.

### [LOW] `print` ou `console.log` como log
File: src/AppManager.js:45, src/utils.js:13, src/app.js:13
Description: Três `console.log` em código de aplicação: o processamento do cartão, o aviso de cache e a mensagem de boot.
Impact: Sem nível nem destino configurável, não há como silenciar ou filtrar os logs.
Recommendation: Um módulo de logger com níveis, usado no lugar dos `console.log` diretos.

================================
Total: 19 findings
================================
```
