# Auditoria de arquitetura — code-smells-project

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python (versão não declarada no projeto; a .venv local usa 3.14.4)
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Database:      SQLite via sqlite3 (stdlib), sem ORM — arquivo local loja.db, conexão global única
Domain:        API de e-commerce (produtos, usuários, pedidos, itens de pedido, relatório de vendas)
Architecture:  Camadas nominais — 4 arquivos com nome de camada, mas cada um atende todos os domínios e mistura rotas, regra, SQL, schema e seed
Entry point:   app.py (python app.py), porta 5000
Source files:  4 files analyzed | ~780 lines of code
Endpoints:     19 routes
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 6 | HIGH: 6 | MEDIUM: 4 | LOW: 4
Deprecated APIs: none detected

## Findings

### [CRITICAL] Operação perigosa exposta sem proteção
File: app.py:59-78, app.py:47-57, app.py:8, app.py:88
Description: `executar_query` (POST /admin/query) passa o campo `sql` do corpo direto para `cursor.execute(query)` e faz commit. `reset_database` (POST /admin/reset-db) apaga as quatro tabelas. Nenhuma das duas verifica identidade. O modo debug está fixo em `app.config["DEBUG"] = True` e em `app.run(host="0.0.0.0", port=5000, debug=True)`.
Impact: Qualquer cliente anônimo na rede lê, altera ou apaga o banco inteiro com uma requisição; com o debugger do Werkzeug exposto em 0.0.0.0, um erro não tratado abre console interativo no servidor.
Recommendation: Remover /admin/query. Proteger /admin/reset-db com token de administrador lido do ambiente, negando acesso quando o token não está configurado. Ler debug e host da configuração, com debug desligado por padrão.

### [CRITICAL] Injeção por query montada com dados de entrada
File: models.py:109-111, models.py:289-299, models.py:47-50, models.py:57-61, models.py:126-129, models.py:140, models.py:148-151, models.py:155, models.py:157-161, models.py:163-166 (+9 ocorrências no mesmo arquivo: 28, 68, 92, 174, 188, 192, 220, 224, 279-281)
Description: As 19 queries com parâmetro de `models.py` são montadas por concatenação. `login_usuario` concatena `email` e `senha` no WHERE; `buscar_produtos` concatena `termo` e `categoria` da query string com `query +=`; `criar_produto`, `atualizar_produto` e `criar_usuario` concatenam strings do corpo; `criar_pedido` concatena `usuario_id`, `item["produto_id"]` e `item["quantidade"]` do JSON sem checar tipo.
Impact: `POST /login` com email `' OR '1'='1' --` autentica como o primeiro usuário (o Admin) sem senha; `GET /produtos/busca?q=` permite ler a tabela `usuarios` via UNION; um nome com apóstrofo (ex.: "Caixa d'água") quebra o INSERT com erro 500.
Recommendation: Trocar todas as queries por placeholders `?` com os valores passados em tupla, inclusive o filtro dinâmico de busca (lista de condições + lista de parâmetros).

### [CRITICAL] Exposição de dados sensíveis
File: models.py:83, models.py:99, controllers.py:285-289, controllers.py:12, 22, 62 (+13 ocorrências no mesmo arquivo), app.py:78
Description: `get_todos_usuarios` e `get_usuario_por_id` incluem `"senha": row["senha"]` no dicionário devolvido por GET /usuarios e GET /usuarios/<id>. `health_check` devolve `secret_key`, `db_path`, `debug` e `ambiente`. Os 16 handlers de `controllers.py` e `executar_query` devolvem `str(e)` ao cliente.
Impact: Qualquer cliente lista as senhas de todos os usuários e obtém a SECRET_KEY em GET /health; as mensagens de exceção revelam o SQL e a estrutura das tabelas, o que facilita a injeção.
Recommendation: Serializar usuário sem o campo `senha`; reduzir /health a status, banco e contagens; responder erros internos com mensagem genérica e registrar o detalhe só no log.

### [CRITICAL] Armazenamento inseguro de senhas
File: models.py:126-129, models.py:109-111, database.py:76-78
Description: `criar_usuario` grava `senha` como recebida; `login_usuario` compara com `AND senha = '<valor recebido>'`; o seed insere `admin123`, `123456` e `senha123` em texto puro.
Impact: Um vazamento do banco (trivial pelos findings acima) entrega todas as senhas prontas para uso, inclusive a do administrador.
Recommendation: Gravar hash com `werkzeug.security.generate_password_hash`, buscar o usuário por email e validar com `check_password_hash`; gerar o seed com hash e migrar as senhas legadas em texto puro no boot.

### [CRITICAL] Credenciais e segredos hardcoded
File: app.py:7, controllers.py:289
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` está no código versionado e a mesma string é repetida como literal na resposta de `health_check`.
Impact: Quem lê o repositório tem a chave que assina sessões e cookies do Flask; trocá-la exige alterar código em dois lugares.
Recommendation: Ler `SECRET_KEY` de variável de ambiente em um módulo de configuração, com valor aleatório gerado no boot quando ausente; documentar em `.env.example`.

### [CRITICAL] God Class ou God File
File: models.py:1-314, controllers.py:1-292, app.py:1-88
Description: `models.py` atende produtos, usuários, pedidos e relatórios em um arquivo só, somando SQL, regra de negócio (estoque, total, desconto) e serialização. `controllers.py` atende os mesmos quatro domínios mais o health check, com validação, notificação e SQL direto. `app.py` reúne configuração, registro das 19 rotas, dois handlers administrativos com SQL e o boot.
Impact: Não há como testar ou alterar um domínio isoladamente; toda mudança toca arquivos compartilhados por todos os fluxos.
Recommendation: Dividir por domínio e por camada: `models/` (acesso a dados), `services/` (regra), `controllers/` (HTTP), `routes/` (blueprints), `config/` e `database/`, com `app.py` só como composição.

### [HIGH] Autenticação ou autorização ausente
File: app.py:11-30, app.py:47, app.py:59, app.py:9, controllers.py:167-186
Description: Nenhuma das 19 rotas tem verificação de identidade. `login` devolve os dados do usuário sem emitir token ou sessão, então o login não protege nada. `CORS(app)` libera qualquer origem.
Impact: Qualquer cliente apaga produtos (DELETE /produtos/<id>), muda o status de qualquer pedido, lista pedidos e usuários de todos e cria pedidos em nome de outro `usuario_id`.
Recommendation: Proteger já as rotas administrativas com token. Autenticação por token nas demais rotas e restrição de origens no CORS mudam o contrato da API e precisam de decisão do time.

### [HIGH] Operação com várias escritas sem transação
File: models.py:148-168, models.py:65-70, app.py:51-55, database.py:36-53
Description: `criar_pedido` executa o INSERT do pedido e, por item, um INSERT em `itens_pedido` e um UPDATE de estoque, com um único `commit` na linha 168 e nenhum rollback; como a conexão é global, uma exceção no meio deixa escritas pendentes que o `commit` da próxima requisição grava. `deletar_produto` apaga o produto sem tratar `itens_pedido`, em schema sem chaves estrangeiras. Severidade elevada de MEDIUM para HIGH por estar no caminho de pedido, estoque e faturamento.
Impact: Pedido gravado sem itens ou com estoque baixado pela metade; itens órfãos aparecem como "Desconhecido" nas listagens.
Recommendation: Envolver a criação do pedido e o reset em transação com rollback em caso de erro (`with conexao:`); decidir a regra para exclusão de produto com pedidos.

### [HIGH] Camadas misturadas ou responsabilidade no lugar errado
File: models.py:139-146, models.py:256-262, models.py:143, models.py:145, database.py:14-84, app.py:47-78
Description: `models.criar_pedido` valida estoque e calcula o total dentro da função que faz os INSERTs e sinaliza erro de negócio devolvendo `{"erro": ...}`. `models.relatorio_vendas` aplica as faixas de desconto. `get_db` cria as quatro tabelas e insere o seed dentro da função que abre a conexão. Os handlers administrativos vivem no entry point.
Impact: A regra de pedido e de desconto só pode ser exercitada com banco real; o controller precisa inspecionar `"erro" in resultado` para saber se deu certo.
Recommendation: Mover validação de estoque, cálculo de total e desconto para services, com exceções de domínio; separar conexão, schema e seed em funções próprias; mover os handlers administrativos para controller e rota próprios.

### [HIGH] Regra de negócio no controller ou na rota
File: controllers.py:266-274, controllers.py:208-210, controllers.py:247-250, app.py:49-55, app.py:66-76
Description: `health_check` abre cursor e executa quatro SELECTs. `criar_pedido` e `atualizar_status_pedido` disparam as notificações (email, SMS, push, aprovação, cancelamento) dentro do handler; a de cancelamento anuncia "Devolver estoque" e nenhum código devolve. `reset_database` e `executar_query` executam SQL na função de rota.
Impact: Efeitos de negócio ficam presos ao HTTP e não são reutilizáveis nem testáveis; a devolução de estoque no cancelamento parece existir e não existe.
Recommendation: Mover contagens para models, notificações para um service de notificação chamado pelo service de pedidos, e deixar nos controllers só leitura da requisição, chamada ao service e resposta.

### [HIGH] Estado global mutável
File: database.py:4, database.py:8-10
Description: `db_connection` é variável de módulo alterada com `global` em `get_db` e compartilhada por todas as requisições com `check_same_thread=False`.
Impact: Requisições concorrentes dividem a mesma conexão e a mesma transação: o commit de uma grava escritas pendentes de outra, e testes dependem da ordem de execução.
Recommendation: Abrir uma conexão por requisição guardada em `flask.g`, fechada em `teardown_appcontext`, com o caminho do banco vindo da configuração.

### [HIGH] Acoplamento forte, sem injeção de dependência
File: models.py:1, models.py:5, 25, 44 (+12 ocorrências no mesmo arquivo), controllers.py:2-3, app.py:3-4
Description: As 15 funções de `models.py` chamam `get_db()` por conta própria e a regra de pedido opera direto sobre o cursor do sqlite3. `controllers.py` importa o módulo `models` inteiro e também `get_db`; `app.py` importa `get_db` para os handlers administrativos.
Impact: Não há como testar regra de negócio sem o arquivo `loja.db` real, nem trocar a persistência sem editar todas as funções.
Recommendation: Models recebem a conexão como parâmetro ou pelo contexto da requisição; services recebem os models; a ligação é feita na composição da aplicação.

### [MEDIUM] Validação de entrada ausente ou incompleta
File: controllers.py:169-171, controllers.py:239-245, controllers.py:43-50, controllers.py:81-90, controllers.py:118-121, controllers.py:153-160, controllers.py:195-203, models.py:140-146
Description: `login` e `atualizar_status_pedido` chamam `dados.get` sem tratar corpo ausente, e o segundo não verifica se o pedido existe (responde 200 para id inexistente). `criar_produto` compara `preco < 0` e `len(nome)` sem checar tipo. `atualizar_produto` não valida tamanho do nome nem categoria, ao contrário da criação. `buscar_produtos` faz `float(preco_min)` sem tratamento. `criar_usuario` não valida formato nem unicidade do email. `criar_pedido` não verifica se o usuário existe, acessa `item["produto_id"]` e `item["quantidade"]` sem checar presença e aceita quantidade negativa.
Impact: Entradas inválidas viram erro 500; quantidade negativa aumenta o estoque e gera pedido com total negativo; emails duplicados e categorias inválidas são gravados.
Recommendation: Centralizar a validação por entidade (presença, tipo, faixa), reutilizada em criação e atualização, respondendo 400 com mensagem clara; verificar existência de usuário e pedido.

### [MEDIUM] Queries N+1
File: models.py:177-200, models.py:209-232, models.py:139-141, models.py:154-156
Description: `get_pedidos_usuario` e `get_todos_pedidos` executam, para cada pedido, um SELECT em `itens_pedido` e, para cada item, um SELECT do nome do produto. `criar_pedido` consulta cada produto duas vezes, uma no laço de validação e outra para reler o preço.
Impact: GET /pedidos com 100 pedidos de 3 itens faz 401 queries; o tempo de resposta cresce com o volume de vendas.
Recommendation: Buscar os itens de todos os pedidos em uma query com JOIN em `produtos` e `IN (...)`, agrupando em memória; reaproveitar no INSERT os produtos já carregados na validação.

### [MEDIUM] Tratamento de erro local, repetido ou engolido
File: controllers.py:10-12, controllers.py:21-22, controllers.py:60-62 (+13 ocorrências no mesmo arquivo), app.py:77-78
Description: O mesmo `except Exception as e: return jsonify({"erro": str(e)}), 500` está copiado nos 16 handlers de `controllers.py` e em `executar_query`; só três deles registram o erro, com `print`. Não existe `errorhandler` central. O `except Exception` também captura os erros HTTP do Flask, então JSON malformado ou Content-Type errado respondem 500.
Impact: A maioria dos erros de programação some sem registro, erros do cliente aparecem como 500 e cada handler novo precisa repetir o bloco.
Recommendation: Remover os try/except dos handlers e registrar handlers centrais para exceções de domínio, `HTTPException` e `Exception`, com log e resposta padronizada.

### [MEDIUM] Código duplicado
File: models.py:12-21, models.py:31-40, models.py:304-313, models.py:79-86, models.py:95-102, models.py:177-200, models.py:209-232, controllers.py:28-46, controllers.py:72-90
Description: O mapeamento de linha de produto para dicionário aparece três vezes e o de usuário duas. O bloco que monta pedido com itens é idêntico em `get_pedidos_usuario` e `get_todos_pedidos`, que diferem só pelo filtro. A validação de `criar_produto` é repetida em `atualizar_produto` e já divergiu (a atualização não valida nome nem categoria).
Impact: Cada correção precisa ser feita em todas as cópias; a divergência entre criação e atualização já permite gravar dados que a criação rejeitaria.
Recommendation: Extrair um serializador por entidade, uma função única de listagem de pedidos com filtro opcional e uma validação de produto compartilhada.

### [LOW] Magic numbers e strings
File: models.py:257-262, controllers.py:47-49, controllers.py:52, controllers.py:242, models.py:247, models.py:250, models.py:253, controllers.py:41, controllers.py:85, app.py:36, controllers.py:285, app.py:88
Description: Faixas de desconto (10000/0.1, 5000/0.05, 1000/0.02), limites de nome (2 e 200), lista de categorias e lista de status escritas inline; status `'pendente'`, `'aprovado'`, `'cancelado'` e categoria `"geral"` repetidos; versão `"1.0.0"` em dois arquivos; host e porta fixos em `app.run`.
Impact: As regras de negócio não têm nome e precisam ser alteradas em vários pontos.
Recommendation: Constantes nomeadas por domínio (faixas de desconto, status, categorias, limites) e host, porta e versão na configuração.

### [LOW] `print` ou `console.log` como log
File: controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250, app.py:56, app.py:83-86
Description: 19 chamadas a `print` fazem o papel de log, incluindo o "envio" de email, SMS e push simulado em `criar_pedido` e as notificações de status.
Impact: Sem nível, formato nem destino configurável; erros e eventos de negócio se perdem na saída padrão.
Recommendation: Usar o módulo `logging` com logger por módulo e nível adequado; isolar as notificações simuladas em um service próprio.

### [LOW] Nomenclatura ruim
File: controllers.py:14, 56, 64, 98, 136, 160, models.py:24, 54, 65, 89, models.py:187, 191, 219, 223, models.py:9, 77, 176, 208, 301
Description: `id` sombreia o built-in como parâmetro ou variável em dez pontos; `cursor2` e `cursor3` são nomes numerados; `result` é usado como nome genérico para listas de produtos, usuários e pedidos.
Impact: É preciso ler a implementação para saber o que cada nome guarda, e o built-in `id` fica inacessível nessas funções.
Recommendation: Renomear para `produto_id`, `usuario_id`, `produtos`, `pedidos`; os nomes numerados somem com a correção do N+1.

### [LOW] Código morto e ruído
File: database.py:2, models.py:2, models.py:122, models.py:63, models.py:70, models.py:283, controllers.py:268, controllers.py:200, models.py:146
Description: `import os` e `import sqlite3` não são usados; o parâmetro `tipo` de `criar_usuario` nunca é passado por nenhum chamador; os `return True` de `atualizar_produto`, `deletar_produto` e `atualizar_status_pedido` são ignorados; `SELECT 1` em `health_check` é redundante com as contagens seguintes; `not itens or len(itens) == 0` repete a mesma checagem; `total = total + ...` em vez de `+=`.
Impact: Sugere dependências e comportamentos que não existem e aumenta o custo de leitura.
Recommendation: Remover imports, parâmetros e retornos sem uso e simplificar as construções redundantes durante a refatoração.

================================
Total: 20 findings
================================
```
