#!/usr/bin/env python3
"""Executa uma lista de requisições contra uma API e imprime um transcript estável.

Uso: smoke.py <base_url> <requests.json>

O transcript é normalizado (JSON com chaves ordenadas, timestamps trocados por <TS>)
para que rodadas antes/depois da refatoração possam ser comparadas com `diff`.
Um caso com "unordered": true também tem as listas ordenadas, para respostas cuja
ordem a API não garante.
A variável de ambiente SMOKE_HEADERS (JSON) acrescenta cabeçalhos a todas as requisições,
para testar rotas que passaram a exigir token após a refatoração.

Campos opcionais de cada caso:
  capture  {"variavel": "caminho.do.campo"}: guarda um valor da resposta JSON; "${variavel}"
           pode ser usado em SMOKE_HEADERS. Campo ausente vira texto vazio, então o login
           do código legado (que não devolve token) não quebra a execução.
  silent   executa a chamada sem registrá-la no transcript (ex.: um login para obter token),
           para que transcripts gravados antes e depois tenham a mesma numeração.
  drop     chaves removidas do JSON antes de normalizar (ex.: o "token" que o login passou
           a devolver), para comparar só o que já existia.
Só usa a biblioteca padrão.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(\.\d+)?")
BOOT_TIMEOUT_S = 30
EXTRA_HEADERS = json.loads(os.environ.get("SMOKE_HEADERS", "{}"))


def wait_until_up(base_url):
    deadline = time.time() + BOOT_TIMEOUT_S
    while time.time() < deadline:
        try:
            urllib.request.urlopen(base_url, timeout=2)
            return
        except urllib.error.HTTPError:
            return  # respondeu, mesmo que com 4xx/5xx
        except OSError:
            time.sleep(0.3)
    sys.exit(f"API não respondeu em {base_url} após {BOOT_TIMEOUT_S}s")


VARIABLE = re.compile(r"\$\{(\w+)\}")
VARIABLES = {}


def substitute(value):
    return VARIABLE.sub(lambda m: VARIABLES.get(m.group(1), ""), value)


def capture(text, spec):
    try:
        data = json.loads(text)
    except ValueError:
        data = None
    for name, path in spec.items():
        value = data
        for key in path.split("."):
            value = value.get(key) if isinstance(value, dict) else None
        VARIABLES[name] = "" if value is None else str(value)


def drop_keys(value, keys):
    if isinstance(value, dict):
        return {k: drop_keys(v, keys) for k, v in value.items() if k not in keys}
    if isinstance(value, list):
        return [drop_keys(v, keys) for v in value]
    return value


def call(base_url, method, path, body):
    data = None
    headers = {k: substitute(v) for k, v in EXTRA_HEADERS.items()}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base_url + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8", "replace")


def sort_lists(value):
    """Ordena listas recursivamente, para respostas cuja ordem não é garantida pela API."""
    if isinstance(value, dict):
        return {k: sort_lists(v) for k, v in value.items()}
    if isinstance(value, list):
        return sorted((sort_lists(v) for v in value), key=lambda v: json.dumps(v, sort_keys=True))
    return value


def normalize(text, unordered=False, drop=()):
    try:
        parsed = drop_keys(json.loads(text), set(drop))
        if unordered:
            parsed = sort_lists(parsed)
        text = json.dumps(parsed, indent=2, sort_keys=True, ensure_ascii=False)
    except ValueError:
        text = text.strip()
    return TIMESTAMP.sub("<TS>", text)


def main():
    base_url, requests_file = sys.argv[1].rstrip("/"), sys.argv[2]
    with open(requests_file, encoding="utf-8") as fh:
        cases = json.load(fh)

    wait_until_up(base_url)
    i = 0
    for case in cases:
        method, path = case["method"], case["path"]
        status, text = call(base_url, method, path, case.get("body"))
        if case.get("capture"):
            capture(text, case["capture"])
        if case.get("silent"):
            continue
        i += 1
        note = f"  # {case['note']}" if case.get("note") else ""
        print(f"### {i:02d} {method} {path}{note}")
        if case.get("body") is not None:
            print("> " + json.dumps(case["body"], ensure_ascii=False))
        print(f"HTTP {status}")
        print(normalize(text, case.get("unordered", False), case.get("drop", ())))
        print()


if __name__ == "__main__":
    main()
