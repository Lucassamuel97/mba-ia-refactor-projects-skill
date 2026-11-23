# Templates de saída (Fases 2 e 3)

Formatos fixos do relatório de auditoria e do resumo final. Um formato estável permite comparar auditorias de projetos diferentes e conferir o resultado contra um checklist, então siga a estrutura à risca: mesmos rótulos, mesma ordem.

Os rótulos ficam em inglês, como abaixo. O texto livre (descrições, impactos, recomendações) vai no idioma da conversa.

## Relatório de auditoria (Fase 2)

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome da pasta do projeto>
Stack:   <linguagem> + <framework>
Files:   <n> analyzed | ~<linhas> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>
Deprecated APIs: <n encontradas | none detected>

## Findings

### [CRITICAL] <nome do anti-pattern>
File: <arquivo>:<linha ou faixa>[, <arquivo>:<linha ou faixa> ...]
Description: <o que o código faz nesse ponto, com nomes e valores reais>
Impact: <o que pode dar errado e para quem>
Recommendation: <a correção, de forma concreta>

### [HIGH] <nome do anti-pattern>
...

================================
Total: <n> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

### Regras de preenchimento

- **Ordem:** todos os CRITICAL, depois HIGH, MEDIUM e LOW. Dentro da mesma severidade, o de maior impacto primeiro.
- **Um finding por anti-pattern.** Ocorrências do mesmo problema ficam juntas na linha `File:`, separadas por vírgula. Se forem muitas, liste as principais e informe o total: `src/server.js:42-45, 88, 131 (+9 ocorrências no mesmo arquivo)`.
- **`File:` sempre com linha.** Caminho relativo à raiz do projeto, seguido de `:linha` ou `:início-fim`. Um finding sobre o arquivo inteiro usa a faixa completa (`src/server.js:1-612`).
- **Linhas conferidas.** Releia o trecho com numeração de linha antes de escrever. As linhas se referem ao código como está no momento da auditoria.
- **`Description` com evidência.** Cite a função, a variável ou o valor real. Exemplo ruim: "Há problemas de segurança". Exemplo bom: "`findLoansByReader` interpola `req.query.reader` direto no `SELECT`".
- **`Impact` concreto.** Diga a consequência prática, não a categoria: "qualquer cliente autentica como administrador sem senha", e não "risco de segurança".
- **`Recommendation` acionável.** Diga o que fazer e onde, com o equivalente moderno quando for API deprecated.
- **Contagens coerentes.** Os números do `Summary` somam o `Total`, e cada finding aparece uma única vez.
- **APIs deprecated.** Cada uma é um finding normal, com título `Deprecated API: <api>`. A linha `Deprecated APIs` do `Summary` informa quantas foram encontradas ou `none detected`, para deixar registrado que a verificação foi feita.
- **Nada além do template.** Sem introdução antes do cabeçalho e sem comentário depois da pergunta final. A pergunta de confirmação é a última linha da resposta.

### Exemplo de finding preenchido

```
### [CRITICAL] Injeção por query montada com dados de entrada
File: src/repositories/loans.js:42-45, src/repositories/loans.js:88, src/server.js:131
Description: `findLoansByReader` interpola `req.query.reader` direto no SELECT com template string; o mesmo padrão aparece no UPDATE de devolução e no filtro de busca do server.js.
Impact: Um leitor consegue listar e alterar empréstimos de qualquer outro passando SQL no parâmetro `reader`.
Recommendation: Usar placeholders do driver (`$1`, `$2`) com os valores em array, nas três queries.
```

### Quando o relatório é salvo em arquivo

O arquivo recebe o mesmo conteúdo impresso, sem a pergunta de confirmação, dentro de um bloco de código ou como texto Markdown simples, precedido do resumo da Fase 1. Não resuma nem reordene ao salvar.

## Resumo final (Fase 3)

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios e arquivos de código após a refatoração>

## Findings
Resolved: <n> of <total>
Partial:
  - [<SEVERIDADE>] <nome do finding>: <o que ficou sem corrigir e por quê>
Deferred:
  - [<SEVERIDADE>] <nome do finding>: <por que não foi aplicado>

## Behavior Changes
  - <método e rota>: <o que mudou e por quê>

## Validation
  <✓ ou ✗> Application boots without errors
  <✓ ou ✗> All endpoints respond correctly (<iguais>/<total> unchanged, <n> intentional changes)
  <✓ ou ✗> Zero anti-patterns remaining (<n> partial, <n> deferred)
================================
```

### Regras de preenchimento

- **Árvore real.** Gere a árvore a partir do disco depois da refatoração, sem dependências nem arquivos gerados. Marque o entry point com `(composition root)`.
- **Todo finding tem destino.** Cada finding do relatório termina resolvido, parcial ou adiado. `Resolved` conta os resolvidos por inteiro e os parciais. `Partial` lista os que tiveram a maior parte das ocorrências corrigida e alguma deixada de fora, dizendo qual e por quê. `Deferred` lista os que não foram aplicados, com o motivo (por exemplo: "exige mudar o contrato da API; requer decisão do time"). Sem itens, escreva `Partial: none` ou `Deferred: none`.
- **`Behavior Changes` completo.** Liste toda diferença de resposta entre antes e depois, mesmo as desejadas. Sem diferenças, escreva `none`.
- **`✓` só com prova.** Marque `✓` apenas no que foi verificado nesta execução: a aplicação subiu, o smoke test rodou, a nova varredura não achou ocorrências. Se uma verificação falhou ou não pôde ser feita, use `✗` e diga o que aconteceu na mesma linha. Um `✓` não verificado é pior que um `✗` honesto, porque esconde do usuário onde olhar.
- **Terceira linha de validação.** `✓` quando todos os findings foram resolvidos, parciais ou adiados com motivo e a nova varredura confirma; os números de parciais e adiados aparecem entre parênteses.
