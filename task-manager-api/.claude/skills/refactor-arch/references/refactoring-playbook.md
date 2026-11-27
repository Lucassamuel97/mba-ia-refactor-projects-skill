# Playbook de refatoração (Fase 3)

Como transformar cada anti-pattern do catálogo em código correto, com exemplos de antes e depois, e como provar que a aplicação continua funcionando. Os exemplos alternam entre Python e JavaScript; a técnica é a mesma em qualquer stack, então adapte a sintaxe e mantenha a ideia.

## Conteúdo

- [Regras gerais](#regras-gerais)
- [Ordem de execução](#ordem-de-execução)
- [Smoke test: antes e depois](#smoke-test-antes-e-depois)
- Transformações
  - [T-01 Parametrizar queries](#t-01--parametrizar-queries)
  - [T-02 Extrair configuração para o ambiente](#t-02--extrair-configuração-para-o-ambiente)
  - [T-03 Dividir a God Class em camadas](#t-03--dividir-a-god-class-em-camadas)
  - [T-04 Parar de expor dados sensíveis](#t-04--parar-de-expor-dados-sensíveis)
  - [T-05 Hash de senha com KDF padrão](#t-05--hash-de-senha-com-kdf-padrão)
  - [T-06 Remover ou proteger operações perigosas](#t-06--remover-ou-proteger-operações-perigosas)
  - [T-07 Afinar o controller](#t-07--afinar-o-controller)
  - [T-08 Trocar estado global por dependência injetada](#t-08--trocar-estado-global-por-dependência-injetada)
  - [T-09 Eliminar N+1](#t-09--eliminar-n1)
  - [T-10 Agrupar escritas em transação e tratar dependentes](#t-10--agrupar-escritas-em-transação-e-tratar-dependentes)
  - [T-11 Centralizar a validação de entrada](#t-11--centralizar-a-validação-de-entrada)
  - [T-12 Centralizar o tratamento de erro](#t-12--centralizar-o-tratamento-de-erro)
  - [T-13 Remover duplicação](#t-13--remover-duplicação)
  - [T-14 Substituir APIs deprecated](#t-14--substituir-apis-deprecated)
  - [T-15 Converter callbacks em async/await](#t-15--converter-callbacks-em-asyncawait)
  - [T-16 Limpeza de legibilidade](#t-16--limpeza-de-legibilidade)
  - [T-17 Autenticação e autorização por padrão](#t-17--autenticação-e-autorização-por-padrão)
- [Limites da refatoração](#limites-da-refatoração)

## Regras gerais

- **A Recommendation aprovada é o escopo da Fase 3, por inteiro.** Cada finding do relatório traz uma Recommendation escrita a partir de uma transformação deste playbook, e a pessoa a aprovou ao confirmar. Aplique-a como escrita: todas as ações e todas as ocorrências listadas em `File:`. Não troque por uma versão mais branda (proteger em vez de remover, registrar em vez de corrigir, proteger só parte das rotas), não deixe parte para depois e não acrescente o que ela não pede.
- **Feche o Impact, não só o sinal.** O finding só está resolvido quando a consequência descrita no `Impact` deixa de acontecer. Mover um `print("Devolver estoque")` para um service não devolve o estoque; proteger as rotas administrativas não impede que qualquer um liste os pedidos. Antes de dar uma transformação por concluída, reproduza o Impact e confirme que ele não acontece mais. Na Fase 2, isso vale ao contrário: só recomende o que este playbook manda fazer, porque a Recommendation será cobrada. Se uma Recommendation se mostrar inviável como escrita, pare e pergunte, com a alternativa.
- **A aplicação precisa subir como antes.** O mesmo comando de start, sem nenhuma variável de ambiente nova obrigatória. Quem clonar o projeto e seguir o README antigo tem de ver a aplicação no ar. Segredos saem do código, mas a ausência deles no ambiente de desenvolvimento não pode impedir o boot (veja T-02).
- **O contrato HTTP não muda**, exceto nas mudanças que a Recommendation aprovada descreve (os tipos permitidos estão nas guidelines de MVC). Fora delas, mensagens de erro, nomes de campos e status codes existentes são copiados como estão. Preservar o contrato nunca justifica aplicar só parte de uma Recommendation: a mudança que ela causa vai para `Behavior Changes`.
- **Passos pequenos, verificados.** Depois de cada camada extraída, confirme que o código ainda carrega (`python -c "import app"`, `node --check arquivo.js` ou o equivalente). Um erro de import descoberto no fim custa muito mais para localizar.
- **Sem dependências novas** quando a biblioteca padrão ou o que o projeto já usa resolve. Cada dependência adicionada é um risco de o projeto não instalar na máquina de outra pessoa.
- **Mova, não reescreva.** Leve o código existente para a camada certa mudando o mínimo. Reescrever regra de negócio durante a mudança de lugar é a principal fonte de regressão.
- **Dados de seed e schema iguais.** Mesmos registros, mesmos ids, mesmas colunas. A única exceção é o valor de campos de senha, que passam a ser hashes.
- **Atualize quem depende.** Procure no projeto inteiro os imports de cada módulo movido (seed, testes, scripts, `Dockerfile`, `Procfile`, `package.json`) e a documentação de como rodar.

## Ordem de execução

A ordem importa porque cada passo usa o que o anterior criou e deixa a aplicação em estado verificável.

1. **Config** (T-02): tudo o mais vai depender dela.
2. **Banco e models** (T-01, T-08, T-09, T-10, T-05): conexão, schema e seed em módulo próprio; um model por domínio, com queries parametrizadas.
3. **Services**, se houver regra que cruza entidades (T-07).
4. **Controllers** (T-07, T-11): um por domínio, finos.
5. **Routes/views** (T-04): só mapeamento e serialização.
6. **Middlewares** (T-12, T-06): erro central e guards.
7. **Entry point**: composition root (T-03).
8. **Limpeza** (T-13, T-14, T-15, T-16): duplicação, APIs deprecated, legibilidade, remoção dos arquivos antigos.
9. **Validação**: smoke test depois, nova varredura do catálogo.

Em um projeto parcialmente organizado, pule o que já existe e está certo, e aplique só os passos cujos findings apareceram no relatório.

## Smoke test: antes e depois

A prova de que nada quebrou é chamar os mesmos endpoints antes e depois e comparar as respostas. O script `scripts/http_smoke.py` desta skill faz as duas coisas com a biblioteca padrão do Python 3.

### 1. Monte o arquivo de requisições

A partir do inventário de rotas da Fase 1, escreva um JSON com pelo menos uma chamada de sucesso por rota e os principais casos de erro (não encontrado, entrada inválida). Guarde-o fora do projeto, em um diretório temporário.

```json
[
  {"method": "GET", "path": "/books"},
  {"method": "GET", "path": "/books/999"},
  {"method": "POST", "path": "/books", "body": {"title": "Dom Casmurro", "copies": 2}},
  {"method": "POST", "path": "/login", "body": {"email": "admin@example.com", "password": "secret"},
   "capture": {"admin": "token"}, "ignore": ["token"]},
  {"method": "GET", "path": "/reports/loans", "headers": {"Authorization": "Bearer ${admin}"},
   "unordered": true}
]
```

`capture` guarda o valor de um campo da resposta (caminho com pontos, como `data.token`) numa variável, e `${nome}` usa essa variável em `path`, `headers` ou `body`. Na gravação do comportamento original, o login ainda não devolve token: a variável fica vazia e o cabeçalho vai como `Bearer `, que o código legado ignora. Assim, o mesmo arquivo serve para antes e depois, e as rotas protegidas chamadas com o token certo precisam devolver exatamente a resposta original.

Cuidados:

- Ordene para que cada chamada encontre o estado de que precisa: criar, ler, atualizar, apagar.
- Deixe por último as chamadas destrutivas globais (reset de dados).
- Use `"unordered": true` em respostas cuja ordem a API não garante, e `"ignore"` em campos que mudam a cada execução.
- Inclua uma chamada que demonstre cada falha de segurança encontrada (por exemplo, o login com injeção) e uma que exercite cada mudança anunciada nas Recommendations (a exclusão de um registro com dependentes, uma entrada que passará a ser recusada, a rota que será removida). Elas comprovam a correção depois.
- Use os exemplos do projeto (`*.http`, README, coleções) para acertar os payloads.

### 2. Grave o comportamento original

Antes de alterar qualquer arquivo de código:

1. Garanta as dependências instaladas, usando o ambiente que o projeto já tem (`.venv`, `node_modules`) ou criando-o como o README manda. Nunca instale pacotes de forma global.
2. Confirme que a porta está livre (`ss -ltnp | grep ':<porta>'` ou `lsof -i :<porta>`). Se algo já escuta nela, não é a aplicação que você vai subir: descubra o que é antes de continuar.
3. Leve o banco local ao estado inicial (apague o arquivo de banco de desenvolvimento que a própria aplicação recria e rode o seed, se houver).
4. Suba a aplicação em segundo plano, com a saída redirecionada para um arquivo de log.
5. Rode o smoke test (o script espera a aplicação responder antes de começar):

```bash
python3 <pasta-da-skill>/scripts/http_smoke.py run \
  --base-url http://127.0.0.1:<porta> --requests <tmp>/requests.json --out <tmp>/before.json
```

6. Derrube a aplicação e confirme que a porta foi liberada. Identifique o processo pela porta em que ele escuta, porque o PID devolvido pelo shell muitas vezes é o de um wrapper (`npm start`, reloader do framework) e matar o wrapper deixa o servidor no ar.

Um servidor antigo esquecido no ar é a falha mais traiçoeira desta etapa: a gravação seguinte fala com o código antigo e "valida" uma refatoração que nunca rodou. Por isso a checagem de porta livre vem antes de cada boot, e o log do boot deve ser lido para confirmar que a aplicação iniciou sem erro.

Se a aplicação não sobe antes da refatoração, registre o erro, corrija só o necessário para subir e siga; se nem assim subir, a validação será apenas estática e isso precisa aparecer no resumo final com `✗`.

**Banco externo:** se a aplicação aponta para um banco que não é local e descartável, não rode chamadas que alteram dados. Limite o smoke test aos `GET` e avise o usuário.

### 3. Marque as mudanças esperadas

Para cada chamada cuja resposta deve mudar por causa de uma Recommendation aprovada (campo removido, rota removida, guard novo, validação nova, exclusão com dependentes), acrescente `"expect_change": "<Recommendation que causa a mudança>"` no arquivo de requisições. Faça isso antes de rodar o depois: declarar a expectativa antes de ver o resultado impede que uma regressão seja racionalizada como "esperada", e o compare acusa as chamadas que deveriam ter mudado e não mudaram, o que denuncia uma Recommendation esquecida.

Se uma rota passou a exigir um cabeçalho (guard de acesso), mantenha a chamada original sem o cabeçalho, marcada com `expect_change`, para registrar o novo comportamento. Mantenha também as chamadas a rotas removidas, marcadas com `expect_change`: o 404 no depois comprova a remoção.

### 4. Grave o comportamento novo e compare

Repita os passos 2 a 6 com o mesmo estado inicial de banco, gravando em `<tmp>/after.json`, e compare:

```bash
python3 <pasta-da-skill>/scripts/http_smoke.py compare <tmp>/before.json <tmp>/after.json
```

O resultado lista mudanças inesperadas, mudanças esperadas e chamadas que deveriam ter mudado e não mudaram. A Fase 3 só está validada com zero mudanças inesperadas, zero pendências e nenhuma resposta 5xx nova. Cada mudança inesperada é uma regressão: corrija o código (não o arquivo de requisições) e rode de novo.

Sem Python 3 disponível, faça o mesmo com `curl -s -w '%{http_code}'`, gravando status e corpo de cada chamada em dois arquivos e comparando com `diff`.

---

## T-01 — Parametrizar queries

**Resolve:** AP-01

Passe os valores separados da query, com os placeholders do driver. O driver trata os valores como dados, nunca como SQL.

Antes (Python, sqlite3):

```python
def find_by_login(email, password):
    cursor.execute(
        "SELECT * FROM readers WHERE email = '" + email + "' AND password = '" + password + "'"
    )
    return cursor.fetchone()

def search(term, max_price):
    query = "SELECT * FROM books WHERE 1=1"
    if term:
        query += " AND title LIKE '%" + term + "%'"
    if max_price:
        query += " AND price <= " + str(max_price)
    cursor.execute(query)
    return cursor.fetchall()
```

Depois:

```python
def find_by_email(email):
    cursor.execute("SELECT * FROM readers WHERE email = ?", (email,))
    return cursor.fetchone()

def search(term, max_price):
    conditions, params = ["1=1"], []
    if term:
        conditions.append("title LIKE ?")
        params.append(f"%{term}%")
    if max_price:
        conditions.append("price <= ?")
        params.append(max_price)
    cursor.execute("SELECT * FROM books WHERE " + " AND ".join(conditions), params)
    return cursor.fetchall()
```

Em JavaScript, `` db.all(`SELECT * FROM books WHERE id = ${id}`) `` vira `db.all('SELECT * FROM books WHERE id = ?', [id])`.

Notas:

- O placeholder depende do driver: `?` (sqlite, mysql), `%s` (psycopg, mysqlclient), `$1` (pg), `:nome` (parâmetros nomeados).
- Em query dinâmica, só os fragmentos fixos de SQL são concatenados; os valores vão sempre na lista de parâmetros.
- Nomes de coluna ou direção de ordenação vindos da requisição não aceitam placeholder: valide contra uma lista fixa de valores permitidos.

## T-02 — Extrair configuração para o ambiente

**Resolve:** AP-02, parte de AP-06 (debug fixo)

Um módulo de config lê o ambiente uma vez; o resto do código recebe os valores. Nenhum segredo fica escrito no código, nem como valor padrão.

Antes (Python):

```python
app.config["SECRET_KEY"] = "chave-super-secreta-123"
app.config["DEBUG"] = True
db = sqlite3.connect("library.db")
app.run(host="0.0.0.0", port=5000, debug=True)
```

Depois:

```python
# config/settings.py
import os
import secrets


def _flag(name, default="false"):
    return os.environ.get(name, default).strip().lower() in ("1", "true", "yes")


class Settings:
    # Sem SECRET_KEY no ambiente, gera uma chave efêmera: o desenvolvimento funciona
    # sem configuração e nenhuma chave conhecida existe no repositório.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = _flag("APP_DEBUG")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "library.db")
    HOST = os.environ.get("APP_HOST", "127.0.0.1")
    PORT = int(os.environ.get("APP_PORT", "5000"))
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")  # ausente = operações administrativas desligadas
```

```python
# app.py
app.config.from_object(Settings)
...
app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
```

Em Node.js:

```js
// src/config/index.js
module.exports = {
  port: Number(process.env.PORT || 3000),
  databasePath: process.env.DATABASE_PATH || ':memory:',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || null, // ausente = gateway desligado
  smtpUser: process.env.SMTP_USER || null,
  smtpPassword: process.env.SMTP_PASSWORD || null,
};
```

Notas:

- **O boot não pode passar a depender de uma variável nova.** Para segredos de que a aplicação precisa para subir, gere um valor efêmero quando ausentes; para segredos de integrações, trate a ausência como "recurso desligado" e falhe só no momento do uso, com mensagem clara.
- Mantenha os valores padrão não sensíveis iguais aos originais (porta, nome do arquivo de banco), para que o comando de start e os clientes continuem funcionando.
- Crie um `.env.example` com os nomes das variáveis e valores fictícios, e confirme que `.env` está no `.gitignore`.
- Use um carregador de `.env` só se o projeto já tiver essa dependência.
- Um segredo que já esteve versionado continua no histórico do git. Diga no resumo final que ele deve ser rotacionado.

## T-03 — Dividir a God Class em camadas

**Resolve:** AP-03, AP-10

Separe a classe pelo que cada trecho faz e ligue as partes no entry point, entregando as dependências de fora para dentro.

Antes (JavaScript, Express):

```js
class LibraryManager {
  constructor() {
    this.db = new sqlite3.Database('library.db');
  }

  initDb() {
    this.db.run('CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT, copies INTEGER)');
    this.db.run('CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY, book_id INTEGER, reader_id INTEGER)');
  }

  setupRoutes(app) {
    app.post('/api/loans', (req, res) => {
      this.db.get('SELECT * FROM books WHERE id = ?', [req.body.book_id], (err, book) => {
        if (err || !book) return res.status(404).send('Livro não encontrado');
        if (book.copies < 1) return res.status(400).send('Livro indisponível');
        this.db.run('INSERT INTO loans (book_id, reader_id) VALUES (?, ?)',
          [book.id, req.body.reader_id], function () {
            res.json({ loan_id: this.lastID });
          });
      });
    });
  }
}
```

Depois:

```
src/
├── config/index.js
├── database/connection.js      abre a conexão e expõe run/get/all com promises
├── database/schema.js          cria tabelas e seed
├── models/bookModel.js
├── models/loanModel.js
├── services/loanService.js
├── controllers/loanController.js
├── routes/loanRoutes.js
├── middlewares/errorHandler.js
└── app.js                      composition root
```

```js
// models/bookModel.js — único lugar com SQL de livros
class BookModel {
  constructor(db) {
    this.db = db;
  }

  findById(id) {
    return this.db.get('SELECT * FROM books WHERE id = ?', [id]);
  }
}

// services/loanService.js — regra de empréstimo, sem HTTP e sem SQL
class LoanService {
  constructor({ bookModel, loanModel }) {
    this.bookModel = bookModel;
    this.loanModel = loanModel;
  }

  async lendBook({ bookId, readerId }) {
    const book = await this.bookModel.findById(bookId);
    if (!book) throw new NotFoundError('Livro não encontrado');
    if (book.copies < 1) throw new BusinessRuleError('Livro indisponível');
    return this.loanModel.create({ bookId, readerId });
  }
}

// controllers/loanController.js — traduz HTTP para o caso de uso
function createLoanController({ loanService }) {
  return {
    async create(req, res) {
      const loanId = await loanService.lendBook({
        bookId: req.body.book_id,
        readerId: req.body.reader_id,
      });
      res.json({ loan_id: loanId });
    },
  };
}

// routes/loanRoutes.js — só mapeamento
function loanRoutes({ loanController }) {
  const router = express.Router();
  router.post('/loans', asyncHandler(loanController.create));
  return router;
}

// app.js — composition root
const db = createConnection(config.databasePath);
initSchema(db);

const bookModel = new BookModel(db);
const loanModel = new LoanModel(db);
const loanService = new LoanService({ bookModel, loanModel });
const loanController = createLoanController({ loanService });

const app = express();
app.use(express.json());
app.use('/api', loanRoutes({ loanController }));
app.use(errorHandler);
app.listen(config.port);
```

Notas:

- Caminhos, status codes e corpos continuam idênticos: `/api/loans`, 404 com o texto `Livro não encontrado`, `{ loan_id }` no sucesso. Se o original respondia em texto puro, o handler de erro responde em texto puro.
- Cada classe recebe o que usa pelo construtor. Nenhuma camada faz `require` da conexão concreta.
- Divida por domínio: um model, um controller e um arquivo de rotas por entidade principal.

## T-04 — Parar de expor dados sensíveis

**Resolve:** AP-04

Defina de forma explícita o que é público. A serialização lista os campos permitidos, em vez de devolver o registro inteiro.

Antes (Python):

```python
class Reader(db.Model):
    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email,
                "password": self.password, "role": self.role}

def health():
    return jsonify({"status": "ok", "secret_key": app.config["SECRET_KEY"], "db_path": DB_PATH})

print(f"Cobrando cartão {card_number} com a chave {gateway_key}")
```

Depois:

```python
class Reader(db.Model):
    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}

def health():
    return jsonify({"status": "ok"})

logger.info("Cobrando cartão final %s", card_number[-4:])
```

Notas:

- Com SQL escrito à mão, selecione as colunas pelo nome nas consultas que alimentam respostas, ou remova o campo no mapeamento. `SELECT *` devolvido direto vaza qualquer coluna nova.
- Campos removidos da resposta são a mudança de contrato mais comum desta transformação: marque as chamadas afetadas com `expect_change`.
- Em endpoints de status, mantenha os campos informativos inofensivos (contagens, versão) e retire configuração e segredos.
- Nunca registre em log senha, token, chave, número completo de cartão ou o corpo inteiro de uma requisição.
- Erros internos: o cliente recebe mensagem genérica; o detalhe vai para o log (T-12).

## T-05 — Hash de senha com KDF padrão

**Resolve:** AP-05

Use uma função de derivação de chave feita para senhas, com salt por senha. Não crie algoritmo próprio.

Antes (Python):

```python
def set_password(self, raw):
    self.password = hashlib.md5(raw.encode()).hexdigest()

def check_password(self, raw):
    return self.password == hashlib.md5(raw.encode()).hexdigest()
```

Depois (Werkzeug já vem com o Flask):

```python
from werkzeug.security import check_password_hash, generate_password_hash

def set_password(self, raw):
    self.password = generate_password_hash(raw)

def check_password(self, raw):
    return check_password_hash(self.password, raw)
```

Em Node.js, sem dependência nova:

```js
const { randomBytes, scryptSync, timingSafeEqual } = require('node:crypto');

function hashPassword(password) {
  const salt = randomBytes(16).toString('hex');
  const hash = scryptSync(password, salt, 64).toString('hex');
  return `scrypt$${salt}$${hash}`;
}

function verifyPassword(password, stored) {
  const [scheme, salt, hash] = String(stored).split('$');
  if (scheme !== 'scrypt' || !salt || !hash) return false;
  const expected = Buffer.from(hash, 'hex');
  const candidate = scryptSync(password, salt, expected.length);
  return timingSafeEqual(candidate, expected);
}
```

Notas:

- **Login com senha em texto puro no SQL** (`WHERE email = ? AND senha = ?`): busque o usuário pelo email e verifique a senha no código com a função de verificação.
- **Seed:** as senhas do seed passam pela mesma função de hash, para que os logins de exemplo continuem funcionando.
- **Dados já gravados** com o esquema antigo: se o banco é recriado a cada boot ou pelo seed, basta o item anterior. Se há dados persistentes, aceite o formato antigo na verificação e regrave com o novo hash no primeiro login bem-sucedido.
- Confira o tamanho da coluna: hashes modernos têm mais de 100 caracteres.
- **Senha padrão** atribuída quando o usuário não informa uma: a Recommendation escolhe entre exigir a senha (a requisição sem ela passa a receber 400) e criar a conta sem senha utilizável (a resposta não muda), e a Fase 3 faz exatamente o escolhido.
- Sem Werkzeug, o Python oferece `hashlib.scrypt` com `secrets.token_bytes` para o salt e `hmac.compare_digest` para comparar.

## T-06 — Remover ou proteger operações perigosas

**Resolve:** AP-06, parte de AP-11

Uma operação perigosa tem um de dois destinos, e a Recommendation diz qual:

| Operação | Correção |
|---|---|
| Executa SQL, comando de shell ou código recebido na requisição | **Remover.** Não existe versão segura: um token só muda quem pode tomar o banco ou o servidor, e qualquer vazamento dele devolve o controle total. A rota, o handler e o código que só ela usava deixam de existir. |
| Operação destrutiva ou administrativa legítima (reset de dados, exclusão em massa, relatório interno) | **Proteger.** A rota continua existindo, desligada por padrão, e só responde a quem apresenta um token definido no ambiente. |

### Remover

Antes (Python):

```python
@app.route("/admin/sql", methods=["POST"])
def run_sql():
    sql = request.get_json().get("sql", "")
    rows = db.execute(sql).fetchall()
    db.commit()
    return jsonify({"rows": [dict(row) for row in rows]}), 200
```

Depois: a rota não é registrada e nenhum código do projeto executa SQL recebido de fora.

```python
# routes/admin_routes.py: só as operações que têm versão segura
admin_bp.add_url_rule("/admin/purge", view_func=require_admin_token(admin_controller.purge_data),
                      methods=["POST"])
# POST /admin/sql deixa de existir e responde 404, como qualquer rota desconhecida.
```

Em Express é igual: o `router.post('/admin/sql', ...)`, o handler e a função que executa o texto recebido são apagados.

Notas:

- Apague também o que só servia à rota: método de controller, função de model que executa texto arbitrário, exceções e mensagens exclusivas dela. Procure cada nome no projeto inteiro antes de apagar.
- Não troque a remoção por um guard, por um 403 fixo ou por um 410 "para manter o contrato". Isso é a rota protegida com outro nome, e a Recommendation disse remover.
- A Recommendation anuncia a mudança ("a rota deixa de existir e passa a responder 404"), e a chamada à rota fica no smoke test com `expect_change`: o 404 no depois comprova a remoção.
- Se a rota tinha um uso legítimo identificável (consultar contagens, por exemplo), esse uso só vira uma rota própria, com query fixa, se a Recommendation disser isso.

### Proteger

Antes (Python):

```python
@app.route("/admin/purge", methods=["POST"])
def purge_data():
    cursor.execute("DELETE FROM loans")
    cursor.execute("DELETE FROM books")
    db.commit()
    return jsonify({"message": "Dados apagados"}), 200
```

Depois:

```python
# middlewares/auth.py
import hmac
from functools import wraps

from flask import current_app, jsonify, request


def require_admin_token(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        expected = current_app.config.get("ADMIN_TOKEN")
        provided = request.headers.get("X-Admin-Token", "")
        if not expected or not hmac.compare_digest(provided, expected):
            return jsonify({"error": "Acesso negado"}), 403
        return view(*args, **kwargs)
    return wrapper
```

```python
# routes/admin_routes.py
admin_bp.add_url_rule("/admin/purge", view_func=require_admin_token(admin_controller.purge_data),
                      methods=["POST"])
```

Notas:

- Quando o projeto tem login de usuário, a proteção usa o papel de administrador do T-17, e não um token separado. `ADMIN_TOKEN` é para projetos sem login.
- Sem `ADMIN_TOKEN` no ambiente, a rota responde 403 sempre. Seguro por padrão, e a rota continua respondendo.
- Use a mesma chave de erro do restante da API no corpo do 403.
- Este caminho vale só para operações que têm versão segura. Execução de SQL, comando ou código recebido na requisição segue o caminho "Remover", mesmo que a rota também esteja atrás de um prefixo `admin`.
- Modo debug: vem da config, desligado por padrão (T-02).
- No Express, o mesmo guard é um middleware `(req, res, next)` aplicado só nas rotas administrativas.
- No smoke test, a chamada sem token fica com `expect_change`.

## T-07 — Afinar o controller

**Resolve:** AP-07, AP-08

A rota mapeia, o controller conduz, a regra vai para o service ou o model, e o acesso a dados fica no model.

Antes (Python, Flask):

```python
@loans_bp.route("/loans", methods=["POST"])
def create_loan():
    data = request.get_json()
    if not data or "book_id" not in data:
        return jsonify({"error": "book_id é obrigatório"}), 400
    book = Book.query.get(data["book_id"])
    if not book:
        return jsonify({"error": "Livro não encontrado"}), 404
    active = Loan.query.filter_by(reader_id=data["reader_id"], returned_at=None).count()
    if active >= 3:
        return jsonify({"error": "Limite de empréstimos atingido"}), 400
    if book.copies < 1:
        return jsonify({"error": "Livro indisponível"}), 400
    loan = Loan(book_id=book.id, reader_id=data["reader_id"])
    book.copies -= 1
    db.session.add(loan)
    db.session.commit()
    return jsonify(loan.to_dict()), 201
```

Depois:

```python
# routes/loan_routes.py
loans_bp = Blueprint("loans", __name__)
loans_bp.add_url_rule("/loans", view_func=loan_controller.create_loan, methods=["POST"])
```

```python
# controllers/loan_controller.py
def create_loan():
    data = request.get_json()
    if not data or "book_id" not in data:
        raise ValidationError("book_id é obrigatório")
    loan = loan_service.lend_book(book_id=data["book_id"], reader_id=data["reader_id"])
    return jsonify(loan.to_dict()), 201
```

```python
# services/loan_service.py
MAX_ACTIVE_LOANS = 3


def lend_book(book_id, reader_id):
    book = db.session.get(Book, book_id)
    if book is None:
        raise NotFoundError("Livro não encontrado")
    if Loan.count_active_for(reader_id) >= MAX_ACTIVE_LOANS:
        raise BusinessRuleError("Limite de empréstimos atingido")
    if not book.is_available():
        raise BusinessRuleError("Livro indisponível")
    loan = Loan(book_id=book.id, reader_id=reader_id)
    book.copies -= 1
    db.session.add(loan)
    db.session.commit()
    return loan
```

Notas:

- As mensagens e os status codes são os mesmos do original; as exceções de domínio são convertidas em resposta pelo handler central (T-12).
- Regra que estava no model errado segue o mesmo caminho: cálculo de desconto dentro da função de relatório vira uma função nomeada no service ou no model da entidade.
- Se o projeto já tem um método ou helper que implementa a regra e ninguém chama, use-o em vez de criar outro.
- CRUD de uma entidade dentro do arquivo de rotas de outra ganha arquivos próprios de rota e controller, com os mesmos caminhos.
- Efeitos colaterais (notificação, email) saem do controller para um service, mesmo que hoje sejam só uma linha de log.

## T-08 — Trocar estado global por dependência injetada

**Resolve:** AP-09, AP-10

O recurso passa a ter um dono (a composição ou o contexto da requisição) e chega a quem usa por parâmetro ou pelo mecanismo do framework.

Antes (Python):

```python
db_connection = None

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("library.db", check_same_thread=False)
        db_connection.execute("CREATE TABLE IF NOT EXISTS books (...)")
        db_connection.execute("INSERT INTO books ...")
    return db_connection
```

Depois (conexão por requisição; schema e seed separados):

```python
# database/connection.py
import sqlite3

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
```

```python
# database/schema.py
def init_db():
    db = get_db()
    db.executescript(SCHEMA_SQL)
    seed_if_empty(db)
    db.commit()
```

```python
# app.py
connection.init_app(app)
with app.app_context():
    schema.init_db()
```

Antes (JavaScript):

```js
let lookupCache = {};
let requestCount = 0;

function remember(key, value) {
  requestCount++;
  lookupCache[key] = value;
}
```

Depois: se nada lê o cache, remova-o (é código morto). Se é usado, vira um objeto com limite, criado na composição e injetado:

```js
class BoundedCache {
  constructor(maxEntries = 500) {
    this.maxEntries = maxEntries;
    this.entries = new Map();
  }

  set(key, value) {
    if (this.entries.size >= this.maxEntries) {
      this.entries.delete(this.entries.keys().next().value);
    }
    this.entries.set(key, value);
  }

  get(key) {
    return this.entries.get(key);
  }
}
```

Notas:

- **Banco em memória** (`:memory:`): cada conexão nova é um banco vazio, então é preciso uma conexão única. Ela é criada no entry point e injetada nos models, não guardada em variável global de módulo.
- **Estado em memória dentro de objetos.** Uma coleção em atributo de um objeto que vive o processo todo (`self.notifications = []`) é estado global com outro nome. Se nada lê esse estado, ele é apagado junto com as escritas; se uma rota ou regra lê, ele passa para uma tabela. Injetar o objeto não resolve: a coleção continua crescendo.
- Com ORM que gerencia sessão por requisição, não crie outro mecanismo; use o do ORM.
- Criação de schema e seed saem da função que abre a conexão e passam a ser chamados uma vez, na inicialização.

## T-09 — Eliminar N+1

**Resolve:** AP-12

Troque a query por item por uma query que traz tudo (`JOIN`, `IN`, `GROUP BY`) e monte a estrutura em memória.

Antes (Python, SQL manual):

```python
def list_loans():
    loans = []
    for row in db.execute("SELECT * FROM loans").fetchall():
        loan = dict(row)
        book = db.execute("SELECT title FROM books WHERE id = ?", (row["book_id"],)).fetchone()
        loan["book_title"] = book["title"] if book else "Desconhecido"
        loans.append(loan)
    return loans
```

Depois:

```python
def list_loans():
    rows = db.execute(
        """
        SELECT l.*, COALESCE(b.title, 'Desconhecido') AS book_title
        FROM loans l
        LEFT JOIN books b ON b.id = l.book_id
        ORDER BY l.id
        """
    ).fetchall()
    return [dict(row) for row in rows]
```

Com pai e lista de filhos, uma query com `JOIN` e agrupamento no código:

```python
def list_orders_with_items():
    rows = db.execute(
        """
        SELECT o.id, o.status, o.total, i.product_id, i.quantity, p.name AS product_name
        FROM orders o
        LEFT JOIN order_items i ON i.order_id = o.id
        LEFT JOIN products p ON p.id = i.product_id
        ORDER BY o.id, i.id
        """
    ).fetchall()
    orders = {}
    for row in rows:
        order = orders.setdefault(
            row["id"], {"id": row["id"], "status": row["status"], "total": row["total"], "items": []}
        )
        if row["product_id"] is not None:
            order["items"].append({"product_id": row["product_id"], "quantity": row["quantity"],
                                   "product_name": row["product_name"]})
    return list(orders.values())
```

Com ORM (SQLAlchemy), carregue os relacionamentos junto e agregue no banco:

```python
# antes: uma query por empréstimo para buscar o leitor
loans = Loan.query.all()
names = [db.session.get(Reader, loan.reader_id).name for loan in loans]

# depois: relacionamentos carregados junto
loans = db.session.execute(
    db.select(Loan).options(selectinload(Loan.reader), selectinload(Loan.book))
).scalars().all()

# antes: um COUNT por status
active = Loan.query.filter_by(status="active").count()
returned = Loan.query.filter_by(status="returned").count()

# depois: um GROUP BY
counts = dict(db.session.execute(db.select(Loan.status, db.func.count()).group_by(Loan.status)).all())
```

Notas:

- A resposta precisa ser idêntica: mesma ordem (`ORDER BY` explícito), mesmos valores padrão para registros ausentes (`LEFT JOIN` com `COALESCE`), mesmas chaves, e zero para grupos sem linhas.
- Use `LEFT JOIN` quando o original tolerava o registro relacionado ausente; `INNER JOIN` faria linhas sumirem.
- Contagens e somas feitas em laço na aplicação viram `COUNT`/`SUM` com `GROUP BY`.

## T-10 — Agrupar escritas em transação e tratar dependentes

**Resolve:** AP-13

Valide tudo antes de escrever e execute as escritas dependentes em uma única transação, com rollback se qualquer uma falhar.

Antes (Python):

```python
def create_order(reader_id, items):
    cursor.execute("INSERT INTO orders (reader_id) VALUES (?)", (reader_id,))
    order_id = cursor.lastrowid
    for item in items:
        cursor.execute("INSERT INTO order_items (order_id, book_id, quantity) VALUES (?, ?, ?)",
                       (order_id, item["book_id"], item["quantity"]))
        cursor.execute("UPDATE books SET copies = copies - ? WHERE id = ?",
                       (item["quantity"], item["book_id"]))
    db.commit()
    return order_id
```

Depois:

```python
def create_order(reader_id, items):
    with db:  # commit ao sair sem erro, rollback se houver exceção
        cursor = db.execute("INSERT INTO orders (reader_id) VALUES (?)", (reader_id,))
        order_id = cursor.lastrowid
        for item in items:
            db.execute("INSERT INTO order_items (order_id, book_id, quantity) VALUES (?, ?, ?)",
                       (order_id, item["book_id"], item["quantity"]))
            db.execute("UPDATE books SET copies = copies - ? WHERE id = ?",
                       (item["quantity"], item["book_id"]))
    return order_id
```

Em Node.js, com um driver baseado em promises:

```js
async function inTransaction(db, work) {
  await db.run('BEGIN');
  try {
    const result = await work();
    await db.run('COMMIT');
    return result;
  } catch (err) {
    await db.run('ROLLBACK');
    throw err;
  }
}
```

Notas:

- Com ORM: um único `commit` no fim do caso de uso e `rollback` no tratamento de erro.
- Pagamentos e outras chamadas externas não participam da transação do banco: faça a chamada externa, depois grave o resultado na transação.

### Exclusão de registro com dependentes

Apagar um registro pai sem tratar os filhos deixa órfãos, mesmo dentro de uma transação. A Recommendation escolhe um destes tratamentos pelo papel que os filhos têm, e a Fase 3 implementa exatamente o escolhido:

| Os registros filhos... | Tratamento | Resposta da exclusão |
|---|---|---|
| só existem em função do pai (itens de um carrinho, sessões, preferências) | apagar os filhos e o pai na mesma transação | a de sucesso de antes |
| têm valor próprio e a referência ao pai é opcional (livro com categoria) | anular a referência e apagar o pai na mesma transação | a de sucesso de antes |
| são histórico ou registro financeiro que outras rotas leem (pedidos, pagamentos, matrículas, empréstimos) | recusar a exclusão enquanto houver filhos; sem filhos, apagar como antes | 409 no envelope de erro da API, enquanto houver filhos |

Histórico não é apagado em cascata porque um pagamento de um cliente removido continua sendo receita que aconteceu: apagá-lo altera relatórios passados sem ninguém perceber.

Antes (Python):

```python
def delete_reader(reader_id):
    db.execute("DELETE FROM readers WHERE id = ?", (reader_id,))
    db.commit()  # empréstimos e multas do leitor ficam apontando para um id que não existe
```

Depois, com empréstimos que o relatório de circulação lê:

```python
def delete_reader(reader_id):
    with db:
        if loan_model.count_by_reader(reader_id) > 0:
            raise ConflictError("Leitor possui empréstimos registrados")  # vira 409 no handler central
        reader_model.delete(reader_id)
```

Depois, com uma referência opcional:

```python
def delete_category(category_id):
    with db:
        db.execute("UPDATE books SET category_id = NULL WHERE category_id = ?", (category_id,))
        db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
```

Notas da exclusão:

- A Recommendation diz qual linha da tabela se aplica e a resposta que resulta dela ("a exclusão responde 409 enquanto o usuário tiver matrículas"). "Decidir a regra depois" não é uma Recommendation.
- A checagem e a exclusão ficam na mesma transação, para que um filho criado entre as duas não escape.
- O 409 vem de uma exceção de domínio com esse status, convertida pelo handler central (T-12), com a chave e o formato de erro que a API já usa.
- A resposta nova entra em `Behavior Changes`, e o smoke test exclui um registro que tem dependentes, com `expect_change`.

## T-11 — Centralizar a validação de entrada

**Resolve:** AP-14

Valide presença, tipo e faixa em um só lugar, antes de qualquer regra ou escrita, e sinalize o erro com uma exceção que o handler central converte em 400.

Antes (Python):

```python
def create_book():
    data = request.get_json()
    if data["price"] < 0:
        return jsonify({"error": "Preço não pode ser negativo"}), 400
    quantity = int(request.args.get("quantity"))
    ...
```

Depois:

```python
# controllers/validation.py
def require_number(data, field, minimum=None, message=None):
    value = data.get(field) if isinstance(data, dict) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(message or f"{field} inválido")
    if minimum is not None and value < minimum:
        raise ValidationError(message or f"{field} inválido")
    return value


def parse_int_param(raw, field):
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} inválido")
```

```python
def create_book():
    data = request.get_json()
    price = require_number(data, "price", minimum=0, message="Preço não pode ser negativo")
    quantity = parse_int_param(request.args.get("quantity"), "quantity")
    ...
```

Notas:

- **Mensagens e status já existentes ficam como estão.** As checagens que já existiam mantêm o texto e o status.
- **A Recommendation define o alcance.** Tudo o que ela lista é validado, inclusive o que hoje é aceito e passa a ser recusado: tipo errado que virava 500, número negativo gravado, corpo `null`, campo que era opcional e passa a ser obrigatório, id de rota que não é inteiro positivo. Cada recusa nova vai para `Behavior Changes` e para o smoke test com `expect_change`.
- Em Python, `bool` é subclasse de `int`; exclua-o ao validar números.
- Valide referências a outros registros (o usuário existe? a categoria existe?) no service, antes da escrita.
- Se o projeto já tem uma biblioteca de validação entre as dependências, use-a; não adicione uma.
- Reaproveite as funções de validação que o projeto já tem e não usa.

## T-12 — Centralizar o tratamento de erro

**Resolve:** AP-15, parte de AP-04

As camadas internas lançam exceções de domínio; um único handler as converte em resposta, registra o inesperado e nunca devolve detalhes internos.

Antes (Python):

```python
def list_books():
    try:
        return jsonify(book_model.find_all()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_book(book_id):
    try:
        ...
    except:
        return jsonify({"error": "Erro interno"}), 500
```

Depois:

```python
# middlewares/errors.py
class AppError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class ValidationError(AppError):
    status_code = 400


class BusinessRuleError(AppError):
    status_code = 400


class NotFoundError(AppError):
    status_code = 404


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class ConflictError(AppError):
    status_code = 409
```

```python
# middlewares/error_handler.py
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": error.message}), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return error  # mantém as respostas padrão do framework (404 de rota, 405, 415)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Erro não tratado")
        return jsonify({"error": "Erro interno do servidor"}), 500
```

```python
# controllers/book_controller.py
def list_books():
    return jsonify(book_model.find_all()), 200
```

Em Express:

```js
// middlewares/errorHandler.js
const asyncHandler = (handler) => (req, res, next) =>
  Promise.resolve(handler(req, res, next)).catch(next);

function errorHandler(err, req, res, next) {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({ error: err.message });
  }
  console.error(err);
  res.status(500).json({ error: 'Erro interno do servidor' });
}
```

Notas:

- Use o envelope de erro que a API já usa (`{"erro": ...}`, `{"error": ...}`, texto puro) e os mesmos status codes. O handler central padroniza o código, não o contrato.
- Se alguma resposta de erro original tinha campos extras (por exemplo `"sucesso": false`), a exceção carrega esses campos para que a resposta saia igual.
- `except:` sem tipo e `catch` vazio são substituídos pelo tipo específico esperado naquele ponto, ou removidos para o erro subir até o handler.
- Em callbacks, verifique o parâmetro de erro antes de usar o resultado; ao converter para promises (T-15), a rejeição chega sozinha ao handler.
- A resposta 500 deixa de trazer o texto da exceção: marque as chamadas afetadas com `expect_change`.

## T-13 — Remover duplicação

**Resolve:** AP-16

Extraia o trecho repetido para uma função com nome e chame-a de todos os lugares.

Antes (Python):

```python
def find_all():
    rows = db.execute("SELECT * FROM books").fetchall()
    return [{"id": r["id"], "title": r["title"], "price": r["price"], "copies": r["copies"]} for r in rows]

def find_by_id(book_id):
    r = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if r:
        return {"id": r["id"], "title": r["title"], "price": r["price"], "copies": r["copies"]}
    return None

# em três rotas diferentes:
if loan.due_date and loan.due_date < now and loan.status != "returned":
    overdue = True
```

Depois:

```python
def _to_dict(row):
    return {"id": row["id"], "title": row["title"], "price": row["price"], "copies": row["copies"]}

def find_all():
    return [_to_dict(row) for row in db.execute("SELECT * FROM books").fetchall()]

def find_by_id(book_id):
    row = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    return _to_dict(row) if row else None

# a regra vive no model e as três rotas chamam loan.is_overdue()
```

Notas:

- Confira se as cópias são mesmo iguais. Quando divergem porque uma perdeu uma checagem que a outra tem (a atualização não valida o que a criação valida), a divergência é um defeito: unifique pela regra mais rígida e declare a mudança. A Recommendation diz isso explicitamente, e a Fase 3 aplica a regra unificada nos dois caminhos.
- Duas funções que diferem por um filtro viram uma função com parâmetro opcional.
- Listas de valores válidos e expressões regulares repetidas viram uma constante única (T-16).

## T-14 — Substituir APIs deprecated

**Resolve:** AP-17

Troque cada API pelo equivalente indicado no catálogo, conferindo que o resultado observável é o mesmo.

Antes (Python):

```python
created_at = db.Column(db.DateTime, default=datetime.utcnow)

if loan.due_date < datetime.utcnow():
    ...

reader = Reader.query.get(reader_id)
```

Depois:

```python
# utils/clock.py
from datetime import datetime, timezone


def utcnow():
    """UTC sem tzinfo, igual ao que o banco já armazena e ao que a API já devolve."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
```

```python
created_at = db.Column(db.DateTime, default=utcnow)

if loan.due_date < utcnow():
    ...

reader = db.session.get(Reader, reader_id)
```

Antes e depois (JavaScript):

```js
const encoded = new Buffer(text).toString('base64');     // antes
const encoded = Buffer.from(text).toString('base64');    // depois

const host = url.parse(address).hostname;                // antes
const host = new URL(address).hostname;                  // depois
```

Notas:

- **Datas:** `datetime.now(timezone.utc)` devolve um valor com fuso. Comparado com valores sem fuso vindos do banco, lança `TypeError`; convertido em texto, ganha o sufixo `+00:00` e muda a resposta. Quando o projeto guarda e devolve UTC sem fuso, use o helper acima em todos os pontos.
- Em colunas do ORM, passe a função como `default` (sem chamar), como no original.
- Depois da troca, rode a aplicação com avisos ligados (`python -W default`, `node --trace-deprecation`) e confirme que os avisos sumiram.
- Atualizar versão de dependência é outra tarefa: só altere versões se o projeto não instala ou não sobe sem isso, e registre no resumo final.

## T-15 — Converter callbacks em async/await

**Resolve:** AP-18, parte de AP-15

Embrulhe a API de callbacks em promises uma única vez e reescreva o fluxo de forma linear.

Antes (JavaScript):

```js
app.get('/api/report', (req, res) => {
  const report = [];
  db.all('SELECT * FROM books', [], (err, books) => {
    let pending = books.length;
    books.forEach((book) => {
      db.all('SELECT * FROM loans WHERE book_id = ?', [book.id], (err, loans) => {
        report.push({ title: book.title, loans: loans.length });
        pending--;
        if (pending === 0) res.json(report);
      });
    });
  });
});
```

Depois:

```js
// database/connection.js — promises sobre o driver de callbacks
function createConnection(path) {
  const raw = new sqlite3.Database(path);
  return {
    run: (sql, params = []) => new Promise((resolve, reject) => {
      raw.run(sql, params, function (err) {
        if (err) reject(err);
        else resolve({ lastID: this.lastID, changes: this.changes });
      });
    }),
    get: (sql, params = []) => new Promise((resolve, reject) => {
      raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    }),
    all: (sql, params = []) => new Promise((resolve, reject) => {
      raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    }),
  };
}
```

```js
// models/reportModel.js — uma query, ordem definida
async function loansPerBook(db) {
  return db.all(
    `SELECT b.title, COUNT(l.id) AS loans
       FROM books b
       LEFT JOIN loans l ON l.book_id = b.id
      GROUP BY b.id
      ORDER BY b.id`,
  );
}
```

Notas:

- Callbacks que usam `this` (como `this.lastID`) precisam de `function`, não de arrow function, dentro do wrapper.
- Quando a ordem do resultado dependia de qual callback terminava primeiro, defina a ordem natural (`ORDER BY` pelo id) e registre a ordem estável em `Behavior Changes`.
- Erros que antes eram ignorados passam a rejeitar a promise e chegam ao handler central (T-12).
- Não misture estilos: o fluxo convertido usa `async/await` de ponta a ponta.

## T-16 — Limpeza de legibilidade

**Resolve:** AP-19, AP-20, AP-21, AP-22

Dê nome ao que tem significado, registre com um logger e apague o que não é usado.

Antes (Python):

```python
import os, sys, json

def calc(o):
    d = 0
    if o.total > 10000:
        d = o.total * 0.1
    elif o.total > 5000:
        d = o.total * 0.05
    print("desconto: " + str(d))
    if o.status in ["pending", "approved", "shipped"]:
        return True
    else:
        return False
```

Depois:

```python
import logging

logger = logging.getLogger(__name__)

DISCOUNT_TIERS = ((10000, 0.10), (5000, 0.05))  # (total mínimo, percentual)
OPEN_STATUSES = ("pending", "approved", "shipped")


def discount_for(total):
    for minimum_total, rate in DISCOUNT_TIERS:
        if total > minimum_total:
            return total * rate
    return 0


def is_open(order):
    logger.debug("desconto: %s", discount_for(order.total))
    return order.status in OPEN_STATUSES
```

Notas:

- **Constantes:** valores de regra (faixas, limites, listas de status e papéis) ganham nome e ficam junto do model ou em um módulo de constantes. Se o projeto já tem constantes definidas e não usadas, use-as.
- **Nomes:** renomeie variáveis e funções internas. Campos do contrato da API (corpo, query string, resposta) e colunas do banco ficam como estão.
- **Log:** use o logger da linguagem ou do framework (`logging`, `app.logger`); em Node sem biblioteca de log, concentre a saída em um módulo `logger` pequeno em vez de adicionar dependência. Nada de dado sensível no log (T-04).
- **Código morto:** remova imports, funções, variáveis e dependências sem uso. Antes de apagar uma função, procure o nome no projeto inteiro, incluindo seeds e testes. Isso inclui serviços e helpers sem chamador cujo uso seria funcionalidade nova (enviar um email que hoje não é enviado): eles são removidos, e a Recommendation diz "remover". A exceção é o helper que implementa exatamente uma regra hoje duplicada em outro lugar; esse passa a ser usado (T-07, T-13).
- **Verbosidade:** `if x: return True else: return False` vira `return x`; `type(v) == list` vira `isinstance(v, list)`.
- Esta transformação vem por último, depois que a estrutura está validada. Assim, uma regressão no smoke test aponta para a mudança estrutural e não para um rename.

---

## T-17 — Autenticação e autorização por padrão

**Resolve:** AP-11, a escalação de privilégio e a parte de AP-04 e AP-06 que vem de rotas sem identidade

Autenticação ausente é corrigida nesta refatoração, mesmo mudando o contrato. Um Impact como "qualquer cliente lista os pedidos de todos" só deixa de acontecer quando a rota exige credencial; proteger só as rotas administrativas, ou deixar o guard pronto e desligado, deixa o Impact acontecendo. A correção tem quatro partes.

### 1. Uma política para cada rota

Monte uma tabela com todas as rotas do inventário da Fase 1 e a política de cada uma. Nenhuma rota fica sem política, e toda rota citada num finding de autenticação, exposição ou privilégio recebe a política que elimina o Impact descrito. Na dúvida entre duas, use a mais restrita.

| Política | Quem acessa | Rotas típicas |
|---|---|---|
| pública | qualquer cliente | login, cadastro público, health, índice, leitura de catálogo que não expõe dados de pessoas nem valores financeiros |
| dono ou admin | o usuário dono do recurso, identificado pelo token, ou um administrador | perfil, pedidos, tarefas, matrículas de um usuário |
| admin | só administradores | criar, alterar e apagar catálogo, usuários e papéis; listagens de todos os usuários ou pedidos; relatórios gerenciais e financeiros; operações administrativas |

A tabela entra na Recommendation do finding de autenticação e em `Behavior Changes`.

### 2. Credencial assinada no login

O login passa a devolver um token assinado com a `SECRET_KEY` e com validade, num campo novo da resposta (`token`). Os campos que a resposta já tinha continuam iguais. Token fixo ou previsível (`"fake-token-" + id`) é substituído pelo assinado. Não precisa de dependência nova: o Flask já instala o `itsdangerous`, e o Node tem `node:crypto`.

Quando o projeto não tem login de usuário (nenhuma rota emite credencial), as rotas de admin usam `ADMIN_TOKEN` do ambiente (T-06) e as rotas de cliente seguem as regras de negócio do domínio (por exemplo, conferir a senha da conta existente antes de usá-la).

### 3. Um guard só, que nega por padrão

Um middleware lê `Authorization: Bearer <token>`, valida assinatura e validade e carrega o usuário do banco. O papel vem do banco a cada requisição, nunca do token, para que rebaixar alguém tenha efeito imediato. Sem credencial válida, 401; com papel insuficiente, 403; os dois no envelope de erro da API. O dono de um recurso vem do token: um `usuario_id` enviado no corpo ou na URL precisa ser o do token, a menos que quem pede seja admin.

### 4. Privilégio só pelo servidor

O cadastro público grava sempre o papel padrão, ignorando o papel enviado. Só um admin autenticado define ou altera papéis; quem não é admin e tenta alterar o próprio papel recebe 403.

Antes (Python):

```python
@readers_bp.route("/login", methods=["POST"])
def login():
    reader = reader_model.find_by_credentials(request.json["email"], request.json["password"])
    if reader is None:
        return jsonify({"error": "Credenciais inválidas"}), 401
    return jsonify({"data": reader, "token": "token-" + str(reader["id"])}), 200


@loans_bp.route("/loans", methods=["GET"])
def list_loans():                      # qualquer cliente lê os empréstimos de todos
    return jsonify(loan_model.find_all()), 200


@readers_bp.route("/readers", methods=["POST"])
def create_reader():                   # qualquer cliente se cadastra como admin
    return jsonify(reader_service.create(**request.json)), 201
```

Depois:

```python
# middlewares/auth.py
from functools import wraps

from flask import current_app, g, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from middlewares.errors import ForbiddenError, UnauthorizedError
from models import reader_model

TOKEN_MAX_AGE_SECONDS = 8 * 60 * 60
ADMIN_ROLE = "admin"


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="auth-token")


def issue_token(reader_id):
    return _serializer().dumps({"uid": reader_id})


def _authenticated_reader():
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme != "Bearer" or not token:
        return None
    try:
        claims = _serializer().loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None
    return reader_model.find_by_id(claims["uid"])  # papel lido do banco


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        reader = _authenticated_reader()
        if reader is None:
            raise UnauthorizedError("Autenticação necessária")
        g.current_reader = reader
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @login_required
    @wraps(view)
    def wrapper(*args, **kwargs):
        if g.current_reader["role"] != ADMIN_ROLE:
            raise ForbiddenError("Acesso negado")
        return view(*args, **kwargs)
    return wrapper


def ensure_owner_or_admin(owner_id):
    reader = g.current_reader
    if reader["role"] != ADMIN_ROLE and reader["id"] != owner_id:
        raise ForbiddenError("Acesso negado")
```

```python
# routes: a política de cada rota fica visível no registro
readers_bp.add_url_rule("/login", view_func=reader_controller.login, methods=["POST"])            # pública
readers_bp.add_url_rule("/readers", view_func=reader_controller.create, methods=["POST"])         # pública
loans_bp.add_url_rule("/loans", view_func=admin_required(loan_controller.list_all), methods=["GET"])
loans_bp.add_url_rule("/readers/<int:reader_id>/loans",
                      view_func=login_required(loan_controller.list_by_reader), methods=["GET"])
```

```python
# controllers
def login():
    email, password = validation.require_credentials(request.get_json(silent=True))
    reader = auth_service.authenticate(email, password)
    if reader is None:
        raise UnauthorizedError("Credenciais inválidas")
    return jsonify({"data": reader, "token": issue_token(reader["id"])}), 200


def list_by_reader(reader_id):
    ensure_owner_or_admin(reader_id)
    return jsonify(loan_model.find_by_reader(reader_id)), 200


def create():
    data = validation.require_reader(request.get_json(silent=True))
    data["role"] = DEFAULT_ROLE          # o papel enviado no cadastro público é ignorado
    return jsonify(reader_service.create(**data)), 201
```

Em Node.js, o mesmo com `node:crypto`:

```js
// middlewares/auth.js
const { createHmac, timingSafeEqual } = require('node:crypto');

const TOKEN_TTL_MS = 8 * 60 * 60 * 1000;

function createAuth({ secret, readerModel }) {
  const sign = (payload) => createHmac('sha256', secret).update(payload).digest('base64url');

  function issueToken(readerId) {
    const payload = Buffer.from(JSON.stringify({ uid: readerId, exp: Date.now() + TOKEN_TTL_MS }))
      .toString('base64url');
    return `${payload}.${sign(payload)}`;
  }

  async function authenticatedReader(req) {
    const [scheme, token] = (req.get('authorization') || '').split(' ');
    if (scheme !== 'Bearer' || !token) return null;
    const [payload, signature] = token.split('.');
    if (!payload || !signature) return null;
    const expected = Buffer.from(sign(payload));
    const received = Buffer.from(signature);
    if (expected.length !== received.length || !timingSafeEqual(expected, received)) return null;
    const { uid, exp } = JSON.parse(Buffer.from(payload, 'base64url').toString());
    if (Date.now() > exp) return null;
    return readerModel.findById(uid); // papel lido do banco
  }

  const requireReader = asyncHandler(async (req, res, next) => {
    req.reader = await authenticatedReader(req);
    if (!req.reader) throw new UnauthorizedError('Autenticação necessária');
    next();
  });

  const requireAdmin = [requireReader, (req, res, next) => {
    if (req.reader.role !== 'admin') throw new ForbiddenError('Acesso negado');
    next();
  }];

  return { issueToken, requireReader, requireAdmin };
}
```

Notas:

- **Nega por padrão, sempre ligado.** Não existe flag que desligue o guard nem modo "auth opcional". Sem `SECRET_KEY` no ambiente, a chave efêmera do T-02 assina e valida os tokens; eles só deixam de valer quando o processo reinicia. Controle de segurança desligado por padrão é controle ausente.
- **401 e 403 com o envelope da API.** Use as exceções de domínio do T-12 (`UnauthorizedError` 401, `ForbiddenError` 403), com a mesma chave de erro do resto da API.
- **O seed precisa ter um admin** com senha conhecida, para que as rotas de admin possam ser exercitadas; o README do projeto passa a dizer como obter o token (login com esse usuário).
- **Smoke test com credencial.** O arquivo de requisições faz login como admin e como usuário comum e captura os tokens (`capture`, veja "Smoke test"). Cada rota protegida aparece três vezes: sem token (`expect_change`: 401), com o token de papel insuficiente (`expect_change`: 403) e com o token certo, que precisa devolver a resposta original.
- **CORS:** se um finding cita CORS aberto, as origens permitidas passam a vir de `CORS_ORIGINS` e, sem a variável, nenhuma origem externa é liberada.

## Limites da refatoração

A refatoração não faz, sem pedido explícito, mudanças que não eliminam nenhum Impact:

- **Padronizar o formato de resposta** (texto puro para JSON, novo envelope). Clientes analisam o formato atual.
- **Renomear campos do contrato**, mesmo que ruins.
- **Trocar de banco, de framework ou fazer atualização maior de dependência.**

Quando uma dessas mudanças for o único jeito de eliminar um Impact, ela entra na Recommendation, é aplicada e vai para `Behavior Changes`.

Nada de segurança entra nesta lista. Autenticação e autorização das rotas citadas (T-17), fim da escalação de privilégio, remoção de rotas que executam código recebido (T-06), tratamento de dependentes na exclusão (T-10), validação recomendada (T-11), validações divergentes (T-13), estado em memória (T-08) e código sem uso (T-16) são aplicados por inteiro, mesmo quando mudam o contrato.

Quando a pessoa, ao confirmar a Fase 2, pede para excluir uma Recommendation, ela não é aplicada e aparece em `Not applied` no resumo final, com a ressalva.
