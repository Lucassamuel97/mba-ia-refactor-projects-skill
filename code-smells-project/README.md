# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

## Configuração

Nenhuma variável é obrigatória. Os nomes e valores padrão estão em [.env.example](.env.example); a aplicação lê o ambiente do processo e não carrega o arquivo `.env` sozinha.

| Variável | Padrão | Uso |
|---|---|---|
| `SECRET_KEY` | aleatória a cada boot | Chave do Flask |
| `ADMIN_TOKEN` | ausente | Token das rotas `/admin/*`, enviado em `X-Admin-Token`. Sem ele, essas rotas respondem 403 |
| `APP_HOST` | `127.0.0.1` | Use `0.0.0.0` para aceitar conexões de outras máquinas |
| `APP_PORT` | `5000` | Porta |
| `APP_DEBUG` | `false` | Modo debug do Flask |
| `APP_ENV` | `producao` | Valor informado em `/health` |
| `DATABASE_PATH` | `loja.db` | Arquivo do banco SQLite |
| `LOG_LEVEL` | `INFO` | Nível de log |

## Estrutura

```
app.py          composition root: monta as camadas e inicia o servidor
config/         configuração lida do ambiente
database/       conexão por requisição, schema e seed
models/         acesso a dados, um módulo por domínio
services/       regras de negócio (pedidos, usuários, relatórios, notificações, senhas)
controllers/    fluxo de cada requisição e validação de entrada
routes/         blueprints: mapeamento de caminho para controller
middlewares/    exceções de domínio, tratamento de erro central e guard administrativo
```
