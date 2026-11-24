#!/usr/bin/env python3
"""Smoke test HTTP para comparar uma API antes e depois de uma refatoração.

Subcomandos:
  run      Executa as requisições de um arquivo JSON e grava as respostas normalizadas.
  compare  Compara duas gravações e mostra, caso a caso, o que mudou.

Formato do arquivo de requisições (lista JSON):
  [
    {"method": "GET",  "path": "/items"},
    {"method": "POST", "path": "/items", "body": {"name": "x"},
     "headers": {"X-Token": "abc"},
     "unordered": true,
     "ignore": ["token"],
     "expect_change": "senha deixa de ser devolvida"}
  ]

  body           corpo JSON da requisição (opcional)
  headers        cabeçalhos extras (opcional)
  unordered      ordena as listas da resposta, para APIs que não garantem ordem
  ignore         nomes de campos cujo valor muda a cada execução (tokens, ids aleatórios)
  expect_change  motivo pelo qual a resposta DEVE mudar após a refatoração

As respostas são normalizadas (chaves JSON ordenadas, timestamps trocados por <TS>)
para que duas execuções com o mesmo estado inicial sejam comparáveis.
Só usa a biblioteca padrão do Python 3.
"""
import argparse
import difflib
import json
import re
import sys
import time
import urllib.error
import urllib.request

TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:?\d{2})?")
MAX_DIFF_LINES = 40


def wait_until_up(base_url, timeout_s):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            urllib.request.urlopen(base_url, timeout=2)
            return True
        except urllib.error.HTTPError:
            return True  # respondeu, mesmo que com 4xx ou 5xx
        except OSError:
            time.sleep(0.3)
    return False


def call(base_url, case):
    data = None
    headers = dict(case.get("headers") or {})
    if case.get("body") is not None:
        data = json.dumps(case["body"]).encode()
        headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(base_url + case["path"], data=data, headers=headers,
                                 method=case["method"].upper())
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8", "replace")
    except OSError as err:
        return 0, f"ERRO DE CONEXAO: {err}"


def scrub(value, unordered, ignore):
    if isinstance(value, dict):
        return {k: "<IGNORED>" if k in ignore else scrub(v, unordered, ignore)
                for k, v in value.items()}
    if isinstance(value, list):
        items = [scrub(v, unordered, ignore) for v in value]
        if unordered:
            items.sort(key=lambda v: json.dumps(v, sort_keys=True))
        return items
    return value


def normalize(text, case):
    try:
        parsed = scrub(json.loads(text), case.get("unordered", False), set(case.get("ignore") or []))
        text = json.dumps(parsed, indent=2, sort_keys=True, ensure_ascii=False)
    except ValueError:
        text = text.strip()
        if text.lower().startswith(("<!doctype", "<html")):
            title = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
            text = "<pagina HTML> " + (title.group(1).strip() if title else "")
    return TIMESTAMP.sub("<TS>", text)


def cmd_run(args):
    base_url = args.base_url.rstrip("/")
    with open(args.requests, encoding="utf-8") as fh:
        cases = json.load(fh)
    if not wait_until_up(base_url, args.wait):
        sys.exit(f"A aplicacao nao respondeu em {base_url} apos {args.wait}s")

    results = []
    for index, case in enumerate(cases, 1):
        status, text = call(base_url, case)
        results.append({
            "id": f"{index:02d} {case['method'].upper()} {case['path']}",
            "status": status,
            "body": normalize(text, case),
            "expect_change": case.get("expect_change"),
        })
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump({"base_url": base_url, "results": results}, fh, indent=2, ensure_ascii=False)

    by_class = {}
    for result in results:
        label = "sem resposta" if result["status"] == 0 else f"{result['status'] // 100}xx"
        by_class[label] = by_class.get(label, 0) + 1
    summary = ", ".join(f"{count} {label}" for label, count in sorted(by_class.items()))
    print(f"{len(results)} requisicoes gravadas em {args.out} ({summary})")
    for result in results:
        if result["status"] == 0 or result["status"] >= 500:
            print(f"  atencao: {result['id']} -> HTTP {result['status']}")


def load_results(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["results"]


def cmd_compare(args):
    before, after = load_results(args.before), load_results(args.after)
    if [r["id"] for r in before] != [r["id"] for r in after]:
        sys.exit("As duas gravacoes nao tem a mesma lista de requisicoes; "
                 "rode as duas com o mesmo arquivo de requisicoes.")

    same, expected, unexpected, missing_change = 0, [], [], []
    for old, new in zip(before, after):
        reason = new.get("expect_change") or old.get("expect_change")
        changed = old["status"] != new["status"] or old["body"] != new["body"]
        if not changed:
            if reason:
                missing_change.append((old["id"], reason))
            else:
                same += 1
            continue
        (expected if reason else unexpected).append((old, new, reason))

    def show(old, new, reason):
        print(f"\n--- {old['id']}")
        if reason:
            print(f"    mudanca esperada: {reason}")
        if old["status"] != new["status"]:
            print(f"    status: {old['status']} -> {new['status']}")
        diff = list(difflib.unified_diff(old["body"].splitlines(), new["body"].splitlines(),
                                         "antes", "depois", lineterm="", n=1))
        for line in diff[:MAX_DIFF_LINES]:
            print("    " + line)
        if len(diff) > MAX_DIFF_LINES:
            print(f"    ... ({len(diff) - MAX_DIFF_LINES} linhas a mais)")

    if unexpected:
        print("== MUDANCAS INESPERADAS ==")
        for item in unexpected:
            show(*item)
    if expected:
        print("\n== MUDANCAS ESPERADAS ==")
        for item in expected:
            show(*item)
    if missing_change:
        print("\n== DEVERIAM TER MUDADO E NAO MUDARAM ==")
        for case_id, reason in missing_change:
            print(f"--- {case_id}\n    esperado: {reason}")

    server_errors = [r["id"] for r in after if r["status"] == 0 or r["status"] >= 500]
    print("\n== RESUMO ==")
    print(f"total: {len(after)} | iguais: {same} | mudancas esperadas: {len(expected)} | "
          f"mudancas inesperadas: {len(unexpected)} | deveriam mudar e nao mudaram: {len(missing_change)}")
    if server_errors:
        print("respostas 5xx ou sem resposta no depois: " + "; ".join(server_errors))
    sys.exit(1 if unexpected or missing_change else 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="executa as requisicoes e grava as respostas")
    run.add_argument("--base-url", required=True, help="ex.: http://127.0.0.1:5000")
    run.add_argument("--requests", required=True, help="arquivo JSON com as requisicoes")
    run.add_argument("--out", required=True, help="arquivo JSON de saida")
    run.add_argument("--wait", type=int, default=30, help="segundos para esperar o boot (padrao: 30)")
    run.set_defaults(func=cmd_run)

    compare = sub.add_parser("compare", help="compara duas gravacoes")
    compare.add_argument("before")
    compare.add_argument("after")
    compare.set_defaults(func=cmd_compare)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
