# Auditoria de arquitetura — code-smells-project

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python (runtime não declarado; .venv local usa Python 3.14)
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Database:      SQLite (`loja.db`) via sqlite3, sem ORM, SQL escrito à mão
Domain:        API de e-commerce (produtos, usuários, pedidos, itens de pedido, relatório de vendas)
Architecture:  Camadas nominais — `models.py` e `controllers.py` são arquivos únicos que atendem todos os domínios; rotas admin com SQL dentro do `app.py`; schema e seed dentro de `get_db()`
Entry point:   app.py (`python app.py`, porta 5000, host 0.0.0.0)
Source files:  4 files analyzed | ~780 lines of code
Endpoints:     19 routes
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

Inventário de rotas (contrato): `GET /`, `GET /health`, `GET|POST /produtos`, `GET /produtos/busca`, `GET|PUT|DELETE /produtos/<id>`, `GET|POST /usuarios`, `GET /usuarios/<id>`, `POST /login`, `GET|POST /pedidos`, `GET /pedidos/usuario/<usuario_id>`, `PUT /pedidos/<pedido_id>/status`, `GET /relatorios/vendas`, `POST /admin/reset-db`, `POST /admin/query`.

```text
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 7 | HIGH: 5 | MEDIUM: 3 | LOW: 4
Deprecated APIs: none detected

## Findings

### [CRITICAL] Operação perigosa exposta sem proteção
File: app.py:59-78, app.py:47-57, app.py:8, app.py:88
Description: `POST /admin/query` (`executar_query`) executa com `cursor.execute(query)` qualquer SQL enviado em `dados["sql"]` e faz commit; `POST /admin/reset-db` (`reset_database`) apaga as quatro tabelas sem nenhuma verificação de identidade; `app.config["DEBUG"] = True` e `app.run(host="0.0.0.0", port=5000, debug=True)` deixam o depurador do Werkzeug ligado em todas as interfaces.
Impact: Qualquer cliente anônimo lê, altera ou apaga o banco inteiro (inclusive `DROP TABLE`) e zera a loja com uma requisição; um erro não tratado expõe o console interativo e o código-fonte para a rede.
Recommendation: Remover `POST /admin/query`, o handler `executar_query` e todo código que executa SQL recebido — a rota passa a responder 404. `POST /admin/reset-db` continua existindo, mas só para admin autenticado (guard do T-17: 401 sem token, 403 com token de cliente); o SQL de reset vai para um model administrativo, numa única transação. O debug passa a vir de `APP_DEBUG` em `config/settings.py`, desligado por padrão; host e porta vêm de `APP_HOST`/`APP_PORT`, com os padrões atuais `0.0.0.0` e `5000`.
Verification: `POST /admin/query {"sql":"SELECT * FROM usuarios"}` → 404. `POST /admin/reset-db` sem token → 401, com token de cliente → 403, com token de admin → 200 com o corpo original. `grep -n "debug=True\|DEBUG\"\] = True"` → nenhuma ocorrência; o log de boot mostra `Debug mode: off`.

### [CRITICAL] Injeção por query montada com dados de entrada
File: models.py:28, models.py:47-50, models.py:57-61, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:140, models.py:149-150, models.py:155, models.py:157-161, models.py:163-166, models.py:174, models.py:188, models.py:192, models.py:220, models.py:224, models.py:279-281, models.py:289-297
Description: Todas as queries concatenam valores: `login_usuario` monta `"... WHERE email = '" + email + "' AND senha = '" + senha + "'"`; `criar_produto`/`atualizar_produto`/`criar_usuario` concatenam `nome`, `descricao`, `email`, `senha` vindos do corpo; `buscar_produtos` acrescenta `termo` e `categoria` da query string com `query += " AND ... '" + valor + "'"`.
Impact: `POST /login` com `{"email":"admin@loja.com' --","senha":"x"}` autentica como administrador sem senha; `GET /produtos/busca?q=' UNION SELECT ...` lê a tabela `usuarios` com senhas; um nome de produto com `'` quebra o INSERT ou injeta comandos.
Recommendation: Reescrever todas as queries listadas com placeholders `?` do sqlite3 e os valores numa tupla; em `buscar_produtos`, montar as condições fixas e passar `%termo%`, `categoria`, `preco_min`, `preco_max` na lista de parâmetros; em `login_usuario`, buscar só por email (`WHERE email = ?`) e verificar a senha no código (ver finding de senhas). Resposta que muda: tentativas de injeção deixam de funcionar (o login injetado passa a responder 401).
Verification: `POST /login {"email":"admin@loja.com' --","senha":"x"}` → 401 (antes 200 com o admin). `GET /produtos/busca?q=' OR '1'='1` → lista vazia. `grep -nE "execute\(.*\" \+|query \+=.*\+" ` nos models → nenhuma ocorrência.

### [CRITICAL] Autenticação ou autorização ausente
File: app.py:11-30, app.py:9, controllers.py:167-186, controllers.py:188-203, controllers.py:222-235
Description: Nenhuma rota verifica identidade. `login` devolve os dados do usuário sem emitir credencial, então nada depois dele sabe quem está pedindo; `criar_pedido` aceita `usuario_id` do corpo sem conferir quem pede; `GET /usuarios`, `GET /pedidos`, `GET /relatorios/vendas`, `PUT /pedidos/<id>/status`, `POST/PUT/DELETE /produtos` são abertos; `CORS(app)` libera qualquer origem. Severidade elevada de HIGH para CRITICAL por estar no caminho de autenticação e expor dados pessoais.
Impact: Qualquer cliente anônimo lista todos os usuários e pedidos, cria pedidos em nome de outro usuário, aprova/cancela pedidos, altera preços e apaga produtos, e lê o faturamento; qualquer site pode fazer essas chamadas pelo navegador de quem o visita.
Recommendation: `POST /login` passa a devolver, num campo novo `token` no nível do corpo (os campos `dados`, `sucesso`, `mensagem` continuam), um token assinado com a `SECRET_KEY` via `itsdangerous` (já instalado pelo Flask), válido por 8 horas. Um guard único em `middlewares/auth.py` exige `Authorization: Bearer <token>` e lê o usuário e o `tipo` do banco a cada requisição; sem token válido → 401 `{"erro": "Autenticação necessária"}`, papel insuficiente → 403 `{"erro": "Acesso negado"}`. Política por rota — pública: `GET /`, `GET /health`, `GET /produtos`, `GET /produtos/busca`, `GET /produtos/<id>`, `POST /usuarios`, `POST /login`; usuário autenticado: `POST /pedidos` (o `usuario_id` do corpo precisa ser o do token, a menos que quem pede seja admin; senão 403); dono ou admin: `GET /usuarios/<id>`, `GET /pedidos/usuario/<usuario_id>`; admin: `POST /produtos`, `PUT /produtos/<id>`, `DELETE /produtos/<id>`, `GET /usuarios`, `GET /pedidos`, `PUT /pedidos/<id>/status`, `GET /relatorios/vendas`, `POST /admin/reset-db`. `POST /usuarios` grava sempre `tipo = "cliente"`, ignorando qualquer `tipo` enviado. O CORS passa a liberar só as origens de `CORS_ORIGINS`; sem a variável, nenhuma origem externa é liberada. O README passa a explicar como obter o token (login com `admin@loja.com`).
Verification: Cada rota protegida chamada sem token → 401; com token de cliente nas rotas de admin e de outro dono → 403; com o token certo → resposta original. `POST /pedidos` com token do João e `usuario_id` da Maria → 403. `POST /usuarios {"tipo":"admin",...}` cria usuário `cliente`. Requisição com `Origin: http://evil.example` não recebe `Access-Control-Allow-Origin`.

### [CRITICAL] Exposição de dados sensíveis
File: models.py:83, models.py:99, controllers.py:286-289, controllers.py:12, controllers.py:22, controllers.py:62, controllers.py:96, controllers.py:220, controllers.py:292, app.py:78 (+13 `return ... str(e)` em controllers.py), controllers.py:161, controllers.py:179, controllers.py:182
Description: `get_todos_usuarios` e `get_usuario_por_id` incluem `"senha": row["senha"]` (texto puro) nas respostas de `GET /usuarios` e `GET /usuarios/<id>`; `health_check` devolve `"secret_key": "minha-chave-super-secreta-123"`, `"db_path"` e `"debug"`; os 17 blocos `except` devolvem `str(e)` ao cliente; `print` registra o email de cada cadastro e login.
Impact: Qualquer cliente obtém a senha de todos os usuários e a chave de assinatura da aplicação (com ela forja tokens); mensagens de exceção revelam SQL e estrutura interna; logs acumulam emails de usuários.
Recommendation: Remover `senha` da serialização de usuários (as respostas de `GET /usuarios` e `GET /usuarios/<id>` perdem esse campo). Remover `secret_key`, `db_path` e `debug` de `GET /health` (continuam `status`, `database`, `counts`, `versao`, `ambiente`). Todo erro inesperado passa pelo handler central e devolve 500 `{"erro": "Erro interno do servidor"}`, com o detalhe só no log. Logs de cadastro e login registram o id do usuário, não o email.
Verification: `GET /usuarios` (token de admin) → nenhum item tem `senha`. `GET /health` → sem `secret_key`, `db_path`, `debug`. `grep -n "str(e)"` → nenhuma ocorrência; `grep -n "email)" ` nas chamadas de log → nenhuma.

### [CRITICAL] Armazenamento inseguro de senhas
File: models.py:109-111, models.py:126-129, database.py:76-78
Description: `criar_usuario` grava `senha` como veio; `login_usuario` compara `senha = '<valor>'` em SQL; o seed insere `"admin123"`, `"123456"`, `"senha123"` em texto puro.
Impact: Um vazamento do banco (trivial hoje, via `/admin/query` ou injeção) entrega a senha de todos os clientes, que costumam reutilizá-la em outros serviços.
Recommendation: Gravar senhas com `werkzeug.security.generate_password_hash` no cadastro e no seed (os logins de exemplo continuam funcionando com as mesmas senhas); no login, buscar por email e verificar com `check_password_hash`. O banco `loja.db` é recriado do seed, sem migração. Respostas não mudam.
Verification: Após o boot, `SELECT senha FROM usuarios` → todos os valores começam com `scrypt:`/`pbkdf2:`. `POST /login` com `admin@loja.com`/`admin123` → 200; senha errada → 401.

### [CRITICAL] Credenciais e segredos hardcoded
File: app.py:7, controllers.py:289
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` está versionado no código e repetido literalmente na resposta do health.
Impact: Quem lê o repositório tem a chave que vai assinar os tokens de autenticação e pode se passar por qualquer usuário, inclusive admin; trocar a chave exige alterar código.
Recommendation: Criar `config/settings.py`, único módulo que lê o ambiente: `SECRET_KEY` de `os.environ` ou, se ausente, `secrets.token_hex(32)` efêmero; também `APP_DEBUG` (padrão false), `APP_HOST` (`0.0.0.0`), `APP_PORT` (`5000`), `DATABASE_PATH` (`loja.db`), `CORS_ORIGINS` (vazio). Criar `.env.example` com nomes e valores fictícios (`.env` já está no `.gitignore` da raiz). Nenhum segredo literal fica no código; o boot não exige variável nova. O resumo final avisa que a chave antiga está no histórico do git e deve ser considerada comprometida.
Verification: `grep -rn "minha-chave-super-secreta"` no código → nenhuma ocorrência; `python app.py` sem variáveis sobe normalmente.

### [CRITICAL] God Class ou God File
File: controllers.py:1-292, models.py:1-314, app.py:1-88, database.py:1-86
Description: `controllers.py` atende produtos, usuários, login, pedidos, relatório e health; `models.py` tem SQL e regras de todos os domínios (desconto, estoque, total); `app.py` mistura configuração, registro de rotas, SQL administrativo e boot; `database.py` abre conexão, cria schema e faz seed na mesma função.
Impact: Nenhum domínio pode ser testado ou alterado isoladamente; mexer na regra de pedidos exige editar os mesmos arquivos que servem login e produtos.
Recommendation: Dividir em `config/settings.py`, `database/` (`connection.py`, `schema.py` com schema e seed), `models/` (`produto_model`, `usuario_model`, `pedido_model`, `admin_model`, `sistema_model`), `services/` (`pedido_service`, `relatorio_service`, `notificacao_service`), `controllers/` (um por domínio + `validacao.py`), `routes/` (um Blueprint por domínio), `middlewares/` (`auth`, `erros`, `error_handler`) e `app.py` como composition root com `create_app()`, mantendo o objeto `app` importável. Remover `controllers.py`, `models.py`, `database.py`. Rotas, payloads e start (`python app.py`) iguais, exceto o que os outros findings anunciam.
Verification: Os quatro arquivos antigos não existem; smoke test sem diferenças fora das anunciadas; checklist das guidelines de MVC percorrido item a item.

### [HIGH] Regra de negócio no controller ou na rota
File: controllers.py:208-210, controllers.py:247-250, controllers.py:52-54, controllers.py:266-274, app.py:49-55
Description: `criar_pedido` dispara "ENVIANDO EMAIL/SMS/PUSH" e `atualizar_status_pedido` dispara notificações de aprovado/cancelado dentro do controller; a lista `categorias_validas` (regra de domínio) está inline no handler; `health_check` faz quatro queries direto no controller; `reset_database` executa os `DELETE` dentro da rota.
Impact: Notificações e contagens só podem ser exercitadas por HTTP e não são reutilizáveis; qualquer outro ponto que crie pedidos teria de copiar o bloco.
Recommendation: Mover as notificações para `services/notificacao_service.py` (`pedido_criado`, `status_alterado`), chamado pelo `pedido_service`, registrando via `logging` com o mesmo texto; mover as contagens do health para `models/sistema_model.py` e os `DELETE` do reset para `models/admin_model.py`; mover as categorias válidas para constante no model de produto. Controllers só leem a requisição, validam, chamam service/model e respondem. Respostas não mudam.
Verification: `grep -n "execute\|cursor" controllers/ routes/ app.py` → nenhuma ocorrência; `grep -n "ENVIANDO\|NOTIFICAÇÃO" controllers/` → nenhuma; smoke test de `POST /pedidos` e `PUT /pedidos/<id>/status` inalterado.

### [HIGH] Camadas misturadas ou responsabilidade no lugar errado
File: models.py:256-262, models.py:137-146, database.py:7-84
Description: `relatorio_vendas` (camada de dados) decide as faixas de desconto de 10%/5%/2%; `criar_pedido` no model valida estoque e calcula o total antes do INSERT; `get_db` cria as tabelas e faz o seed dentro da função que abre a conexão.
Impact: Mudar a política de desconto ou a regra de estoque exige mexer no SQL; testar a regra exige banco; cada abertura de conexão carrega a responsabilidade de migrar e popular o banco.
Recommendation: Mover o cálculo de desconto para `services/relatorio_service.py` (o model só devolve contagens e somas); mover a validação de estoque e o cálculo do total para `services/pedido_service.py` (o model só grava); mover schema e seed para `database/schema.py` (`init_db`), chamado uma vez em `create_app()`. Respostas não mudam.
Verification: `grep -n "desconto\|0.1\|0.05" models/` → nenhuma ocorrência; `grep -n "CREATE TABLE" database/connection.py` → nenhuma; `GET /relatorios/vendas` (admin) idêntico ao original.

### [HIGH] Estado global mutável
File: database.py:4-10
Description: `db_connection` é variável de módulo alterada com `global db_connection` e aberta com `check_same_thread=False`: uma única conexão sqlite3 compartilhada por todas as requisições e threads.
Impact: Requisições concorrentes usam o mesmo cursor e a mesma transação; escritas pendentes de uma requisição que falhou são gravadas pelo `commit` de outra; comportamento depende do histórico do processo.
Recommendation: Conexão por requisição em `database/connection.py`, guardada em `flask.g`, aberta com o `DATABASE_PATH` da config e fechada em `teardown_appcontext`; remover a variável global e o `check_same_thread=False`. Respostas não mudam.
Verification: `grep -n "global\|check_same_thread" database/` → nenhuma ocorrência; smoke test completo inalterado.

### [HIGH] Operação com várias escritas sem transação
File: models.py:148-168, models.py:65-70
Description: `criar_pedido` faz INSERT em `pedidos`, INSERT em `itens_pedido` e UPDATE de estoque por item sem rollback: uma exceção no meio deixa as escritas pendentes na conexão global; o estoque é checado num SELECT e baixado depois, sem condição. `deletar_produto` apaga o produto sem tratar `itens_pedido`, que ficam órfãos e passam a aparecer como `"Desconhecido"` nos pedidos. Severidade elevada de MEDIUM para HIGH por ser caminho de dinheiro.
Impact: Uma falha no meio gera pedido sem itens ou estoque baixado pela metade, e esse estado parcial é gravado pelo próximo commit de qualquer requisição; dois pedidos simultâneos passam na checagem e deixam estoque negativo; apagar um produto vendido apaga o nome dele do histórico de pedidos.
Recommendation: Em `pedido_model.criar`, gravar pedido, itens e baixa de estoque numa única transação (`with db:`, rollback em erro); a baixa vira `UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?` e, se nenhuma linha for afetada, a transação é desfeita com a mesma resposta `"Estoque insuficiente para <nome>"`. Itens de pedido são histórico lido por outras rotas: `DELETE /produtos/<id>` passa a responder 409 `{"erro": "Produto possui pedidos registrados"}` enquanto houver itens que o referenciam; sem itens, apaga como antes; checagem e exclusão na mesma transação.
Verification: `DELETE /produtos/<id>` de produto já pedido → 409 e `GET /pedidos` continua mostrando o nome; `DELETE` de produto sem pedidos → 200; revisão do código: escritas do pedido dentro de um único `with db:`.

### [HIGH] Validação de entrada ausente ou incompleta
File: controllers.py:26-50, controllers.py:66-90, controllers.py:118-121, controllers.py:148-158, controllers.py:169-174, controllers.py:190-201, controllers.py:239-245, models.py:139-146
Description: `preco`/`estoque` sem checagem de tipo (`"preco": "abc"` → `TypeError` → 500); `nome` não checado como texto; `float(preco_min)` lança `ValueError` → 500; `login` e `atualizar_status_pedido` fazem `dados.get` com corpo ausente → 500; `criar_pedido` aceita `quantidade` zero ou negativa, `produto_id` ausente (KeyError → 500) e `usuario_id` inexistente; `atualizar_status_pedido` responde 200 para pedido que não existe; `criar_usuario` aceita email repetido. Severidade elevada de MEDIUM para HIGH: `quantidade` negativa grava pedido de total negativo e aumenta o estoque.
Impact: Um cliente cria pedido com `"quantidade": -5`, reduzindo o faturamento e repondo estoque fictício; entradas mal formadas viram 500 com detalhes internos; emails duplicados tornam o login ambíguo.
Recommendation: Criar `controllers/validacao.py` e validar antes de qualquer escrita, mantendo mensagens e status existentes. Passam a ser recusados: `POST/PUT /produtos` com `nome` não-texto → 400 "Nome é obrigatório", `preco` não numérico (bool excluído) → 400 "Preço inválido", `estoque` não inteiro → 400 "Estoque inválido", `descricao`/`categoria` não-texto → 400 "Dados inválidos"; `GET /produtos/busca` com `preco_min`/`preco_max` não numéricos → 400 "Parâmetro preco_min inválido"/"Parâmetro preco_max inválido"; `POST /login` sem corpo ou corpo não-objeto → 400 "Email e senha são obrigatórios"; `POST /usuarios` com campos não-texto → 400 "Nome, email e senha são obrigatórios" e email já cadastrado → 409 "Email já cadastrado"; `POST /pedidos` com `usuario_id` não inteiro positivo → 400 "Usuario ID é obrigatório", usuário inexistente → 400 "Usuário não encontrado", item sem `produto_id` inteiro positivo ou `quantidade` inteira ≥ 1 → 400 "Itens inválidos"; `PUT /pedidos/<id>/status` sem corpo → 400 "Status inválido" e pedido inexistente → 404 "Pedido não encontrado".
Verification: `POST /pedidos` com `"quantidade": -5` → 400 e estoque inalterado; `POST /produtos {"preco":"abc",...}` → 400 (antes 500); `GET /produtos/busca?preco_min=abc` → 400; `PUT /pedidos/999/status` → 404; `POST /usuarios` com `joao@email.com` → 409; `POST /login` sem corpo → 400.

### [MEDIUM] Queries N+1
File: models.py:186-199, models.py:219-231, models.py:154-156
Description: `get_pedidos_usuario` e `get_todos_pedidos` fazem, para cada pedido, um SELECT em `itens_pedido` (`cursor2`) e, para cada item, um SELECT do nome do produto (`cursor3`); `criar_pedido` relê o preço de cada produto que já tinha lido no laço anterior.
Impact: Listar 100 pedidos de 3 itens faz ~400 queries; `GET /pedidos` degrada linearmente com o histórico da loja.
Recommendation: Uma única query `pedidos LEFT JOIN itens_pedido LEFT JOIN produtos` com `ORDER BY p.id, i.id` e `COALESCE(pr.nome, 'Desconhecido')`, agrupada em memória, com filtro opcional por `usuario_id`; em `criar_pedido`, buscar os produtos uma vez (`WHERE id IN (...)`) e reaproveitar o preço. Respostas não mudam (mesma ordem e valores padrão).
Verification: Revisão do código: nenhum `execute` dentro de laço em `models/pedido_model.py`; `GET /pedidos` e `GET /pedidos/usuario/<id>` idênticos ao original no smoke test.

### [MEDIUM] Tratamento de erro local, repetido ou engolido
File: controllers.py:6-12, controllers.py:15-22, controllers.py:60-62, controllers.py:218-220, controllers.py:291-292, app.py:68-78 (+12 blocos iguais em controllers.py)
Description: Os 16 handlers de `controllers.py` e `executar_query` repetem `try: ... except Exception as e: return jsonify({"erro": str(e)}), 500`; não existe `errorhandler` central.
Impact: Cada handler novo precisa copiar o bloco; erros de programação viram 500 sem registro em log e com detalhes internos para o cliente.
Recommendation: Criar `middlewares/erros.py` (exceções de domínio `ErroValidacao` 400, `ErroRegraNegocio` 400, `ErroNaoEncontrado` 404, `ErroNaoAutenticado` 401, `ErroAcessoNegado` 403, `ErroConflito` 409, carregando campos extras como `"sucesso": False` onde o original os tinha) e `middlewares/error_handler.py` com `@app.errorhandler`: exceções de domínio viram `{"erro": ...}` com o status delas; `HTTPException` segue o padrão do Flask; qualquer outra é registrada com `logger.exception` e devolve 500 `{"erro": "Erro interno do servidor"}`. Remover todos os `try/except` genéricos dos controllers.
Verification: `grep -n "except Exception" controllers/ routes/` → nenhuma ocorrência; erros 400/404 do smoke test com corpo e status originais.

### [MEDIUM] Código duplicado
File: models.py:12-21, models.py:31-40, models.py:304-313, models.py:79-86, models.py:95-102, models.py:171-201, models.py:203-233, controllers.py:28-50, controllers.py:72-90
Description: O mapeamento linha→dicionário de produto aparece três vezes e o de usuário duas; `get_pedidos_usuario` e `get_todos_pedidos` são cópias que diferem só pelo `WHERE`; a validação de `atualizar_produto` copia a de `criar_produto` mas perdeu as checagens de tamanho de `nome` e de `categoria` válida.
Impact: `PUT /produtos/<id>` grava nome de 1 caractere e categorias inexistentes que `POST` recusa; cada correção nos mapeamentos precisa ser repetida em todas as cópias.
Recommendation: Extrair `_para_dict` em cada model; unificar as duas listagens de pedidos numa função com `usuario_id` opcional; uma única função `validar_produto` usada em criação e atualização, com a regra mais rígida — `PUT /produtos/<id>` passa a responder 400 "Nome muito curto", "Nome muito longo" e "Categoria inválida. Válidas: [...]" como o `POST`.
Verification: `PUT /produtos/1 {"nome":"X","preco":1,"estoque":1}` → 400 "Nome muito curto" (antes 200); `PUT` com `"categoria":"xyz"` → 400; revisão do código: um único mapeamento por entidade.

### [LOW] Magic numbers e strings
File: models.py:257-262, controllers.py:47-50, controllers.py:52, controllers.py:242, models.py:150, app.py:36, controllers.py:285, app.py:85, app.py:88
Description: Faixas `10000/0.1`, `5000/0.05`, `1000/0.02`; limites de nome `2` e `200`; listas de categorias e de status inline; status inicial `'pendente'` no SQL; versão `"1.0.0"` repetida em dois lugares; porta `5000` literal.
Impact: As regras de desconto, cadastro e transição de status não têm nome e precisam ser procuradas e alteradas em vários pontos.
Recommendation: Constantes `FAIXAS_DESCONTO` (relatorio_service), `NOME_MIN`/`NOME_MAX`/`CATEGORIAS_VALIDAS` (produto_model), `STATUS_VALIDOS`/`STATUS_INICIAL` (pedido_model), `VERSAO_API` e porta em config. Respostas não mudam.
Verification: `grep -nE "10000|0\.05|\"aprovado\", \"enviado\"" ` fora das definições de constante → nenhuma ocorrência.

### [LOW] Nomenclatura ruim
File: controllers.py:14, controllers.py:56, controllers.py:64, controllers.py:98, controllers.py:136, controllers.py:160, models.py:24, models.py:54, models.py:65, models.py:89, models.py:187, models.py:191-193
Description: `id` sombreia o built-in como parâmetro e variável em vários handlers e funções de model; `cursor2`, `cursor3`, `prod` são nomes numerados/abreviados.
Impact: É preciso ler a implementação para saber de qual entidade cada `id` é, e o built-in `id()` fica inacessível nessas funções.
Recommendation: Renomear para `produto_id`, `usuario_id`, `novo_id` nos parâmetros internos e nos nomes de variável da rota; `cursor2`/`cursor3`/`prod` desaparecem com a query única do finding N+1. Caminhos, campos e respostas não mudam.
Verification: `grep -nwE "def \w+\(id\)|\bid = |cursor[23]" ` no código novo → nenhuma ocorrência.

### [LOW] `print` como log
File: app.py:56, app.py:83-86, controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:61, controllers.py:106, controllers.py:161, controllers.py:179, controllers.py:182, controllers.py:208-210, controllers.py:219, controllers.py:248, controllers.py:250
Description: 18 chamadas `print`, incluindo a simulação de envio de email, SMS e push em `criar_pedido` e as notificações de status.
Impact: Sem nível nem destino configurável, os avisos de pedido se misturam ao ruído do servidor e não podem ser filtrados ou desligados.
Recommendation: Trocar todos os `print` por `logging` (`logger = logging.getLogger(__name__)`, configurado no entry point); notificações saem pelo `notificacao_service` com o mesmo texto em nível INFO; erros inesperados via `logger.exception` no handler central; banners de boot viram `logger.info`. Respostas não mudam.
Verification: `grep -rn "print(" --include=*.py .` fora de `.claude/` e `.venv/` → nenhuma ocorrência.

### [LOW] Código morto e ruído
File: models.py:2, database.py:2, controllers.py:268, controllers.py:200, models.py:63, models.py:70, models.py:283
Description: `import sqlite3` em models.py e `import os` em database.py nunca usados; `cursor.execute("SELECT 1")` no health descartado; `if not itens or len(itens) == 0` redundante; `return True` de `atualizar_produto`, `deletar_produto`, `atualizar_status_pedido` nunca lido.
Impact: Imports e retornos sugerem dependências e contratos que não existem e aumentam o custo de leitura.
Recommendation: Remover os imports sem uso, o `SELECT 1`, a condição redundante (`if not itens`) e os `return True` não lidos. Respostas não mudam.
Verification: `python -W default -c "import app"` sem avisos; revisão do código: nenhum import sem uso nos módulos novos.

================================
Total: 19 findings
================================
```
