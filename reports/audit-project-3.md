# Auditoria de arquitetura — task-manager-api

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3 (versão não declarada no projeto; o .venv local usa 3.14.4)
Framework:     Flask 3.0.0
Dependencies:  flask-sqlalchemy 3.1.1 (SQLAlchemy 2.1.9 instalado), flask-cors 4.0.0, marshmallow 3.20.1, requests 2.31.0, python-dotenv 1.0.0 (as três últimas nunca importadas)
Database:      SQLite (tasks.db) via ORM Flask-SQLAlchemy; schema por db.create_all() no import do app.py
Domain:        Gerenciador de tarefas com login e relatórios de produtividade (tasks, users, categories)
Architecture:  Parcialmente em camadas — models/, routes/, services/ e utils/ existem, mas os 3 arquivos de rotas (733 linhas) concentram validação, regra, acesso a dados e serialização; sem controllers, config nem erro central; CRUD de categorias dentro de report_routes.py; métodos de model, helpers e NotificationService sem uso
Entry point:   app.py (python seed.py && python app.py, porta 5000)
Source files:  15 files analyzed | ~1160 lines of code
Endpoints:     22 routes
DB tables:     users, tasks, categories
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   15 analyzed | ~1160 lines of code

## Summary
CRITICAL: 6 | HIGH: 2 | MEDIUM: 8 | LOW: 4
Deprecated APIs: 3 encontradas

## Findings

### [CRITICAL] Autenticação ou autorização ausente
File: routes/user_routes.py:185-211, routes/user_routes.py:52, routes/user_routes.py:71-78, routes/user_routes.py:119-125, routes/user_routes.py:10-183, routes/task_routes.py:11-299, routes/report_routes.py:12-223, app.py:15
Description: Nenhuma das 22 rotas verifica identidade. `POST /login` devolve o token fixo `'fake-jwt-token-' + str(user.id)` (user_routes.py:210), que nenhuma rota confere; `POST /users` aceita `role` do corpo, inclusive `'admin'` (52, 71-78); `PUT /users/<id>` altera `role` e `active` de qualquer usuário (119-125); `DELETE /users/<id>` apaga qualquer usuário e suas tasks; tasks, relatórios e categorias são lidos e alterados por qualquer cliente; `CORS(app)` libera qualquer origem (app.py:15). Severidade elevada de HIGH para CRITICAL: a escalação a admin por `POST /users` é explorável com uma requisição.
Impact: Qualquer cliente anônimo se cadastra como administrador, lê emails, tasks e relatórios de todos os usuários e altera ou apaga tasks, usuários e categorias de terceiros; qualquer site pode fazer essas chamadas pelo navegador de quem o visita.
Recommendation: `POST /login` mantém os campos atuais e o campo `token` passa a ser um token assinado com a `SECRET_KEY` (`itsdangerous.URLSafeTimedSerializer`, já instalado com o Flask), válido por 8 horas. Um guard único em `middlewares/auth.py`, sempre ligado, lê `Authorization: Bearer <token>`, valida assinatura e validade e carrega o usuário do banco (papel lido do banco; usuário inexistente ou inativo → 401). Respostas: 401 `{"error": "Autenticação necessária"}`, 403 `{"error": "Acesso negado"}`. Política por rota — públicas: `GET /`, `GET /health`, `POST /login`, `GET /categories`, `POST /users` (o `role` enviado só tem efeito quando quem pede apresenta token de admin; caso contrário o usuário é gravado com `role` `user`); só admin: `GET /users`, `DELETE /users/<id>`, `GET /tasks`, `GET /tasks/search`, `GET /tasks/stats`, `GET /reports/summary`, `POST /categories`, `PUT /categories/<id>`, `DELETE /categories/<id>`; dono ou admin: `GET /users/<id>`, `GET /users/<id>/tasks`, `GET /reports/user/<id>`, `PUT /users/<id>` (só admin altera `role` e `active`; não admin enviando esses campos → 403); dono da task ou admin: `GET`, `PUT` e `DELETE /tasks/<id>` (não admin mudando `user_id` para outro usuário → 403); autenticado: `POST /tasks` (não admin com `user_id` diferente do próprio → 403). O papel `manager` não ganha privilégio (o código não define nenhum). CORS passa a liberar só as origens de `CORS_ORIGINS`; sem a variável, nenhuma origem externa. O README passa a explicar como obter o token pelo login do admin do seed (`joao@email.com` / `1234`).
Verification: Sem token, `GET /users`, `GET /tasks`, `GET /reports/summary`, `DELETE /users/2` e `POST /categories` → 401; com token de Maria (`user`), `GET /users`, `GET /users/1`, `DELETE /tasks/1` e `GET /reports/summary` → 403, `GET /users/2` → 200 e `PUT /users/2 {"role":"admin"}` → 403; com token de admin → resposta original. `POST /users` com `"role":"admin"` sem token cria o usuário com `role` `user`. Preflight com `Origin: http://evil.example` não recebe `Access-Control-Allow-Origin`.

### [CRITICAL] Exposição de dados sensíveis
File: models/user.py:16-25, routes/user_routes.py:33, routes/user_routes.py:85, routes/user_routes.py:129, routes/user_routes.py:209
Description: `User.to_dict()` inclui `'password': self.password` (models/user.py:21), o hash MD5 da senha, e esse dicionário é devolvido por `GET /users/<id>` (33), `POST /users` (85), `PUT /users/<id>` (129) e `POST /login` (209).
Impact: Qualquer cliente obtém o hash MD5 da senha de qualquer usuário e o reverte com tabelas prontas (as senhas do seed `1234`, `abcd`, `pass` caem na hora).
Recommendation: Remover `password` de `User.to_dict()`; a serialização lista só `id`, `name`, `email`, `role`, `active`, `created_at`. As quatro respostas deixam de trazer o campo `password`; os demais campos continuam iguais.
Verification: `GET /users/1` (admin), `POST /users`, `PUT /users/2` e `POST /login` devolvem corpo sem a chave `password`; `grep "'password'" models/user.py` não encontra o campo na serialização.

### [CRITICAL] Armazenamento inseguro de senhas
File: models/user.py:27-32, seed.py:19, seed.py:26, seed.py:33
Description: `set_password` grava `hashlib.md5(pwd.encode()).hexdigest()` e `check_password` compara MD5 sem salt; o seed grava `1234`, `abcd`, `pass` por esse caminho.
Impact: Um vazamento do banco (ou da API, finding anterior) entrega as senhas de todos os usuários: MD5 sem salt é revertido por tabelas prontas.
Recommendation: `set_password` passa a usar `werkzeug.security.generate_password_hash` e `check_password` usa `check_password_hash`. A coluna `String(255)` comporta o hash. O seed continua passando por `set_password`, então os logins de exemplo continuam funcionando; o banco de desenvolvimento é recriado pelo `seed.py`, que o README já manda rodar. `import hashlib` sai do model.
Verification: Após o seed, `users.password` começa com o prefixo do KDF (`scrypt:`); `POST /login` com `joao@email.com`/`1234` → 200 e com senha errada → 401; `grep -rn md5` → nenhuma ocorrência.

### [CRITICAL] Operação perigosa exposta sem proteção (debug fixo)
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` liga o debugger do Werkzeug de forma fixa e com bind em todas as interfaces.
Impact: Qualquer pessoa na rede que provoque um erro não tratado recebe o console interativo do Werkzeug e o código-fonte, o que dá execução remota de código.
Recommendation: O debug passa a vir de `APP_DEBUG` em `config/settings.py`, desligado por padrão; host e porta vêm de `APP_HOST` e `APP_PORT` com os padrões originais `0.0.0.0` e `5000`. O comando `python app.py` continua igual.
Verification: Com `python app.py` sem variáveis, o log de boot não contém `Debugger is active` e `app.debug` é `False`.

### [CRITICAL] Credenciais e segredos hardcoded
File: app.py:13, services/notification_service.py:9-10
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` no código; `NotificationService` guarda `email_user = 'taskmanager@gmail.com'` e `email_password = 'senha123'`.
Impact: Quem lê o repositório tem a chave que, após o finding de autenticação, assina os tokens de login (e poderia forjar um token de admin), além da senha da conta SMTP; trocar qualquer um exige alterar código.
Recommendation: Criar `config/settings.py`, único leitor do ambiente, que carrega `.env` com o `python-dotenv` já declarado: `SECRET_KEY = os.environ.get("SECRET_KEY")` ou chave efêmera de `secrets.token_hex(32)` quando ausente; `DATABASE_URL` (padrão `sqlite:///tasks.db`), `APP_DEBUG`, `APP_HOST`, `APP_PORT`, `CORS_ORIGINS`. `app.py` usa `app.config.from_object(Settings)`. As credenciais SMTP saem com a remoção do `NotificationService` sem uso (finding de código morto). Criar `.env.example` com nomes e valores fictícios e `.gitignore` com `.env`, `instance/` e `__pycache__/`. O resumo final avisa que os dois segredos estão no histórico do git e devem ser rotacionados.
Verification: `grep -rn "super-secret-key-123\|senha123"` no código → nenhuma ocorrência; a aplicação sobe sem nenhuma variável definida; o login emite token aceito pelo guard.

### [CRITICAL] God File nas rotas
File: routes/task_routes.py:1-299, routes/user_routes.py:1-211, routes/report_routes.py:1-223
Description: Cada arquivo de rotas declara rotas, lê a requisição, valida entrada, consulta e grava pelo ORM (`Task.query`, `db.session`), calcula regras (atraso, estatísticas, taxa de conclusão), serializa e escolhe status code — 733 linhas com quatro naturezas de responsabilidade; `report_routes.py` ainda atende dois domínios (relatórios e categorias).
Impact: Nenhuma regra pode ser testada ou reutilizada sem passar por HTTP, e qualquer mudança em uma rota mexe no acesso a dados e nas regras de todas as outras do arquivo.
Recommendation: Completar o MVC mantendo as pastas atuais: `config/settings.py`; `models/` (task, user, category: queries, regras da entidade, constantes e `to_dict`); `services/` (`task_service`, `user_service`, `category_service`, `report_service`: casos de uso que cruzam entidades e transações); `controllers/` (um por domínio, mais `validation.py`: leem a requisição, validam, respondem); `routes/` (`task_routes`, `user_routes`, `report_routes`, `category_routes`, `status_routes`: só `add_url_rule` com o guard de cada rota); `middlewares/` (`errors.py`, `error_handler.py`, `auth.py`); `utils/` (`helpers.py` com os helpers usados, `clock.py`); `app.py` como composition root com `create_app()` e o objeto `app` no módulo (o `seed.py` importa `from app import app, db`). Caminhos, métodos, corpos e status continuam iguais, exceto o que as demais Recommendations declaram.
Verification: Arquivos em `routes/` só contêm registro de rotas; `grep -rn "db.session\|db.select\|\.query" controllers routes` → nenhuma ocorrência; smoke test sem mudanças inesperadas.

### [HIGH] Regra de negócio na rota
File: routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:115-124, routes/task_routes.py:273-299, routes/user_routes.py:140-142, routes/user_routes.py:171-180, routes/report_routes.py:12-155
Description: A regra de atraso (`due_date < utcnow` e status fora de `done`/`cancelled`) está escrita dentro de 6 funções de rota; `task_stats`, `summary_report` (contagens, atrasadas com `days_overdue`, atividade de 7 dias, produtividade por usuário) e `user_report` são laços de agregação na rota; `delete_user` apaga as tasks do usuário na rota; `create_task` confere existência de usuário e categoria na rota.
Impact: As regras de atraso e produtividade só podem ser exercitadas por HTTP, estão copiadas em 6 lugares e já podem divergir entre relatório e listagem.
Recommendation: A regra de atraso passa a ser `Task.is_overdue()` (método já existente) chamada em todos os pontos; estatísticas e relatórios vão para `services/report_service.py` usando consultas do model; a exclusão do usuário com suas tasks vai para `services/user_service.py` numa única transação; a checagem de existência de usuário e categoria na criação/atualização de task vai para `services/task_service.py`, lançando `NotFoundError` com as mesmas mensagens (`Usuário não encontrado`, `Categoria não encontrada`). Respostas inalteradas.
Verification: `grep -n "due_date <" controllers routes services` → nenhuma ocorrência (só `models/task.py`); smoke test sem mudanças inesperadas em `/tasks`, `/tasks/stats`, `/reports/*` e `/users/<id>/tasks`.

### [HIGH] Camadas misturadas e camada correta ignorada
File: routes/report_routes.py:157-223, app.py:22-28, models/task.py:38-60, utils/helpers.py:9-23, utils/helpers.py:110-116, routes/report_routes.py:7
Description: O CRUD de categorias (`get_categories`, `create_category`, `update_category`, `delete_category`) mora em `report_routes.py`; `/health` e `/` são declaradas no entry point; `Task.validate_status`, `Task.validate_priority` e `Task.is_overdue` nunca são chamados enquanto as rotas reescrevem a mesma lógica; `calculate_percentage`, `validate_email`, `format_date` e as constantes `VALID_STATUSES`, `VALID_ROLES`, `MIN_TITLE_LENGTH` etc. de `utils/helpers.py` nunca são usados, e as rotas repetem os mesmos cálculos, regex e listas; `report_routes.py` importa `format_date` e `calculate_percentage` sem usá-los.
Impact: A estrutura promete uma separação que o código não cumpre: corrigir a regra no model ou no helper não muda o comportamento da API, porque as rotas usam cópias próprias.
Recommendation: Categorias ganham `routes/category_routes.py`, `controllers/category_controller.py` e `services/category_service.py` com os mesmos caminhos; `/health` e `/` vão para `routes/status_routes.py` + `controllers/status_controller.py` com as mesmas respostas. `Task.is_overdue` passa a ser a única regra de atraso; a validação de status e prioridade usa os métodos e as constantes do model; as constantes de `helpers.py` vão para `models/task.py` (status, título, prioridade) e `models/user.py` (papéis, senha mínima); `calculate_percentage` passa a calcular os três `completion_rate`, `validate_email` valida o email nas duas rotas de usuário e `format_date` serializa `due_date`. `utils/helpers.py` fica só com os helpers usados.
Verification: `grep -rn "route\|add_url_rule" app.py` → nada; `report_routes.py` não contém rotas `/categories`; `grep` encontra chamadas a `is_overdue`, `calculate_percentage`, `validate_email`, `format_date` e nenhuma cópia das regras; smoke test de `/categories`, `/health` e `/` sem mudanças.

### [MEDIUM] Queries N+1
File: routes/task_routes.py:41-57, routes/user_routes.py:22, routes/report_routes.py:53-68, routes/report_routes.py:157-165, routes/report_routes.py:15-28, routes/task_routes.py:275-279
Description: `get_tasks` faz `User.query.get` e `Category.query.get` por task; `get_users` lê `len(u.tasks)` (relacionamento lazy) por usuário; `summary_report` faz `Task.query.filter_by(user_id=u.id).all()` por usuário; `get_categories` faz um `count()` por categoria; `summary_report` faz 9 `count()` separados por status e prioridade e `task_stats` faz 4.
Impact: O número de queries cresce com o volume: com 1000 tasks, `GET /tasks` faz ~2000 consultas.
Recommendation: `GET /tasks` carrega `user` e `category` com `selectinload` (com `ORDER BY id`); contagens por usuário (`task_count`, produtividade) e por categoria viram uma consulta com `GROUP BY`; contagens por status e por prioridade viram uma consulta `GROUP BY` cada, com zero para grupos sem linhas. Respostas idênticas (mesmas chaves, valores e ordem).
Verification: Script com listener `before_cursor_execute` conta as queries de `GET /tasks`, `GET /users`, `GET /categories` e `GET /reports/summary`: número constante (≤ 5) independente do número de linhas; smoke test sem mudanças nessas rotas.

### [MEDIUM] Exclusão de registro com dependentes deixa órfãos
File: routes/report_routes.py:211-223
Description: `delete_category` apaga a categoria sem tocar nas tasks; elas continuam com `category_id` apontando para um id inexistente (o SQLite não aplica as foreign keys por padrão).
Impact: Após apagar uma categoria, tasks exibem `category_id` inválido, e uma nova categoria que reaproveite o id herda essas tasks sem ninguém ter pedido.
Recommendation: As tasks têm valor próprio e a categoria é opcional: `category_service.delete` anula `category_id` das tasks da categoria e apaga a categoria na mesma transação. A resposta continua `200 {"message": "Categoria deletada"}`.
Verification: `DELETE /categories/1` (admin) → 200; em seguida `GET /tasks/1` (admin) mostra `"category_id": null` (antes mostrava `1`).

### [MEDIUM] Validação de entrada ausente ou incompleta
File: routes/task_routes.py:96-113, routes/task_routes.py:140-144, routes/task_routes.py:166-184, routes/task_routes.py:209-213, routes/task_routes.py:260-264, routes/user_routes.py:49-65, routes/user_routes.py:102-125, routes/user_routes.py:191-201, routes/report_routes.py:173-180, routes/report_routes.py:196-202
Description: `priority` texto ou `null` cai em `priority < 1` → `TypeError` 500 (e `True` é aceito como 1); `title` não textual cai em `len()` → 500; `tags` numérico é gravado e quebra `to_dict` (`.split`) em toda leitura seguinte; `int(priority)`/`int(user_id)` na busca → 500 com texto; nome/email/senha não textuais → 500; `PUT /users` grava `name` vazio e `active` de qualquer tipo; `PUT /categories/<id>` sem corpo faz `'name' in None` → 500; `color` não é validada apesar de `is_valid_color` existir; corpos que são lista ou número → 500 em `data.get`.
Impact: Entradas inválidas viram erro 500 ou são gravadas e corrompem dados: uma única task com `tags` numérico derruba `GET /tasks` para todos.
Recommendation: Criar `controllers/validation.py`, usado por todos os controllers, mantendo as mensagens e status existentes. Recusas novas (400): corpo que não é objeto JSON em qualquer `POST`/`PUT` (inclusive `PUT /categories/<id>` sem corpo) → `Dados inválidos`; `title` não textual → `Título inválido`; `priority` não inteiro (texto, bool, decimal, `null`) → `Prioridade deve ser entre 1 e 5`; `description` não textual e não `null` → `Descrição inválida` (tasks e categorias); `tags` que não seja texto nem lista de textos → `Tags inválidas`; na busca, `priority`/`user_id` não inteiros → `Parâmetro priority inválido` / `Parâmetro user_id inválido`; `name` de usuário ou categoria ausente, vazio ou não textual (create e update) → `Nome é obrigatório`; `email` não textual → `Email inválido`; `password` não textual → `Senha inválida`; `active` não booleano → `Campo active inválido`; `email`/`password` não textuais no login → `Email e senha são obrigatórios`; `color` que não passa em `is_valid_color` (7 caracteres começando com `#`) → `Cor inválida`.
Verification: `POST /tasks {"title":"abc","priority":"x"}`, `POST /tasks {"title":"abc","tags":5}`, `GET /tasks/search?priority=x`, `PUT /categories/1` sem corpo, `POST /categories {"name":"X","color":"azul"}` e `PUT /users/2 {"active":"talvez"}` → 400 com as mensagens acima (antes 500 ou gravação).

### [MEDIUM] Tratamento de erro local, repetido ou engolido
File: routes/task_routes.py:62, routes/task_routes.py:137, routes/task_routes.py:151, routes/task_routes.py:204, routes/task_routes.py:221, routes/task_routes.py:236, routes/user_routes.py:87, routes/user_routes.py:130, routes/user_routes.py:149, routes/report_routes.py:186, routes/report_routes.py:207, routes/report_routes.py:221, utils/helpers.py:46, utils/helpers.py:49, utils/helpers.py:88
Description: 12 blocos `try/except` copiados nos handlers, 9 deles `except:` sem tipo (ex.: `except:` envolvendo `strptime` e todo o `get_tasks`); não existe `errorhandler`, e cada handler escolhe a própria mensagem de 500.
Impact: Erros de programação somem sem registro (o `except:` de `get_tasks` esconde qualquer bug sob `Erro interno`), e erros fora dos blocos devolvem página HTML de erro do Flask em vez de JSON.
Recommendation: Criar `middlewares/errors.py` (`AppError`, `ValidationError`, `NotFoundError`, `ConflictError`, `UnauthorizedError`, `ForbiddenError`) e `middlewares/error_handler.py` com handlers para `AppError` (→ `{"error": msg}` com o status da exceção), `HTTPException` (passa como está: 404 de rota, 405, 415) e `Exception` (`db.session.rollback()`, `logger.exception` e `500 {"error": "Erro interno"}`). Os `try/except` saem dos handlers; `strptime` passa a capturar só `(ValueError, TypeError)` mantendo as mensagens de data atuais. Os 500 que tinham mensagens próprias (`Erro ao criar task`, `Erro ao atualizar` etc.) passam a responder `Erro interno`.
Verification: `grep -rn "except:" --include=*.py .` (fora da `.venv`) → nenhuma ocorrência; uma requisição que provoca exceção inesperada (controller forçado num script de verificação) responde `500 {"error": "Erro interno"}` em JSON e o traceback aparece no log.

### [MEDIUM] Código duplicado
File: routes/task_routes.py:17-28, routes/task_routes.py:110, routes/task_routes.py:177, routes/task_routes.py:140-144, routes/task_routes.py:209-213, routes/task_routes.py:296, routes/user_routes.py:61, routes/user_routes.py:71, routes/user_routes.py:106, routes/user_routes.py:120, routes/user_routes.py:162-169, routes/report_routes.py:67, routes/report_routes.py:151, models/task.py:39, utils/helpers.py:75
Description: `get_tasks` remonta campo a campo o que `Task.to_dict` já faz; a lista de status aparece 5 vezes, a de papéis 3, a regex de email 3; a conversão de `tags` lista→texto 2 vezes; o cálculo de `completion_rate` 3 vezes; as validações de título/status/prioridade estão copiadas entre `create_task` e `update_task`.
Impact: Cada correção precisa ser repetida em todas as cópias, e as validações de create e update já divergem (create recusa `title` vazio com `Título é obrigatório`, update com `Título muito curto`).
Recommendation: `GET /tasks` usa `Task.to_dict()` acrescido de `overdue`, `user_name` e `category_name`; `/users/<id>/tasks` usa um único `Task.to_summary_dict()` com os campos atuais; listas de status e papéis viram constantes únicas nos models; a regex fica só em `validate_email`; normalização de `tags` e `completion_rate` (via `calculate_percentage`) viram funções únicas; create e update de task passam pelo mesmo validador, que mantém as mensagens atuais de cada rota (respostas inalteradas).
Verification: `grep -rn "'pending', 'in_progress'"` → uma única definição; `grep -rn "a-zA-Z0-9+_.-"` → uma única; `grep -rn "join(" controllers services models` → uma normalização de tags; smoke test sem mudanças.

### [MEDIUM] Deprecated API: datetime.utcnow()
File: routes/task_routes.py:31, routes/task_routes.py:72, routes/task_routes.py:215, routes/task_routes.py:285, routes/user_routes.py:172, routes/report_routes.py:35, routes/report_routes.py:42, routes/report_routes.py:45, routes/report_routes.py:71, routes/report_routes.py:133, models/task.py:15-16, models/task.py:52, models/user.py:14, models/category.py:11, utils/helpers.py:38, services/notification_service.py:35, seed.py:66-74 (+5 ocorrências no seed)
Description: `datetime.utcnow()` é usado em 22 pontos, inclusive como `default` das colunas; está deprecated desde o Python 3.12 e a `.venv` roda 3.14.
Impact: Cada chamada emite `DeprecationWarning` hoje e o projeto quebra quando a função for removida.
Recommendation: Criar `utils/clock.py` com `utcnow()` que retorna `datetime.now(timezone.utc).replace(tzinfo=None)` (UTC sem fuso, como o banco e a API já usam) e usá-lo em todos os pontos, inclusive no seed e nos `default`/`onupdate` das colunas (passado sem chamar). Respostas com o mesmo formato.
Verification: `grep -rn "datetime.utcnow" --include=*.py .` (fora da `.venv`) → nenhuma ocorrência; boot e smoke test com `python -W error::DeprecationWarning` sem aviso de `utcnow`.

### [MEDIUM] Deprecated API: Query.get()
File: routes/task_routes.py:42, routes/task_routes.py:51, routes/task_routes.py:67, routes/task_routes.py:117, routes/task_routes.py:122, routes/task_routes.py:158, routes/task_routes.py:188, routes/task_routes.py:195, routes/task_routes.py:227, routes/user_routes.py:29, routes/user_routes.py:94, routes/user_routes.py:136, routes/user_routes.py:155, routes/report_routes.py:105, routes/report_routes.py:192, routes/report_routes.py:213
Description: 16 chamadas `Model.query.get(id)`, API legada no SQLAlchemy 2.x (2.1.9 na `.venv`), que emite `LegacyAPIWarning`.
Impact: A API some numa versão futura do SQLAlchemy e gera aviso a cada chamada.
Recommendation: Trocar as 16 chamadas por `db.session.get(Model, id)`, dentro dos models.
Verification: `grep -rn "query.get(" --include=*.py .` (fora da `.venv`) → nenhuma ocorrência.

### [MEDIUM] Deprecated API: Model.query
File: routes/task_routes.py:14, routes/task_routes.py:247-266, routes/task_routes.py:275-281, routes/user_routes.py:12, routes/user_routes.py:35, routes/user_routes.py:67, routes/user_routes.py:109, routes/user_routes.py:140, routes/user_routes.py:159, routes/user_routes.py:197, routes/report_routes.py:15-30, routes/report_routes.py:46-56, routes/report_routes.py:109, routes/report_routes.py:159-163, seed.py:11-13, seed.py:94-96
Description: Todo o acesso a dados usa a interface `Model.query`, marcada como legada no Flask-SQLAlchemy 3.x em favor de `db.session.execute(db.select(...))`.
Impact: O projeto depende de uma API legada que não recebe recursos novos e será removida; a refatoração dos models manteria esse débito.
Recommendation: Todas as consultas, inclusive as do `seed.py`, passam a usar `db.select`/`db.session.execute`/`db.session.scalars`/`db.session.scalar` (`db.func.count`, `db.delete` no seed), dentro dos models.
Verification: `grep -rnE "\.query\b" --include=*.py .` (fora da `.venv`) → nenhuma ocorrência.

### [LOW] Magic numbers e strings
File: routes/task_routes.py:96, routes/task_routes.py:99, routes/task_routes.py:104, routes/task_routes.py:113, routes/task_routes.py:167, routes/task_routes.py:169, routes/task_routes.py:182, routes/user_routes.py:64, routes/user_routes.py:115, routes/report_routes.py:24-28, routes/report_routes.py:45, routes/report_routes.py:129, routes/report_routes.py:180, models/user.py:35
Description: Título entre `3` e `200`, prioridade entre `1` e `5`, prioridade padrão `3`, senha mínima `4`, `priority <= 2` como "alta prioridade", janela de `timedelta(days=7)`, cor padrão `'#000000'`, papel `'admin'` e o mapeamento prioridade 1–5 → `critical`…`minimal` escritos como literais soltos.
Impact: A regra fica escondida e sem nome; mudar um limite exige caçá-lo em vários arquivos.
Recommendation: Constantes nomeadas nos models: `Task.MIN_TITLE_LENGTH`, `MAX_TITLE_LENGTH`, `MIN_PRIORITY`, `MAX_PRIORITY`, `DEFAULT_PRIORITY`, `HIGH_PRIORITY_MAX`, `VALID_STATUSES`, `PRIORITY_LABELS`; `User.MIN_PASSWORD_LENGTH`, `VALID_ROLES`, `DEFAULT_ROLE`, `ADMIN_ROLE`; `Category.DEFAULT_COLOR`; `RECENT_ACTIVITY_DAYS` no `report_service`. Todos os usos as referenciam. Respostas inalteradas.
Verification: `grep -rnE "< 3|> 200|<= 2|days=7|'#000000'" controllers services routes` → nenhuma ocorrência.

### [LOW] Nomenclatura ruim
File: routes/report_routes.py:24-28, routes/task_routes.py:16, routes/user_routes.py:14, routes/report_routes.py:160, routes/report_routes.py:192, models/category.py:14, models/user.py:27
Description: `p1`…`p5` para contagens por prioridade, `t`, `u`, `c` em laços longos, `cat`, `d` em `Category.to_dict`, `pwd`.
Impact: É preciso ler a implementação para saber o que cada nome guarda; `p1`…`p5` só fazem sentido olhando o dicionário da resposta.
Recommendation: Renomear identificadores internos (`priority_counts`, `task`, `user`, `category`, `raw_password` etc.); campos do contrato e colunas ficam como estão.
Verification: `grep -nE "\bp[1-5]\b|for (t|u|c) in|\bcat\b|\bpwd\b" -r controllers services models routes` → nenhuma ocorrência.

### [LOW] print como log
File: routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147, utils/helpers.py:39-41, services/notification_service.py:21, services/notification_service.py:24
Description: `print(f"Task criada: ...")`, `print(f"ERRO: {str(e)}")`, `log_action` e o "Email enviado" do `NotificationService` usam `print` como log no código de aplicação.
Impact: Não há nível, formato nem destino configurável; erros impressos se perdem no stdout.
Recommendation: Os services registram criação, atualização e exclusão de tasks e usuários com `logging.getLogger(__name__)` (`logger.info`, mesma informação, sem dado sensível); erros são registrados pelo handler central; os `print` de `helpers.py` e do `NotificationService` saem com a remoção desses códigos. A saída de console do `seed.py` (script de CLI) permanece.
Verification: `grep -rn "print(" --include=*.py . | grep -v "^./seed.py\|.venv"` → nenhuma ocorrência.

### [LOW] Código morto e ruído
File: app.py:7, routes/task_routes.py:7, routes/user_routes.py:6, routes/report_routes.py:7-8, models/task.py:3, utils/helpers.py:3-7, utils/helpers.py:25-50, utils/helpers.py:57-108, services/notification_service.py:1-48, requirements.txt:4-5, models/task.py:40-60, models/user.py:34-38, routes/task_routes.py:141, routes/task_routes.py:210, utils/helpers.py:103
Description: Imports sem uso (`os, sys, json` em app.py; `json, os, sys, time` em task_routes; `hashlib, json` em user_routes; `json` e os dois helpers em report_routes; `json` em models/task.py; `os, json, sys, math, hashlib` em helpers); funções sem chamador (`sanitize_string`, `generate_id`, `log_action`, `parse_date`, `process_task_data`); `NotificationService` inteiro nunca importado (com estado em memória `self.notifications` e SMTP instanciado no método); `marshmallow` e `requests` declarados e nunca importados; construções verbosas `if ...: return True else: return False` e `type(x) == list`.
Impact: O código sugere notificações por email, validação via marshmallow e chamadas HTTP que não existem, e aumenta o custo de leitura.
Recommendation: Remover os imports sem uso, as funções sem chamador citadas, o arquivo `services/notification_service.py` (o envio de email seria funcionalidade nova) e `marshmallow` e `requests` do `requirements.txt`; `python-dotenv` passa a ser usado pela config; `is_valid_color` passa a ser usado na validação de cor e `User.is_admin` pelo guard. Construções verbosas viram `return <expr>` e `isinstance(x, list)`.
Verification: `pyflakes` (via `.venv`, sem instalar no projeto) ou `grep` dos nomes removidos → nenhum import sem uso e nenhuma referência; `services/notification_service.py` não existe; `requirements.txt` sem `marshmallow` e `requests`.

================================
Total: 20 findings
================================
```

## Errata (Fase 3)

**[MEDIUM] Exclusão de registro com dependentes deixa órfãos — falso positivo.** A gravação do comportamento original mostrou que `DELETE /categories/<id>` já deixava `category_id: null` nas tasks: o relacionamento `Task.category` (backref `Category.tasks`) faz o SQLAlchemy anular a referência ao apagar a categoria. O Impact descrito não acontecia. A Recommendation foi aplicada como escrita (`category_service.delete_category` anula `category_id` explicitamente e apaga a categoria na mesma transação), sem mudança de resposta, e a Verification confirmou `category_id: null` depois da exclusão.
