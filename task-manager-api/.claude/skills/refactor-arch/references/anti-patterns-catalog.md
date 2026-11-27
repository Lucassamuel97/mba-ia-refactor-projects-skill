# Catálogo de anti-patterns (Fase 2)

Vinte e dois anti-patterns de arquitetura, segurança e qualidade, com os sinais que os denunciam no código e a severidade de cada um. Na Fase 2, percorra o catálogo inteiro contra o código lido na Fase 1: cada entrada é uma pergunta a responder com "não ocorre" ou com uma lista de arquivos e linhas.

Os sinais são descritos pelo comportamento do código, com exemplos em mais de uma linguagem. Em uma stack que não aparece nos exemplos, procure o equivalente: o que importa é o que o código faz, não a sintaxe.

## Conteúdo

- [Escala de severidade](#escala-de-severidade)
- [Como registrar um finding](#como-registrar-um-finding)
- [CRITICAL](#critical): AP-01 a AP-06
- [HIGH](#high): AP-07 a AP-11
- [MEDIUM](#medium): AP-12 a AP-18
- [LOW](#low): AP-19 a AP-22
- [APIs deprecated conhecidas](#apis-deprecated-conhecidas)

## Escala de severidade

| Severidade | Critério |
|---|---|
| CRITICAL | Falha grave de arquitetura ou segurança: impede o funcionamento correto, expõe dados sensíveis ou viola por completo a separação de responsabilidades |
| HIGH | Forte violação de MVC ou SOLID, que dificulta muito a manutenção e os testes |
| MEDIUM | Problema de padronização, duplicação ou gargalo moderado de performance |
| LOW | Legibilidade, nomenclatura, magic numbers |

A severidade de cada entrada é o padrão. Ajuste quando o contexto mudar o impacto, e diga o motivo na descrição do finding:

- Suba um nível quando o problema está em um caminho de dinheiro, autenticação ou dados pessoais, ou quando foi comprovado que é explorável.
- Desça um nível quando o trecho é código morto, script de desenvolvimento ou seed.

## Como registrar um finding

- **Um finding por anti-pattern**, com todas as ocorrências listadas em `File:`. Vinte queries concatenadas são um finding de SQL injection com vinte locais, não vinte findings.
- **Arquivo e linha exatos.** Confirme cada linha relendo o arquivo com números de linha (`grep -n`, `cat -n`) imediatamente antes de escrever o relatório, numerando um arquivo por vez. Linha citada de memória, ou contada sobre vários arquivos concatenados, costuma estar errada.
- **Evidência concreta.** A descrição diz o que o código faz naquele ponto, com o nome real da função, variável ou valor. "Código de baixa qualidade" não é um finding.
- **Só o que está no código.** Se um sinal não aparece, o anti-pattern não entra no relatório. Não invente ocorrências para preencher uma severidade.
- **Recommendation executável.** A Recommendation vem da transformação do playbook indicada em cada entrada abaixo e é o escopo exato da Fase 3: ações completas, sem alternativas. Ela elimina cada consequência descrita no Impact do finding e vem com a linha `Verification` (veja o template).

---

## CRITICAL

### AP-01 — Injeção por query montada com dados de entrada

**Sinais de detecção:**

- Query SQL construída por concatenação, interpolação ou formatação de string com valores que vêm da requisição: `"... WHERE id = " + str(id)`, `f"SELECT ... {nome}"`, `"...%s" % valor`, `` `SELECT ... ${id}` ``, `"...".format(x)`, `String.format`.
- Query dinâmica montada em partes (`query += " AND campo = '" + valor + "'"`).
- O mesmo padrão com comandos de shell (`os.system`, `subprocess` com `shell=True`, `child_process.exec`), `eval`/`exec`, filtros NoSQL montados a partir do corpo da requisição.

**Não confundir com:** query com placeholders (`?`, `%s`, `$1`, `:nome`) e os valores passados à parte; identificadores fixos concatenados (nome de tabela vindo de uma constante).

**Impacto:** quem controla a entrada controla a query: lê, altera ou apaga dados e contorna autenticação.

**Transformação:** T-01

### AP-02 — Credenciais e segredos hardcoded

**Sinais de detecção:**

- Literais atribuídos a nomes como `SECRET_KEY`, `password`, `passwd`, `senha`, `token`, `api_key`, `apiKey`, `private_key`, `dbPass`, `smtp_password`.
- Strings com formato de credencial: prefixos `sk_`, `pk_live_`, `AKIA`, `ghp_`, `Bearer `, connection strings com usuário e senha.
- Segredos em arquivos versionados de configuração, em seeds ou em valores padrão de `os.environ.get("X", "valor-real")`.

**Não confundir com:** nomes de campos de formulário, dados fictícios de seed (esses caem em AP-05 se forem senhas guardadas sem hash), valores padrão não sensíveis (porta, nome de banco local).

**Impacto:** quem lê o repositório tem as credenciais; trocar um segredo exige alterar código e republicar.

**Transformação:** T-02

### AP-03 — God Class ou God File

**Sinais de detecção:**

- Uma classe, módulo ou arquivo que reúne três ou mais naturezas de responsabilidade: roteamento, regra de negócio, acesso a dados, configuração, criação de schema.
- Nomes genéricos que denunciam o acúmulo: `Manager`, `Handler`, `Utils`, `Helper`, `main`, `server`.
- Um arquivo único de "models" ou "controllers" atendendo todos os domínios da aplicação.
- Métodos com mais de ~50 linhas que validam, consultam, calculam e respondem.

**Impacto:** nada pode ser testado ou alterado em isolamento; qualquer mudança arrisca todos os fluxos.

**Transformação:** T-03

### AP-04 — Exposição de dados sensíveis

**Sinais de detecção:**

- Senha, hash de senha, token ou chave incluídos na serialização de resposta (`to_dict`, `toJSON`, `SELECT *` devolvido direto, objeto do ORM serializado inteiro).
- Log ou `print` com senha, número de cartão, token, chave de API ou corpo completo da requisição.
- Endpoint de status ou health que devolve configuração interna (chave, caminho do banco, variáveis de ambiente).
- Mensagem de exceção interna ou stack trace devolvidos ao cliente (`return str(e)`, `res.send(err.stack)`).

**Impacto:** vazamento direto de credenciais e de detalhes que facilitam outros ataques.

**Transformação:** T-04

### AP-05 — Armazenamento inseguro de senhas

**Sinais de detecção:**

- Senha gravada ou comparada em texto puro (`WHERE senha = ?` com o valor recebido, seed com senhas legíveis).
- Hash rápido e sem salt: `md5`, `sha1`, `sha256` aplicados direto sobre a senha.
- Função caseira de "criptografia" (base64, XOR, repetição de caracteres, truncamento).
- Senha padrão atribuída quando o usuário não informa uma.

**Não confundir com:** uso de KDF próprio para senhas (`bcrypt`, `scrypt`, `argon2`, `PBKDF2`, `werkzeug.security`).

**Impacto:** um vazamento do banco entrega todas as senhas; hashes rápidos são revertidos por tabelas prontas.

**Transformação:** T-05

### AP-06 — Operação perigosa exposta sem proteção

**Sinais de detecção:**

- Rota que executa SQL, comando ou código recebido na requisição.
- Rota que apaga ou reinicia dados em massa (reset de banco, truncate) sem autenticação.
- Modo debug ligado de forma fixa (`debug=True`, `app.run(debug=True)`, `DEBUG = True`), em especial com bind em `0.0.0.0`: um erro não tratado expõe console interativo e código-fonte.
- Rotas com prefixo `admin`, `internal`, `debug` sem nenhuma verificação de identidade.

**Impacto:** controle total do banco ou do servidor por qualquer cliente anônimo.

**Transformação:** T-06. Rota que executa SQL, comando ou código recebido na requisição é removida, porque não tem versão segura; as demais operações destrutivas ficam atrás de credencial de administrador (o papel de admin do T-17 quando o projeto tem login; `ADMIN_TOKEN` quando não tem); o debug vem da configuração, desligado por padrão.

---

## HIGH

### AP-07 — Regra de negócio no controller ou na rota

**Sinais de detecção:**

- Função de rota que, além de ler a requisição e responder, calcula valores, decide fluxos, aplica regras de domínio ou percorre coleções agregando resultados.
- Acesso a dados direto na função de rota: SQL, `Model.query`, `db.session`, `db.get(...)`.
- Funções de rota com mais de ~30 linhas ou com vários níveis de `if` aninhado sobre dados de domínio.
- Efeitos colaterais de negócio disparados na rota (notificação, baixa de estoque, cobrança).

**Não confundir com:** validação de formato da entrada e escolha do status code, que pertencem ao controller.

**Impacto:** a regra só pode ser exercitada por HTTP, não é reutilizável e se duplica entre rotas.

**Transformação:** T-07

### AP-08 — Camadas misturadas ou responsabilidade no lugar errado

**Sinais de detecção:**

- Camada de dados decidindo regra de negócio (faixas de desconto, validação de estoque, cálculo de totais dentro da função que faz o `INSERT`).
- Camada de dados ou de serviço importando objetos HTTP (`request`, `jsonify`, `res`) ou devolvendo respostas HTTP.
- Módulo que não pertence ao domínio do arquivo (CRUD de uma entidade dentro do arquivo de rotas de outra).
- Camada correta existente e ignorada: método de modelo, helper ou serviço que implementa a regra e nunca é chamado, enquanto a mesma lógica é reescrita em outro lugar.
- Schema e seed criados dentro da função que abre a conexão.

**Impacto:** a estrutura de pastas promete uma separação que o código não cumpre; trocar persistência ou testar regra exige mexer em tudo.

**Transformação:** T-07, T-03

### AP-09 — Estado global mutável

**Sinais de detecção:**

- Variável de módulo alterada em tempo de execução: `global conexao`, `let cache = {}` no topo do arquivo, contadores e acumuladores globais.
- Conexão de banco única criada no import e compartilhada por todas as requisições (`check_same_thread=False` é um forte indício).
- Cache global sem limite de tamanho nem expiração.
- Singleton acessado de qualquer lugar por import, em vez de recebido como dependência.
- Coleção guardada em atributo de um objeto que vive o processo todo (`self.notifications = []`, `this.cache = new Map()`) e que só cresce.

**Não confundir com:** constantes imutáveis de módulo; conexão única exigida por banco em memória, desde que criada na composição e injetada; coleção local dentro de uma função.

**Impacto:** requisições concorrentes interferem entre si, testes dependem da ordem de execução e o comportamento varia com o histórico do processo.

**Transformação:** T-08. Estado que ninguém lê é apagado junto com as escritas; estado que uma rota ou regra lê vai para o banco.

### AP-10 — Acoplamento forte, sem injeção de dependência

**Sinais de detecção:**

- Classe que instancia as próprias dependências no construtor (`this.db = new Database(...)`, `self.mailer = SMTP(...)`).
- Módulos que importam direto a implementação concreta de infraestrutura (driver de banco, cliente HTTP, gateway de pagamento) dentro da regra de negócio.
- Integração externa chamada de dentro do fluxo, sem uma interface que permita substituí-la.

**Impacto:** não há como testar a regra sem banco e serviços reais, nem trocar uma implementação sem editar quem a usa.

**Transformação:** T-08

### AP-11 — Autenticação ou autorização ausente

**Sinais de detecção:**

- Nenhum middleware, decorator ou guard de autenticação nas rotas.
- Token fixo ou previsível devolvido no login (`"fake-token-" + id`) e nunca verificado.
- Papel ou privilégio aceito do corpo da requisição (`role`, `is_admin`, `tipo`) sem conferir quem está pedindo.
- Rotas que alteram ou apagam recursos de qualquer usuário sem verificar o dono.
- Login que devolve os dados do usuário sem emitir credencial, de modo que nada depois dele consegue saber quem está pedindo.
- Identidade tirada do corpo ou da URL (`usuario_id` no corpo de um pedido) sem conferir com quem está autenticado.
- Guard que existe mas fica desligado por padrão (`AUTH_REQUIRED=false`) ou protege só parte das rotas que o finding cita.
- CORS aberto para qualquer origem combinado com os itens acima.

**Impacto:** qualquer cliente lê e altera dados de qualquer usuário e pode se promover a administrador.

**Transformação:** T-17, obrigatória. Autenticação e autorização das rotas citadas e o fim da escalação de privilégio são correção de segurança: entram na Recommendation e são aplicados nesta refatoração, mesmo mudando o contrato. Nunca ficam pendentes nem atrás de uma flag desligada.

---

## MEDIUM

### AP-12 — Queries N+1

**Sinais de detecção:**

- Query dentro de laço que percorre o resultado de outra query (`for order in orders: cursor.execute(...)`, `rows.forEach(r => db.get(...))`).
- Acesso a relacionamento lazy do ORM dentro de laço (`len(reader.loans)`, `loan.book.title`, `Model.query.get(x.fk_id)` por item).
- Contagem ou soma por item feita com uma query por item.

**Impacto:** o número de queries cresce com o volume de dados; uma listagem de 100 itens faz centenas de consultas.

**Transformação:** T-09

### AP-13 — Operação com várias escritas sem transação

**Sinais de detecção:**

- Dois ou mais `INSERT`/`UPDATE`/`DELETE` dependentes na mesma operação, sem transação nem rollback em caso de erro.
- `commit` chamado no meio de uma sequência de escritas.
- Callbacks encadeados em que cada escrita só acontece se a anterior responder, sem desfazer as anteriores em caso de falha.
- Exclusão de um registro pai sem tratar os filhos, em schema sem chaves estrangeiras.

**Impacto:** uma falha no meio deixa dados inconsistentes (compra sem itens, cobrança sem registro, registros órfãos).

**Transformação:** T-10. A exclusão de registro com dependentes segue a regra de T-10 (filhos apagados, referência anulada ou 409), e a Recommendation diz qual se aplica.

### AP-14 — Validação de entrada ausente ou incompleta

**Sinais de detecção:**

- Campos do corpo ou da query string usados sem checar presença, tipo ou faixa (`int(request.args[...])` sem tratamento, comparação numérica sobre valor que pode ser texto).
- Quantidades, preços ou ids aceitos negativos ou zero.
- Corpo ausente ou `null` não tratado antes de acessar chaves.
- Referências a outros registros (id de usuário, de categoria) gravadas sem verificar que existem.
- Unicidade esperada pela regra (email) sem verificação nem constraint.

**Impacto:** entradas inválidas viram erro 500 ou, pior, são gravadas e corrompem dados.

**Transformação:** T-11

### AP-15 — Tratamento de erro local, repetido ou engolido

**Sinais de detecção:**

- O mesmo `try/except` ou `try/catch` genérico copiado em cada handler.
- `except:` sem tipo, `except Exception: pass`, `catch (e) {}`.
- Parâmetro de erro de callback ignorado (`(err, row) => { usa row sem olhar err }`).
- Promise sem `catch`, ou handler assíncrono sem encaminhar o erro ao framework.
- Ausência de um handler de erro central (`errorhandler`, middleware de erro).

**Impacto:** erros de programação somem sem registro, o cliente recebe respostas inconsistentes e cada novo handler precisa repetir o mesmo bloco.

**Transformação:** T-12

### AP-16 — Código duplicado

**Sinais de detecção:**

- Blocos de 5 ou mais linhas quase idênticos em dois ou mais lugares (mapeamento de linha para dicionário, validação de criação repetida na atualização, a mesma regra de cálculo em várias rotas).
- Duas funções que diferem só por um filtro ou parâmetro.
- A mesma lista de valores válidos ou a mesma expressão regular escrita em vários arquivos.

**Impacto:** cada correção precisa ser repetida em todas as cópias, e elas divergem com o tempo.

**Transformação:** T-13

### AP-17 — API deprecated

**Sinais de detecção:**

- Uso de qualquer item da tabela [APIs deprecated conhecidas](#apis-deprecated-conhecidas).
- Avisos de depreciação que o projeto já documenta ou que aparecem em logs versionados.
- Dependência declarada em versão sem suporte, ou pacote oficialmente abandonado.

Como verificar além da tabela: compare a versão do runtime e das bibliotecas (levantadas na Fase 1) com o uso no código, e desconfie de qualquer API marcada como "legacy" na documentação da versão em uso. Na Fase 3, rodar a aplicação com avisos de depreciação ligados (`python -W default`, `node --trace-deprecation`) confirma os achados.

**Impacto:** a API some em uma versão futura do runtime ou da biblioteca e o projeto quebra na atualização; muitas vezes o substituto também corrige um defeito.

**Transformação:** T-14

### AP-18 — Fluxo assíncrono desestruturado

**Sinais de detecção:**

- Callback hell: três ou mais callbacks aninhados.
- Contadores manuais para saber quando callbacks paralelos terminaram.
- Mistura de callbacks, promises e `async/await` no mesmo fluxo.
- Ordem do resultado dependente de qual callback termina primeiro.

**Impacto:** tratamento de erro falho, respostas em ordem instável e fluxo difícil de seguir e de alterar.

**Transformação:** T-15

---

## LOW

### AP-19 — Magic numbers e strings

**Sinais de detecção:**

- Literais numéricos com significado de regra soltos em condições (`if total > 10000`, `priority <= 2`, `len(senha) < 4`).
- Listas de valores válidos escritas inline (`status in ["pendente", "aprovado"]`).
- Strings de status ou tipo repetidas pelo código (`"PAID"`, `"admin"`).
- Porta, host e limites fixos no meio da lógica.

**Impacto:** a regra fica escondida, sem nome, e precisa ser alterada em vários lugares.

**Transformação:** T-16

### AP-20 — Nomenclatura ruim

**Sinais de detecção:**

- Variáveis de uma ou duas letras fora de laços curtos (`u`, `e`, `p`, `cc`, `d`).
- Nomes numerados ou genéricos (`p1`, `data2`, `tmp`, `result`, `obj`).
- Nome que sombreia um built-in da linguagem (`id`, `type`, `list`, `filter`).
- Nome que não diz o que a função faz (`process`, `handle`, `doStuff`) ou que mente sobre o que ela faz.

**Não confundir com:** nomes de campos do contrato da API, que devem ser preservados mesmo que ruins.

**Impacto:** é preciso ler a implementação para entender o que cada nome guarda.

**Transformação:** T-16

### AP-21 — `print` ou `console.log` como log

**Sinais de detecção:**

- `print(...)`, `console.log(...)`, `System.out.println(...)`, `fmt.Println(...)` em código de aplicação.
- "Envio" de email, SMS ou notificação simulado por uma linha de log dentro do fluxo.

**Impacto:** não há nível, formato nem destino configurável; em produção o que importa se perde no ruído.

**Transformação:** T-16

### AP-22 — Código morto e ruído

**Sinais de detecção:**

- Imports não utilizados.
- Funções, métodos, constantes e variáveis nunca referenciados.
- Dependência declarada no manifesto e nunca importada.
- Construções verbosas sem ganho (`if x: return True else: return False`, `type(x) == list`, `i = i + 1` em linguagem com `+=`).

**Impacto:** sugere dependências e comportamentos que não existem e aumenta o custo de leitura.

**Transformação:** T-16. Serviço ou helper sem chamador é removido, salvo quando implementa uma regra hoje duplicada em outro lugar: então passa a ser usado (T-07, T-13).

---

## APIs deprecated conhecidas

Lista de partida para AP-17. Não é exaustiva; trate como exemplos do que procurar e confira a versão em uso.

### Python

| Deprecated | Desde | Use |
|---|---|---|
| `datetime.utcnow()`, `datetime.utcfromtimestamp()` | Python 3.12 | `datetime.now(timezone.utc)`, `datetime.fromtimestamp(ts, timezone.utc)` |
| `Model.query.get(id)`, `Query.get()` | SQLAlchemy 2.0 (legado) | `db.session.get(Model, id)` |
| `Model.query` e a API `Query` em geral | Flask-SQLAlchemy 3.x (legado) | `db.session.execute(db.select(Model)...)` |
| `from sqlalchemy.ext.declarative import declarative_base` | SQLAlchemy 2.0 | `from sqlalchemy.orm import declarative_base` ou `DeclarativeBase` |
| `@app.before_first_request` | removido no Flask 2.3 | inicialização explícita na criação da aplicação |
| `flask.json.JSONEncoder`, `app.json_encoder` | removido no Flask 2.3 | `app.json` (provider) |
| `FLASK_ENV`, `app.env` | removido no Flask 2.3 | `FLASK_DEBUG`, `app.debug` |
| `asyncio.get_event_loop()` sem loop em execução | Python 3.10 a 3.12 | `asyncio.run()`, `asyncio.get_running_loop()` |
| `imp`, `distutils` | removidos no Python 3.12 | `importlib`, `setuptools` |
| `pkg_resources` | setuptools recentes | `importlib.metadata`, `importlib.resources` |
| `logger.warn()` | Python 3.3 | `logger.warning()` |

### JavaScript e Node.js

| Deprecated | Desde | Use |
|---|---|---|
| `new Buffer(x)`, `Buffer(x)` | Node 6 (DEP0005) | `Buffer.from(x)`, `Buffer.alloc(n)` |
| `url.parse()` | API legada (DEP0169) | `new URL(...)` |
| `crypto.createCipher()`, `createDecipher()` | Node 10 (DEP0106), removido no Node 22 | `crypto.createCipheriv()`, `createDecipheriv()` |
| `fs.exists()` | DEP0103 | `fs.existsSync()`, `fs.access()`, `fs.stat()` |
| `util.isArray()`, `util.isString()` e similares | Node 4 (DEP0044 em diante) | `Array.isArray()`, `typeof` |
| `String.prototype.substr()` | legado no ECMAScript (Annex B) | `substring()` ou `slice()` |
| `body-parser` como pacote separado para JSON | Express 4.16+ | `express.json()`, `express.urlencoded()` |
| `req.param(nome)` | Express 4 | `req.params`, `req.query`, `req.body` |
| `res.send(status, corpo)`, `res.json(status, corpo)` | Express 4 | `res.status(status).send(corpo)` |
| pacote `request` | abandonado em 2020 | `fetch` nativo (Node 18+), `undici`, `axios` |
| `domain` (módulo) | DEP0032 | `AsyncLocalStorage`, tratamento explícito de erro |

### Outras stacks

| Stack | Exemplos do que procurar |
|---|---|
| Java | `new Date(ano, mes, dia)`, `Thread.stop()`, `finalize()`, `javax.*` em Jakarta EE 9+, `WebSecurityConfigurerAdapter` (Spring Security 5.7+) |
| PHP | funções `mysql_*`, `each()`, `create_function()` |
| Ruby e Rails | `update_attributes`, `before_filter`, `find_by_<campo>` dinâmicos |
| Go | `io/ioutil` (Go 1.16+), `strings.Title` |
| .NET | `WebClient`, `BinaryFormatter` |

No relatório, cada API deprecated encontrada aparece com a alternativa moderna na recomendação. Quando nenhuma for encontrada, o relatório diz isso de forma explícita (veja o template).
