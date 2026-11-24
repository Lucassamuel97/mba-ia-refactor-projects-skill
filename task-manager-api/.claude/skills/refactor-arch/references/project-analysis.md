# Análise de projeto (Fase 1)

Heurísticas para descobrir a stack, o banco de dados, o domínio e a arquitetura atual de um projeto que você nunca viu. O resultado alimenta as outras duas fases: a auditoria precisa saber quais sinais procurar nessa stack, e a refatoração precisa do inventário de rotas para provar que nada quebrou.

A Fase 1 é somente leitura. Não instale dependências, não suba a aplicação e não crie arquivos nela.

## Conteúdo

1. [Arquivos que contam](#1-arquivos-que-contam)
2. [Linguagem e runtime](#2-linguagem-e-runtime)
3. [Framework e dependências](#3-framework-e-dependências)
4. [Banco de dados](#4-banco-de-dados)
5. [Inventário de rotas](#5-inventário-de-rotas)
6. [Mapa de responsabilidades](#6-mapa-de-responsabilidades)
7. [Classificação da arquitetura](#7-classificação-da-arquitetura)
8. [Domínio](#8-domínio)
9. [Como a aplicação roda](#9-como-a-aplicação-roda)
10. [Formato do resumo](#10-formato-do-resumo)

## 1. Arquivos que contam

Conte e leia os arquivos de código-fonte escritos pela equipe do projeto. O número impresso no resumo precisa bater com o que uma pessoa contaria olhando a árvore.

Fora da contagem:

- Dependências e ambientes: `node_modules/`, `.venv/`, `venv/`, `vendor/`, `target/`, `dist/`, `build/`, `__pycache__/`
- Controle de versão e ferramentas: `.git/`, `.claude/`, `.gemini/`, `.codex/`, `.idea/`, `.vscode/`
- Arquivos gerados ou de dados: lockfiles, bancos locais (`*.db`, `*.sqlite`), `.env`
- Documentação e exemplos de requisição (`*.md`, `*.http`): leia, porque ajudam a entender o projeto, mas não conte como código

Em um repositório git, a lista de arquivos versionados já respeita o `.gitignore`:

```bash
git ls-files -- . ':!.claude' | grep -Ev '\.(md|http|json|lock|txt|toml|ya?ml)$'
```

Sem git, liste com exclusões:

```bash
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' \) \
  -not -path './node_modules/*' -not -path './.venv/*' -not -path './venv/*' \
  -not -path './.git/*' -not -path './.claude/*' -not -path './dist/*' -not -path './build/*'
```

Ajuste as extensões à linguagem detectada. Conte as linhas com `wc -l` sobre a mesma lista e arredonde no resumo (`~800 lines`).

Leia todos os arquivos contados, por inteiro. Projetos legados escondem o pior nos arquivos de nome inocente (`utils`, `helpers`, `database`), então amostragem não serve aqui.

## 2. Linguagem e runtime

O manifesto de dependências é o sinal mais confiável.

| Arquivo na raiz | Linguagem | Gerenciador |
|---|---|---|
| `package.json` | JavaScript ou TypeScript (Node.js) | npm, yarn, pnpm (veja o lockfile) |
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py` | Python | pip, poetry, pipenv |
| `pom.xml`, `build.gradle`, `build.gradle.kts` | Java ou Kotlin | Maven, Gradle |
| `go.mod` | Go | go modules |
| `Gemfile` | Ruby | bundler |
| `composer.json` | PHP | composer |
| `*.csproj`, `*.sln` | C# (.NET) | dotnet |
| `Cargo.toml` | Rust | cargo |

Regras de desempate:

- Sem manifesto, decida pela extensão predominante entre os arquivos contados.
- `tsconfig.json` ou arquivos `.ts` indicam TypeScript, mesmo com `package.json`.
- Mais de um manifesto (ex.: API em Python e front em Node) significa mais de um projeto; analise o que contém o backend e diga isso no resumo.

Registre a versão do runtime quando o projeto a declara (`engines` no `package.json`, `python_requires`, `.python-version`, `.nvmrc`, `go` no `go.mod`). Ela importa para a detecção de APIs deprecated.

## 3. Framework e dependências

Procure o framework nas dependências declaradas e confirme pelos imports do entry point. A versão vem do manifesto; se ele usa faixa (`^4.18.2`), use o lockfile para a versão exata e, sem lockfile, informe a faixa.

| Sinal (dependência ou import) | Framework |
|---|---|
| `flask`, `from flask import Flask` | Flask |
| `fastapi`, `FastAPI()` | FastAPI |
| `django`, `manage.py`, `settings.py` | Django |
| `express`, `require('express')` | Express |
| `@nestjs/core` | NestJS |
| `fastify`, `koa`, `@hapi/hapi` | Fastify, Koa, Hapi |
| `spring-boot-starter-web` | Spring Boot |
| `gin-gonic/gin`, `labstack/echo`, `net/http` | Gin, Echo, biblioteca padrão do Go |
| `rails`, `sinatra` | Rails, Sinatra |
| `laravel/framework`, `slim/slim` | Laravel, Slim |
| `Microsoft.AspNetCore` | ASP.NET Core |

No resumo, `Dependencies` lista as demais dependências diretas relevantes (CORS, ORM, validação, autenticação, driver de banco), sem repetir o framework.

Anote também dependências declaradas e nunca importadas, e imports sem declaração no manifesto. Os dois casos viram findings.

## 4. Banco de dados

Descubra três coisas: qual banco, como o código fala com ele e onde o schema é definido.

| Sinal | Conclusão |
|---|---|
| `sqlite3`, `better-sqlite3`, arquivo `*.db`, `:memory:` | SQLite |
| `psycopg2`, `asyncpg`, `pg`, `postgres://` | PostgreSQL |
| `mysqlclient`, `pymysql`, `mysql2`, `mysql://` | MySQL ou MariaDB |
| `pymongo`, `mongoose`, `mongodb://` | MongoDB |
| `redis`, `ioredis` | Redis |
| `sqlalchemy`, `flask_sqlalchemy`, `django.db`, `peewee` | ORM em Python |
| `sequelize`, `typeorm`, `prisma`, `knex`, `mongoose` | ORM ou query builder em Node |
| `hibernate`, `spring-data-jpa`, `gorm`, `ActiveRecord`, `Eloquent`, `EntityFramework` | ORM em outras stacks |

Para listar as tabelas ou coleções:

- SQL escrito à mão: procure `CREATE TABLE` e os nomes após `FROM`, `INTO`, `UPDATE`, `JOIN`.
- ORM: procure as classes de modelo e o nome de tabela declarado (`__tablename__`, `@Entity`, `tableName`, `Meta.db_table`).
- Migrations: leia a pasta de migrations (`migrations/`, `alembic/`, `prisma/schema.prisma`, `db/migrate/`).

Registre onde a conexão é criada e quem a guarda (variável global, singleton, objeto por requisição, injeção), e se o banco é local e descartável (arquivo SQLite, memória) ou externo. Isso decide, na Fase 3, se é seguro rodar requisições que alteram dados.

## 5. Inventário de rotas

Liste todas as rotas HTTP: método, caminho e a função que atende. Esse inventário é o contrato que a refatoração precisa preservar e a base do smoke test da Fase 3, então uma rota esquecida aqui é uma rota que pode quebrar sem ninguém notar.

Padrões de busca por framework:

| Framework | Onde as rotas aparecem |
|---|---|
| Flask | `@app.route(`, `@<blueprint>.route(`, `.get(`/`.post(` como decorator, `add_url_rule(`, `register_blueprint(..., url_prefix=` |
| FastAPI | `@app.get(`, `@router.post(`, `include_router(..., prefix=` |
| Django | `urlpatterns`, `path(`, `re_path(`, `include(` |
| Express, Koa, Fastify | `app.get(`, `router.post(`, `app.use('/prefixo', router)` |
| NestJS | `@Controller(`, `@Get(`, `@Post(` |
| Spring | `@RequestMapping`, `@GetMapping`, `@PostMapping` |
| Go | `http.HandleFunc(`, `r.GET(`, `e.POST(` |
| Rails | `config/routes.rb` |
| Laravel | `routes/*.php`, `Route::get(` |
| ASP.NET Core | `[HttpGet]`, `app.MapGet(` |

Cuidados:

- Componha os prefixos: um router montado em `/api` com rota `/users` atende em `/api/users`.
- Rotas registradas fora do arquivo de rotas (no entry point, em um arquivo de "admin") costumam ser as mais perigosas. Procure os padrões no projeto inteiro, não só na pasta `routes`.
- Arquivos de exemplo (`*.http`, coleções do Postman, README) mostram os payloads esperados; use-os para montar o smoke test.

## 6. Mapa de responsabilidades

Para cada arquivo de código, anote quais destas responsabilidades ele exerce:

| Responsabilidade | Como reconhecer |
|---|---|
| Roteamento | Declaração de rotas, registro de routers ou blueprints |
| Tratamento de requisição | Lê `request`/`req`, monta a resposta HTTP, define status code |
| Validação de entrada | Checagens de presença, tipo, formato e faixa dos dados recebidos |
| Regra de negócio | Cálculos, decisões, fluxos (preço, estoque, desconto, status, permissões) |
| Acesso a dados | SQL, chamadas ao ORM, abertura de conexão, transações |
| Serialização | Conversão de linhas ou objetos em dicionários ou JSON de resposta |
| Configuração | Segredos, portas, URLs, flags |
| Infraestrutura | Criação de schema, seed, log, cache, envio de email |
| Composição | Criação da aplicação, ligação das camadas, início do servidor |

Um arquivo com três ou mais responsabilidades de naturezas diferentes (por exemplo roteamento, regra de negócio e acesso a dados) é candidato a God Class. Pastas ou arquivos com nome de camada (`models`, `controllers`, `services`) só contam como camada se o conteúdo corresponder ao nome; confira o conteúdo.

Anote também o que existe e não é usado: helpers, métodos de modelo, serviços e constantes que ninguém importa. Em projetos parcialmente organizados é comum a camada certa existir e a lógica ter sido reescrita em outro lugar.

## 7. Classificação da arquitetura

Use o mapa de responsabilidades para enquadrar o projeto em um destes níveis. O nível define o tamanho da refatoração na Fase 3.

| Nível | Característica | O que a Fase 3 faz |
|---|---|---|
| Monolítica | Uma ou poucas unidades concentram rotas, regra e dados | Cria a estrutura MVC completa |
| Camadas nominais | Há arquivos com nome de camada, mas o conteúdo é misturado ou um arquivo único serve todos os domínios | Divide por domínio e move cada trecho para a camada certa |
| Parcialmente em camadas | Pastas por camada existem e parte do código as respeita, mas faltam camadas ou elas são ignoradas | Mantém o que está certo, cria o que falta e realoca o que está fora do lugar |
| MVC adequado | Camadas completas e respeitadas | Só corrige os findings pontuais |

Descreva a arquitetura no resumo em uma frase concreta, com números quando ajudarem: "Monolítica — tudo em 4 arquivos, sem separação de camadas" ou "Parcialmente em camadas — models e routes separados, regra de negócio dentro das rotas, sem controllers".

## 8. Domínio

Descreva em uma linha o que a aplicação faz, com as entidades principais entre parênteses. As pistas estão nos nomes de tabelas, nos caminhos das rotas, nos nomes de modelos e no README.

Descreva pelo que o código faz, não pelo nome da pasta: um projeto chamado `blog-api` que agenda consultas e cobra pacientes é um sistema de agendamento com cobrança.

## 9. Como a aplicação roda

Levante o que a Fase 3 vai precisar para subir a aplicação:

- Comando de start (`scripts.start` no `package.json`, `python app.py`, `flask run`, README, `Procfile`, `Dockerfile`)
- Porta e host (literal no código, variável de ambiente, padrão do framework)
- Passos anteriores ao boot: instalação de dependências, seed, migrations
- Variáveis de ambiente lidas pelo código
- Outros arquivos que importam módulos do projeto (scripts de seed, testes, tarefas agendadas), porque eles quebram se um módulo mudar de lugar
- Testes automatizados existentes e como rodá-los

## 10. Formato do resumo

Imprima exatamente este bloco ao fim da Fase 1. Os rótulos são fixos; os valores vão no idioma da conversa.

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem e versão do runtime, se declarada>
Framework:     <framework e versão>
Dependencies:  <demais dependências diretas relevantes>
Database:      <banco e forma de acesso, ex.: SQLite via sqlite3, sem ORM>
Domain:        <o que a aplicação faz (entidades principais)>
Architecture:  <nível da classificação — frase concreta>
Entry point:   <arquivo e comando de start>
Source files:  <n> files analyzed | ~<linhas> lines of code
Endpoints:     <n> routes
DB tables:     <tabelas ou coleções>
================================
```

Exemplo preenchido:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js 20)
Framework:     Express 4.19.2
Dependencies:  pg, cors, jsonwebtoken
Database:      PostgreSQL via pg, sem ORM
Domain:        API de biblioteca (livros, leitores, empréstimos)
Architecture:  Monolítica — rotas, regras e SQL em um único server.js de 600 linhas
Entry point:   server.js (npm start)
Source files:  3 files analyzed | ~750 lines of code
Endpoints:     14 routes
DB tables:     books, readers, loans
================================
```

Se algum item não puder ser determinado, escreva `não identificado` e diga o que faltou. Um valor inventado aqui contamina as duas fases seguintes.
