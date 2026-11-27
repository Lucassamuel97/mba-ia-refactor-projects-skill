# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`, organizada em MVC.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

Nenhuma variável de ambiente é obrigatória. As opcionais estão em `.env.example` (`SECRET_KEY`, `APP_DEBUG`, `APP_HOST`, `APP_PORT`, `DATABASE_PATH`, `CORS_ORIGINS`). Sem `SECRET_KEY`, uma chave aleatória é gerada a cada boot e os tokens emitidos deixam de valer quando o processo reinicia.

## Autenticação

`POST /login` devolve um campo `token`, válido por 8 horas. Envie-o nas rotas protegidas:

```bash
curl -s -X POST localhost:5000/login -H 'Content-Type: application/json' \
  -d '{"email": "admin@loja.com", "senha": "admin123"}'
curl -s localhost:5000/pedidos -H "Authorization: Bearer <token>"
```

| Política | Rotas |
|---|---|
| pública | `GET /`, `GET /health`, `GET /produtos`, `GET /produtos/busca`, `GET /produtos/<id>`, `POST /usuarios`, `POST /login` |
| autenticado (o `usuario_id` do corpo precisa ser o do token, exceto para admin) | `POST /pedidos` |
| dono ou admin | `GET /usuarios/<id>`, `GET /pedidos/usuario/<usuario_id>` |
| admin | `POST /produtos`, `PUT /produtos/<id>`, `DELETE /produtos/<id>`, `GET /usuarios`, `GET /pedidos`, `PUT /pedidos/<id>/status`, `GET /relatorios/vendas`, `POST /admin/reset-db` |

Sem token válido a resposta é 401; com papel insuficiente, 403. Usuários de exemplo: `admin@loja.com` / `admin123` (admin), `joao@email.com` / `123456` e `maria@email.com` / `senha123` (clientes).

## Estrutura

```
config/        configuração lida do ambiente
database/      conexão por requisição, schema e seed
models/        acesso a dados por entidade
services/      regras que cruzam entidades (pedido, relatório, notificações)
controllers/   fluxo de cada requisição e validação de entrada
routes/        um Blueprint por domínio, com a política de acesso de cada rota
middlewares/   autenticação, exceções de domínio e tratamento de erro central
app.py         composition root
```
