# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Configuração

Nenhuma variável de ambiente é obrigatória. As opcionais estão descritas em `.env.example`:

| Variável | Efeito |
|---|---|
| `PORT` | Porta HTTP (padrão `3000`) |
| `ADMIN_TOKEN` | Libera as rotas administrativas para quem envia o cabeçalho `X-Admin-Token` com o mesmo valor |
| `PAYMENT_GATEWAY_KEY` | Chave do gateway de pagamento (sem ela, o gateway é apenas simulado) |
| `LOG_LEVEL` | `error`, `warn`, `info` (padrão) ou `debug` |

`GET /api/admin/financial-report` e `DELETE /api/users/:id` respondem `403` enquanto `ADMIN_TOKEN` não estiver definido:

```bash
ADMIN_TOKEN=meu-token npm start
curl -H 'X-Admin-Token: meu-token' http://localhost:3000/api/admin/financial-report
```

## Estrutura

```
src/
├── app.js          composition root: monta as camadas e inicia o servidor
├── config/         configuração lida do ambiente
├── database/       conexão (promises e transações) e schema com seed
├── models/         SQL de cada entidade
├── services/       checkout, relatório financeiro e gateway de pagamento
├── controllers/    leitura e validação da requisição, resposta HTTP
├── routes/         mapeamento de rotas
├── middlewares/    guard de administrador e tratamento de erro central
└── utils/          erros de domínio, logger e hash de senha
```
