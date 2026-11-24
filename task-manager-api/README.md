# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. O projeto está organizado em MVC, com as regras de negócio em services.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`instance/tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Configuração

Nenhuma variável é obrigatória. Os nomes e valores padrão estão em [.env.example](.env.example); copie-o para `.env` na raiz do projeto para alterar os padrões.

| Variável | Padrão | Uso |
|---|---|---|
| `SECRET_KEY` | aleatória a cada boot | Chave do Flask |
| `APP_HOST` | `127.0.0.1` | Use `0.0.0.0` para aceitar conexões de outras máquinas |
| `APP_PORT` | `5000` | Porta |
| `FLASK_DEBUG` | `false` | Modo debug do Flask. Não ligue fora do desenvolvimento |
| `LOG_LEVEL` | `INFO` | Nível de log |
| `DATABASE_URL` | `sqlite:///tasks.db` | URL do banco (SQLAlchemy) |
| `CORS_ORIGINS` | `*` | Origens aceitas, separadas por vírgula |
| `SMTP_HOST`, `SMTP_PORT` | `smtp.gmail.com`, `587` | Servidor de email do `NotificationService` |
| `SMTP_USER`, `SMTP_PASSWORD` | ausentes | Credenciais de email. Sem elas, nenhum email é enviado |

## Estrutura

```
app.py          composition root: monta as camadas e inicia o servidor
config/         configuração lida do ambiente
database.py     instância do ORM, criação do schema e commit com rollback
models/         colunas, regras de cada entidade e consultas
services/       casos de uso: validação das regras, referências entre entidades, relatórios
controllers/    fluxo de cada requisição: lê a entrada, chama o service, monta a resposta
routes/         blueprints: mapeamento de caminho para controller
middlewares/    exceções de domínio e tratamento de erro central
utils/          constantes de domínio e funções puras
seed.py         dados de exemplo
```

As dependências apontam em um só sentido: `routes → controllers → services → models`.

## Segurança

- As senhas são gravadas com `werkzeug.security` (scrypt com salt). Hashes MD5 gravados por versões anteriores continuam válidos e são regravados no primeiro login bem-sucedido.
- O hash da senha não aparece em nenhuma resposta.
- **Pendente:** as rotas não exigem autenticação. O `token` devolvido por `POST /login` é um valor de demonstração que nenhuma rota verifica, e o campo `role` é aceito no corpo de `POST /users` e `PUT /users/<id>`. Exigir autenticação muda o contrato da API e depende de decisão do time.
