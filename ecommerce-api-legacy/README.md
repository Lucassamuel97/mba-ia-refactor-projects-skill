# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

## Configuração

Variáveis de ambiente (veja `.env.example`); nenhuma é obrigatória para subir:

- `PORT`: porta HTTP (padrão 3000).
- `ADMIN_TOKEN`: token das rotas administrativas. Sem ele, essas rotas respondem 403 a todos os pedidos.

```bash
ADMIN_TOKEN=um-token-aleatorio npm start
```

## Rotas

| Rota | Acesso |
|---|---|
| `POST /api/checkout` | pública; `usr`, `eml`, `pwd`, `c_id` e `card` são obrigatórios. Se o email já tem conta, `pwd` precisa ser a senha dela (senão 401) |
| `GET /api/admin/financial-report` | admin: cabeçalho `X-Admin-Token: <ADMIN_TOKEN>` |
| `DELETE /api/users/:id` | admin: cabeçalho `X-Admin-Token: <ADMIN_TOKEN>`; responde 409 se o usuário tem matrículas |

Sem o cabeçalho, as rotas de admin respondem 401; com token errado (ou sem `ADMIN_TOKEN` configurado), 403.

## Estrutura

```
src/
├── app.js            composition root
├── config/           configuração lida do ambiente
├── database/         conexão (promises + transações) e schema/seed
├── models/           SQL por entidade
├── services/         checkout, gateway de pagamento, relatório, usuários
├── controllers/      fluxo HTTP e validação de entrada
├── routes/           mapeamento das rotas
├── middlewares/      erro central, asyncHandler, guard de admin
└── utils/            erros, logger, hash de senha
```

Exemplos de requisições estão em `api.http`.
