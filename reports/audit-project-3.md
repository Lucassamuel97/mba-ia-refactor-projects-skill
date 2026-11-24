# Auditoria de arquitetura — task-manager-api

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python (versão não declarada no projeto; o .venv local usa 3.14.4)
Framework:     Flask 3.0.0
Dependencies:  Flask-SQLAlchemy 3.1.1 (SQLAlchemy não fixada; 2.1.9 instalada), Flask-CORS 4.0.0; marshmallow 3.20.1, requests 2.31.0 e python-dotenv 1.0.0 declaradas e nunca importadas
Database:      SQLite (instance/tasks.db) via ORM Flask-SQLAlchemy; schema criado por db.create_all() no import do app.py
Domain:        API de gerenciamento de tarefas com relatórios e login (tasks, users, categories)
Architecture:  Parcialmente em camadas — models/ e routes/ separados, mas validação, regra de negócio, queries e serialização ficam dentro das rotas; sem controllers; services/ e utils/ existem e não são usados
Entry point:   app.py (python app.py, porta 5000; python seed.py popula o banco antes)
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
Stack:   Python + Flask
Files:   15 analyzed | ~1160 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 7 | LOW: 5
Deprecated APIs: 3 encontradas

## Findings

### [CRITICAL] Exposição de dados sensíveis
File: models/user.py:21, routes/user_routes.py:33, routes/user_routes.py:85, routes/user_routes.py:129, routes/user_routes.py:209
Description: `User.to_dict` inclui o campo `password` (o hash MD5). Esse dicionário é devolvido por `get_user` (GET /users/<id>), `create_user`, `update_user` e `login`.
Impact: Qualquer cliente anônimo obtém o hash de senha de qualquer usuário com um GET /users/<id>; somado ao MD5 sem salt, isso entrega as senhas.
Recommendation: Remover `password` de `User.to_dict` e nunca serializar o hash em nenhuma resposta.

### [CRITICAL] Armazenamento inseguro de senhas
File: models/user.py:29, models/user.py:32
Description: `set_password` grava `hashlib.md5(pwd.encode()).hexdigest()` e `check_password` compara com o mesmo MD5, sem salt e sem custo computacional.
Impact: Um vazamento do banco (ou o GET /users/<id> acima) permite reverter as senhas com tabelas prontas em segundos.
Recommendation: Usar `werkzeug.security.generate_password_hash` e `check_password_hash` (já instalados com o Flask), aceitando no login os hashes MD5 antigos e regravando-os no formato novo.

### [CRITICAL] Operação perigosa exposta sem proteção
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` liga o modo debug de forma fixa e escuta em todas as interfaces.
Impact: Um erro não tratado expõe o debugger interativo do Werkzeug e o código-fonte para qualquer máquina da rede.
Recommendation: Ler o debug de configuração (`FLASK_DEBUG`), com padrão desligado, e manter host e porta em um módulo de config.

### [CRITICAL] Credenciais e segredos hardcoded
File: app.py:13, services/notification_service.py:9-10
Description: `SECRET_KEY = 'super-secret-key-123'` está no código do entry point; `NotificationService.__init__` fixa `email_user = 'taskmanager@gmail.com'` e `email_password = 'senha123'`.
Impact: Quem lê o repositório tem a chave de assinatura da aplicação e a senha da conta SMTP; trocar qualquer uma exige alterar código.
Recommendation: Mover para um módulo de config que lê variáveis de ambiente; para `SECRET_KEY`, gerar um valor aleatório quando a variável não existir; para o SMTP, não enviar sem credenciais configuradas.

### [HIGH] Autenticação ou autorização ausente
File: app.py:15, routes/user_routes.py:52, routes/user_routes.py:71-78, routes/user_routes.py:119-122, routes/user_routes.py:135-151, routes/user_routes.py:210 (+ nenhuma das 22 rotas verifica identidade)
Description: `login` devolve `'fake-jwt-token-' + str(user.id)`, que nenhuma rota confere. `create_user` e `update_user` aceitam `role` do corpo, inclusive `admin`. `delete_user` apaga qualquer usuário e todas as tasks dele. `CORS(app)` libera qualquer origem.
Impact: Qualquer cliente lê, altera e apaga dados de qualquer usuário e pode criar ou promover uma conta a administrador.
Recommendation: Emitir token assinado no login e exigir autenticação nas rotas de escrita, restringindo `role` a administradores. Isso muda o contrato da API, então depende de decisão do time.

### [HIGH] Regra de negócio no controller ou na rota
File: routes/task_routes.py:12-63, 86-154, 157-223, 241-271, 274-299, routes/user_routes.py:11-25, 43-90, 93-132, 135-151, 154-183, 186-211, routes/report_routes.py:13-101, 104-155 (+7 handlers menores; as 20 funções de blueprint usam `Model.query` ou `db.session` direto)
Description: As funções de rota validam, consultam o banco, calculam e serializam no mesmo corpo. `summary_report` tem 89 linhas agregando status, prioridade, atraso e produtividade; `create_task` e `update_task` têm ~70 linhas cada; `task_stats` e `user_report` calculam taxa de conclusão e atraso em laços.
Impact: Nenhuma regra pode ser testada sem subir HTTP e banco, e a mesma regra (atraso, taxa de conclusão) já está copiada em várias rotas.
Recommendation: Criar `controllers/` (requisição e resposta) e services por domínio (`task_service`, `user_service`, `category_service`, `report_service`) com as regras e o acesso a dados; as rotas ficam só com o mapeamento de URL.

### [HIGH] Camadas misturadas ou responsabilidade no lugar errado
File: routes/report_routes.py:157-223, models/task.py:38-60, utils/helpers.py:19-23, 43-50, 57-108, 110-116, services/notification_service.py:4-48, app.py:9-31
Description: O CRUD de categorias está dentro do arquivo de rotas de relatórios. As camadas certas existem e são ignoradas: `Task.is_overdue`, `validate_status` e `validate_priority` nunca são chamados; `process_task_data`, `validate_email`, `parse_date` e as constantes `VALID_STATUSES`/`VALID_ROLES` de `utils/helpers.py` não têm uso, enquanto as rotas reescrevem a mesma lógica; `NotificationService` nunca é importado. `app.py` configura, declara rotas e cria o schema (`db.create_all()`) no import do módulo.
Impact: A estrutura de pastas promete uma separação que o código não cumpre; quem corrige a regra no model ou no helper não altera o comportamento real da API.
Recommendation: Mover categorias para rotas, controller e service próprios; fazer os services usarem `Task.is_overdue` e as constantes; trocar o módulo `app.py` por uma application factory que só compõe.

### [MEDIUM] Validação de entrada ausente ou incompleta
File: routes/task_routes.py:96, 113, 167, 182, 261, 264, routes/user_routes.py:64, 102-103, 115, 124-125, routes/report_routes.py:180, 196-202
Description: `create_task`/`update_task` aplicam `len()` e `<` sobre `title` e `priority` sem checar o tipo; `search_tasks` faz `int(priority)` e `int(user_id)` sem tratamento; `update_user` grava `name` e `active` sem checagem; `update_category` usa `'name' in data` sem tratar corpo `null` e aceita `name` vazio; `color` é gravada sem validar o formato.
Impact: Entradas como `"priority": "alta"`, `?priority=abc` ou `"name": null` viram erro 500 em vez de 400.
Recommendation: Centralizar a validação em funções por entidade que checam presença, tipo e faixa e levantam um erro de validação convertido em 400.

### [MEDIUM] Queries N+1
File: routes/task_routes.py:42, 51, routes/user_routes.py:22, routes/report_routes.py:19-28, 56, 163
Description: `get_tasks` faz `User.query.get` e `Category.query.get` para cada task; `get_users` chama `len(u.tasks)` por usuário; `summary_report` faz uma query de tasks por usuário e 9 `count()` separados por status e prioridade; `get_categories` faz um `count()` por categoria.
Impact: O número de queries cresce com os dados: listar 100 tasks dispara até 201 consultas.
Recommendation: Carregar os relacionamentos com `joinedload`/`selectinload` e trocar as contagens por queries agregadas com `GROUP BY`.

### [MEDIUM] Tratamento de erro local, repetido ou engolido
File: routes/task_routes.py:62, 137, 204, 236, routes/user_routes.py:130, 149, routes/report_routes.py:186, 207, 221, utils/helpers.py:46, 49, 88, app.py:1-34
Description: Há 12 `except:` sem tipo; o bloco `try: commit / except: rollback / return 500` está copiado em 9 handlers; `get_tasks` embrulha a função inteira e devolve "Erro interno" sem registrar nada. `app.py` não tem `errorhandler` central.
Impact: Erros de programação somem sem log e cada rota responde falhas de um jeito próprio.
Recommendation: Definir exceções de domínio (`NotFoundError`, `ValidationError`, `ConflictError`) e registrar handlers centrais em um módulo de middlewares, com rollback e log no handler genérico de 500.

### [MEDIUM] Código duplicado
File: routes/task_routes.py:17-28, 30-39, 71-80, 96-114, 166-184, 284-287, 296, routes/user_routes.py:61-72, 105-121, 162-180, routes/report_routes.py:34-37, 67, 132-135, 151
Description: A regra de atraso aparece 6 vezes nas rotas, além de `Task.is_overdue`. `get_tasks` remonta campo a campo o que `Task.to_dict` já faz. A validação de criação é repetida na atualização, em tasks e em usuários. A lista de status está escrita 5 vezes e o regex de email 3 vezes no projeto; a fórmula de `completion_rate` aparece 3 vezes.
Impact: Uma mudança na regra de atraso ou nos status válidos precisa ser repetida em até 6 lugares, e as cópias já divergem (mensagens de erro diferentes entre criar e atualizar).
Recommendation: Usar `Task.is_overdue` e `to_dict` em todos os pontos, um validador por entidade compartilhado por criação e atualização, e constantes únicas para status, roles e regex.

### [MEDIUM] Deprecated API: datetime.utcnow()
File: models/task.py:15-16, 52, models/category.py:11, models/user.py:14, routes/task_routes.py:31, 72, 215, 285, routes/user_routes.py:172, routes/report_routes.py:35, 42, 45, 71, 133, services/notification_service.py:35, utils/helpers.py:38, seed.py:66-67, 69-70, 74
Description: 23 usos de `datetime.utcnow`, como default de colunas e nas comparações de atraso. A função está deprecated desde o Python 3.12 e o ambiente local roda 3.14.
Impact: Emite `DeprecationWarning` hoje e está marcada para remoção em versão futura do Python.
Recommendation: Criar um helper único `utcnow()` baseado em `datetime.now(timezone.utc)`, devolvendo valor sem tzinfo para manter o formato gravado e exibido, e usá-lo em todos os pontos.

### [MEDIUM] Deprecated API: Query.get()
File: routes/task_routes.py:42, 51, 67, 117, 122, 158, 188, 195, 227, routes/user_routes.py:29, 94, 136, 155, routes/report_routes.py:105, 192, 213
Description: 16 chamadas `Model.query.get(id)`, API legada desde o SQLAlchemy 2.0 (a versão instalada é 2.1.9).
Impact: Emite `LegacyAPIWarning` a cada chamada e pode sair em uma versão futura da biblioteca.
Recommendation: Trocar por `db.session.get(Model, id)`.

### [MEDIUM] Acoplamento forte, sem injeção de dependência
File: services/notification_service.py:5-10, 15-17
Description: `NotificationService` fixa host, porta e credenciais no construtor e `send_email` instancia `smtplib.SMTP` direto, sem ponto de substituição. Severidade reduzida de HIGH para MEDIUM porque a classe hoje não é chamada por ninguém.
Impact: Não dá para testar ou reaproveitar o serviço sem um servidor SMTP real.
Recommendation: Receber a configuração e a fábrica de conexão SMTP pelo construtor.

### [LOW] Código morto e ruído
File: app.py:7, routes/task_routes.py:7, 141, 210, 221, 287, routes/user_routes.py:6, routes/report_routes.py:7-8, 37, 61, 121-135, models/task.py:3, 40-43, 46-48, 51-60, models/user.py:34-38, utils/helpers.py:3-7, 9-55, requirements.txt:4-6
Description: Imports sem uso (`os`, `sys`, `json`, `time`, `hashlib`, `math`, `format_date`, `calculate_percentage`); `User.is_admin` e os helpers `format_date`, `sanitize_string`, `generate_id`, `log_action`, `is_valid_color` nunca referenciados; `marshmallow`, `requests` e `python-dotenv` declarados e nunca importados; construções verbosas (`if x: return True else: return False`, `type(tags) == list`, `x = x + 1`).
Impact: Sugere dependências e comportamentos que não existem e aumenta o custo de leitura.
Recommendation: Remover imports, funções e dependências sem uso, e simplificar as construções (`return cond`, `isinstance`, `+=`).

### [LOW] Magic numbers e strings
File: routes/task_routes.py:96, 99, 104, 110, 113, 167, 169, 177, 182, routes/user_routes.py:64, 71, 115, 120, routes/report_routes.py:24-28, 45, 129, 180, app.py:34
Description: Limites de título (3 e 200), faixa de prioridade (1 a 5), prioridade padrão 3, senha mínima 4, janela de 7 dias, `priority <= 2` como "alta prioridade", cor `'#000000'`, listas de status e roles inline, host e porta no `app.run`.
Impact: As regras ficam sem nome e espalhadas; as constantes equivalentes em `utils/helpers.py:110-116` existem e não são usadas.
Recommendation: Reunir as constantes em um módulo único e referenciá-las nos validadores e services.

### [LOW] `print` como log
File: routes/task_routes.py:149, 153, 219, 234, routes/user_routes.py:83, 89, 147, services/notification_service.py:21, 24, utils/helpers.py:39, 41
Description: Criação, atualização, exclusão e erros são registrados com `print`; `log_action` é um wrapper de `print`.
Impact: Sem nível, formato ou destino configurável; erros de banco se perdem no stdout.
Recommendation: Usar `logging.getLogger(__name__)` com `info` para eventos e `exception` para falhas.

### [LOW] Deprecated API: Model.query (interface Query legada)
File: routes/task_routes.py:14-281, routes/user_routes.py:12-197, routes/report_routes.py:15-213 (51 linhas com `Model.query` nas rotas), seed.py:11-13, 94-96
Description: Todo o acesso a dados usa `Model.query.filter_by(...)`, `.all()`, `.count()`, interface marcada como legada no Flask-SQLAlchemy 3.x. Severidade reduzida de MEDIUM para LOW porque não emite aviso nem tem remoção anunciada.
Impact: Código novo fica preso a uma API sem evolução, fora do estilo 2.0 do SQLAlchemy.
Recommendation: Migrar para `db.session.execute(db.select(Model)...)` e `db.session.scalars(...)` ao mover as queries para os services.

### [LOW] Nomenclatura ruim
File: routes/report_routes.py:24-28, routes/task_routes.py:16, 51, models/category.py:14, models/task.py:45, models/user.py:27, 31, utils/helpers.py:57, 83, seed.py:78
Description: `p1` a `p5` para contagens por prioridade; `t` como variável de um laço de 44 linhas em `get_tasks`; `cat`, `d`, `p`, `pwd`, `td`; `process_task_data` não diz que valida e normaliza.
Impact: É preciso ler a implementação para saber o que cada nome guarda.
Recommendation: Renomear para nomes descritivos (`task`, `category`, `priority`, `password`, `counts_by_priority`) sem alterar os campos do contrato da API.

================================
Total: 19 findings
================================
```
