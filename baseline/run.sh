#!/usr/bin/env bash
# Sobe um dos projetos com banco zerado, roda o smoke test e derruba a aplicação.
#
# Uso: bash baseline/run.sh <1|2|3> [arquivo-de-saida]
#   1 = code-smells-project   2 = ecommerce-api-legacy   3 = task-manager-api
#
# Sem arquivo de saída, grava em baseline/project-<n>.txt (a linha de base).
# Depois da refatoração, grave em outro arquivo e compare:
#   bash baseline/run.sh 1 /tmp/depois-1.txt && diff baseline/project-1.txt /tmp/depois-1.txt
#
# START_CMD e SEED_CMD sobrescrevem os comandos padrão, caso o entry point mude.
# Para rotas que passaram a exigir token, defina a variável da aplicação e o cabeçalho:
#   ADMIN_TOKEN=t SMOKE_HEADERS='{"X-Admin-Token":"t"}' bash baseline/run.sh 2 /tmp/depois-2.txt
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
n="${1:?informe o projeto: 1, 2 ou 3}"

case "$n" in
  1) dir=code-smells-project;  port=5000; start=".venv/bin/python app.py"; seed="" ;;
  2) dir=ecommerce-api-legacy; port=3000; start="npm start";               seed="" ;;
  3) dir=task-manager-api;     port=5000; start=".venv/bin/python app.py"; seed=".venv/bin/python seed.py" ;;
  *) echo "projeto inválido: $n" >&2; exit 2 ;;
esac
start="${START_CMD:-$start}"
seed="${SEED_CMD:-$seed}"
out="${2:-$ROOT/baseline/project-$n.txt}"
server_log="${out%.txt}.server.log"

if (exec 3<>"/dev/tcp/127.0.0.1/$port") 2>/dev/null; then
  echo "porta $port já está em uso; pare o processo antes de rodar" >&2
  exit 1
fi

cd "$ROOT/$dir"
# Banco zerado para que IDs e contagens sejam determinísticos.
find . -name "*.db" -not -path "./.venv/*" -not -path "./node_modules/*" -delete
if [ -n "$seed" ]; then bash -c "$seed" >/dev/null; fi

setsid bash -c "$start" >"$server_log" 2>&1 &
server_pid=$!
stop_server() {
  kill -- "-$server_pid" 2>/dev/null || true
  # Espera a porta liberar, para que rodadas em sequência não colidam.
  for _ in $(seq 1 50); do
    (exec 3<>"/dev/tcp/127.0.0.1/$port") 2>/dev/null || return 0
    sleep 0.1
  done
}
trap stop_server EXIT

python3 "$ROOT/baseline/smoke.py" "http://127.0.0.1:$port" \
  "$ROOT/baseline/requests-project-$n.json" >"$out"

echo "ok: $(grep -c '^### ' "$out") requisições -> $out"
grep '^HTTP ' "$out" | sort | uniq -c
