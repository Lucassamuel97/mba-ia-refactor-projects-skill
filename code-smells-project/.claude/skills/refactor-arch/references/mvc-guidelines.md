# Guidelines de arquitetura MVC (Fase 3)

O padrão alvo da refatoração: quais camadas existem, o que cabe em cada uma e como elas dependem umas das outras. Vale para qualquer linguagem e framework; as seções finais mostram como adaptar à convenção de cada stack e ao ponto de partida do projeto.

## Conteúdo

1. [Estrutura alvo](#1-estrutura-alvo)
2. [Responsabilidade de cada camada](#2-responsabilidade-de-cada-camada)
3. [Regra de dependência](#3-regra-de-dependência)
4. [Onde vai cada tipo de código](#4-onde-vai-cada-tipo-de-código)
5. [Contrato HTTP a preservar](#5-contrato-http-a-preservar)
6. [Adaptação ao ponto de partida](#6-adaptação-ao-ponto-de-partida)
7. [Convenções por stack](#7-convenções-por-stack)
8. [Checklist da estrutura final](#8-checklist-da-estrutura-final)

## 1. Estrutura alvo

```
<raiz do código>/
├── config/         configuração lida do ambiente
├── models/         dados e regras de cada entidade, um módulo por domínio
├── controllers/    fluxo de cada requisição, um módulo por domínio
├── views/ ou routes/   mapeamento HTTP e formato das respostas
├── services/       (opcional) regras que cruzam entidades e integrações externas
├── middlewares/    tratamento de erro central, guards de acesso
└── <entry point>   composition root: monta e inicia a aplicação
```

Em uma API, a View é a face HTTP: as rotas e a forma como os dados viram resposta (JSON). Use o nome que a stack e o projeto já usam (`routes/` é o mais comum em APIs; `views/` também serve). O que importa é a camada existir, separada das outras.

`services/` é opcional. Crie quando houver regra que envolve mais de uma entidade (fechamento de uma compra, relatórios) ou integração externa (pagamento, email). Em um CRUD simples, controller e model bastam, e uma camada vazia só adiciona indireção.

## 2. Responsabilidade de cada camada

### Models

- Representam as entidades do domínio e são o único lugar que fala com o banco: SQL, chamadas ao ORM, transações.
- Guardam as regras que pertencem a uma entidade (um empréstimo sabe dizer se está atrasado; uma fatura sabe calcular o próprio total).
- Recebem e devolvem dados puros (objetos, dicionários, tipos da linguagem).
- Não conhecem HTTP: não importam `request`/`response`, não escolhem status code, não montam JSON de resposta.

### Views / Routes

- Declaram as rotas: método, caminho e qual função do controller atende.
- Definem o formato de saída (serializadores, campos públicos de cada entidade).
- Aplicam middlewares específicos de rota (guard de acesso, por exemplo).
- Não têm lógica: uma rota com `if` de regra de negócio está no lugar errado.

### Controllers

- Conduzem o fluxo de uma requisição: extraem os dados da requisição, validam a entrada, chamam models ou services e escolhem a resposta e o status code.
- Traduzem resultados e erros de domínio para HTTP (não encontrado vira 404, entrada inválida vira 400).
- São finos: sem SQL, sem cálculo de regra de negócio, sem laços de agregação. Quando um método de controller cresce, a lógica pertence a um model ou service.

### Services (opcional)

- Implementam casos de uso que cruzam entidades e coordenam várias operações de model em uma transação.
- Encapsulam integrações externas atrás de uma função ou classe substituível.
- Recebem as dependências de quem os cria; não as instanciam por conta própria.
- Não conhecem HTTP, como os models.

### Config

- Lê do ambiente tudo o que varia entre ambientes ou é segredo: chaves, credenciais, URL do banco, porta, flags de debug.
- É o único lugar que lê variáveis de ambiente. O resto do código recebe valores já resolvidos.
- Nenhum segredo literal; valores padrão só para o que não é sensível.

### Middlewares

- Tratamento de erro central: converte exceções em respostas, registra o erro e não vaza detalhes internos.
- Guards de acesso para rotas que exigem proteção.
- Outras preocupações transversais (log de requisição, CORS).

### Entry point (composition root)

- Cria a aplicação, carrega a configuração, inicializa o banco, registra rotas e middlewares e inicia o servidor.
- É o único lugar que conhece todas as camadas e as conecta.
- Não tem rota, regra nem SQL próprios.

## 3. Regra de dependência

As dependências apontam em um só sentido:

```
entry point → routes/views → controllers → services → models
                                   └──────────────────────┘
config e middlewares podem ser usados por qualquer camada
```

- Uma camada nunca importa a camada que está acima dela. Um model que importa um controller indica lógica no lugar errado.
- Models não importam o framework web. Isso é o que permite testá-los sem subir um servidor.
- Dependências de infraestrutura (conexão, clientes externos) são criadas na composição e entregues a quem precisa, por parâmetro, construtor ou pelo mecanismo de contexto do framework.

## 4. Onde vai cada tipo de código

| Código encontrado | Destino |
|---|---|
| Declaração de rota | routes/views |
| Leitura de corpo, query string e parâmetros de rota | controller |
| Validação de presença, tipo, formato e faixa da entrada | controller, ou módulo de validação chamado por ele |
| Escolha de status code e montagem da resposta | controller, com os serializadores da view |
| Lista de campos públicos de uma entidade | view (serializador) ou método de serialização do model, sem campos sensíveis |
| SQL, chamadas ao ORM, transação | model |
| Regra de uma entidade (cálculo, estado, transição válida) | model |
| Regra que envolve várias entidades | service |
| Chamada a gateway, email, API externa | service |
| Segredos, URLs, portas, flags | config |
| `try/except` genérico repetido em cada handler | middleware de erro |
| Verificação de token ou permissão | middleware/guard |
| Criação de schema e seed | módulo de banco, chamado pela composição ou por script próprio |
| Constantes de domínio (status válidos, limites) | junto do model da entidade ou em um módulo de constantes |
| Criação da aplicação e início do servidor | entry point |

## 5. Contrato HTTP a preservar

A refatoração muda a organização interna, não a API. Clientes existentes devem continuar funcionando sem alteração.

Preserve:

- Caminho e método de todas as rotas do inventário da Fase 1.
- Status codes e formato do corpo das respostas de sucesso e de erro de validação (mesmas chaves, mesmo envelope, mesmas mensagens).
- Nomes dos campos de entrada, mesmo que sejam ruins. Nomes internos podem melhorar; o contrato não.
- A ordem de registro das rotas quando o framework resolve por ordem (rota fixa antes de rota com parâmetro).
- O comando de start e a porta padrão.
- Os dados de seed e o schema, para que o estado inicial seja o mesmo.

Podem mudar, e toda mudança entra em `Behavior Changes` no resumo final:

- Campos sensíveis deixam de aparecer nas respostas.
- Tentativas de injeção deixam de funcionar.
- Operações perigosas passam a exigir proteção.
- Erros internos passam a devolver mensagem genérica, sem detalhes da exceção.
- Entradas inválidas que causavam erro 500 passam a devolver 400.

Qualquer outra diferença de comportamento é um defeito da refatoração.

## 6. Adaptação ao ponto de partida

Use a classificação da Fase 1. A meta é o projeto terminar no padrão acima com a menor mudança que resolve os findings, não reescrever o que já está certo.

| Ponto de partida | Estratégia |
|---|---|
| Monolítica | Crie a estrutura completa. Extraia na ordem config, models, services, controllers, routes, middlewares, entry point. |
| Camadas nominais | Transforme cada arquivo único em um pacote com um módulo por domínio e mova cada trecho para a camada que corresponde ao que ele faz. |
| Parcialmente em camadas | Mantenha as pastas e os nomes que já funcionam. Crie só as camadas que faltam, tire a lógica das rotas, realoque módulos que estão no arquivo errado e passe a usar (ou remova) helpers e métodos que existem e ninguém chama. |
| MVC adequado | Não reestruture. Corrija os findings no lugar. |

Regras para qualquer ponto de partida:

- **Respeite as convenções do projeto.** Idioma dos identificadores, estilo de nomes de arquivo, raiz do código (`src/` ou raiz do repositório) e sistema de módulos continuam os mesmos.
- **Não renomeie por gosto.** Uma pasta `routes/` que cumpre o papel de view não precisa virar `views/`.
- **Não troque de tecnologia.** Sem trocar de framework, introduzir ORM onde havia SQL ou mudar o banco. Dependências novas só quando não houver alternativa na biblioteca padrão ou no que o projeto já usa.
- **Um módulo por domínio em cada camada** (`models/book`, `controllers/book`), em vez de um arquivo gigante por camada.
- **Sem cópias antigas.** O arquivo que foi dividido ou substituído é removido; código morto que sobra vira o próximo legado.

## 7. Convenções por stack

O mecanismo muda, a divisão é a mesma.

| Stack | Routes/Views | Entry point | Erro central | Recurso por requisição |
|---|---|---|---|---|
| Flask | `Blueprint` por domínio em `routes/` | `app.py` com `create_app()` | `@app.errorhandler` | `flask.g` com `teardown_appcontext` |
| FastAPI | `APIRouter` por domínio | `main.py` | `@app.exception_handler` | `Depends` |
| Django | `urls.py` e views por app | `manage.py`, `wsgi.py` | middleware | ORM gerencia |
| Express | `express.Router()` por domínio em `routes/` | `app.js` ou `server.js` | middleware de 4 argumentos, registrado por último | injeção por construtor ou closure |
| NestJS | `@Controller` em módulos | `main.ts` | exception filter | providers |
| Spring Boot | `@RestController` | classe `@SpringBootApplication` | `@ControllerAdvice` | injeção do container |

Notas:

- Em frameworks onde "view" já significa outra coisa (Django, NestJS), siga o vocabulário do framework e mantenha a mesma separação de responsabilidades.
- Em Flask, mantenha um objeto `app` importável no módulo do entry point se outros arquivos do projeto o importam (scripts de seed, testes, servidor WSGI).
- Em Express 4, handlers `async` precisam encaminhar a exceção ao `next`; use um wrapper. No Express 5 isso é automático.

## 8. Checklist da estrutura final

Confira antes de declarar a Fase 3 concluída:

- [ ] Existe um módulo de config, e nenhum segredo literal fora dele (nem dentro dele)
- [ ] Todo acesso a dados está nos models
- [ ] Nenhum model ou service importa objetos de requisição ou resposta
- [ ] As rotas só mapeiam caminho para controller
- [ ] Os controllers não contêm SQL nem regra de negócio
- [ ] Existe um tratamento de erro central, e os `try/except` genéricos repetidos saíram dos handlers
- [ ] O entry point só compõe e inicia
- [ ] Nenhuma camada importa a camada acima dela
- [ ] Cada camada tem um módulo por domínio
- [ ] Os arquivos antigos substituídos foram removidos
- [ ] Todo arquivo que importava um módulo movido foi atualizado (seed, testes, scripts)
- [ ] O comando de start documentado continua funcionando
