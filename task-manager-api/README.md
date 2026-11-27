# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

> Se você tinha um `tasks.db` de uma versão anterior, rode `python seed.py` de novo: as senhas agora são gravadas com hash KDF (`werkzeug.security`) e os hashes MD5 antigos não são mais aceitos.

## Configuração

Nenhuma variável de ambiente é obrigatória. Para configurar, copie `.env.example` para `.env`:

| Variável | Padrão | Uso |
|---|---|---|
| `SECRET_KEY` | chave efêmera gerada no boot | assina os tokens de login |
| `DATABASE_URL` | `sqlite:///tasks.db` | banco de dados |
| `APP_DEBUG` | `false` | modo debug do Flask |
| `APP_HOST` / `APP_PORT` | `0.0.0.0` / `5000` | endereço do servidor |
| `CORS_ORIGINS` | vazio (nenhuma origem externa) | origens liberadas, separadas por vírgula |

## Autenticação

`POST /login` devolve um `token` assinado, válido por 8 horas. Envie-o em `Authorization: Bearer <token>`.
O seed cria o administrador `joao@email.com` / `1234` e a usuária comum `maria@email.com` / `abcd`.

```bash
curl -s -X POST localhost:5000/login -H 'Content-Type: application/json' \
  -d '{"email": "joao@email.com", "password": "1234"}'
```

| Política | Rotas |
|---|---|
| pública | `GET /`, `GET /health`, `POST /login`, `POST /users` (o `role` enviado só vale com token de admin), `GET /categories` |
| só admin | `GET /users`, `DELETE /users/<id>`, `GET /tasks`, `GET /tasks/search`, `GET /tasks/stats`, `GET /reports/summary`, `POST/PUT/DELETE /categories` |
| dono ou admin | `GET/PUT /users/<id>` (só admin altera `role` e `active`), `GET /users/<id>/tasks`, `GET /reports/user/<id>`, `GET/PUT/DELETE /tasks/<id>` |
| autenticado | `POST /tasks` (quem não é admin só atribui a task a si mesmo) |

Sem token, as rotas protegidas respondem `401`; com papel insuficiente, `403`.

## Estrutura

```
config/       configuração lida do ambiente
models/       entidades, regras e consultas (task, user, category)
services/     casos de uso e transações (tasks, usuários, categorias, relatórios)
controllers/  fluxo de cada requisição e validação de entrada
routes/       mapeamento das rotas e política de acesso
middlewares/  erros de domínio, handler central e autenticação
utils/        helpers e relógio UTC
app.py        composition root
```
