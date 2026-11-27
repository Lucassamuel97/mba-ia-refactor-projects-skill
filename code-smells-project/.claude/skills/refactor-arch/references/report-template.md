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
Recommendation: <o que a Fase 3 vai fazer, por inteiro>
Verification: <como a Fase 3 prova que o Impact deixou de acontecer>

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
- **Linhas conferidas.** Releia o trecho com numeração de linha antes de escrever, um arquivo por vez (`grep -n padrão arquivo`, `cat -n arquivo`). `cat -n` de vários arquivos juntos continua a contagem de um arquivo no outro e produz linhas que não existem. As linhas se referem ao código como está no momento da auditoria.
- **`Description` com evidência.** Cite a função, a variável ou o valor real. Exemplo ruim: "Há problemas de segurança". Exemplo bom: "`findLoansByReader` interpola `req.query.reader` direto no `SELECT`".
- **`Impact` concreto.** Diga a consequência prática, não a categoria: "qualquer cliente autentica como administrador sem senha", e não "risco de segurança".
- **`Recommendation` é o escopo da Fase 3.** Escreva as ações da transformação do playbook que resolve o finding, completas e sem alternativas: nada de "ou", "avaliar", "considerar", "decidir depois". Cubra todas as ocorrências de `File:`. Quando a ação muda uma resposta da API, diga qual ("a rota deixa de existir e passa a responder 404", "a exclusão responde 409 enquanto houver matrículas"). Dê o equivalente moderno quando for API deprecated. Escreva só o que a Fase 3 vai aplicar: depois da confirmação, cada ação da Recommendation será conferida contra o código.
- **A Recommendation fecha o `Impact` inteiro.** Cada consequência descrita em `Impact` precisa deixar de acontecer depois da Fase 3. Se o Impact diz "qualquer cliente lista usuários e pedidos", a Recommendation protege todas as rotas que fazem isso, não só as administrativas. Escreva no `Impact` só consequências reais, e cubra todas na Recommendation. Nenhuma parte de um finding fica pendente, e segurança (autenticação, autorização, privilégio) nunca é adiada como decisão de produto.
- **`Verification` executável.** Diga como a Fase 3 prova que o Impact sumiu: a requisição e a resposta esperada (`POST /admin/sql → 404`; `GET /users sem token → 401, com token de admin → 200`) ou, quando o finding não tem efeito HTTP, a checagem no código (`grep "md5" → nenhuma ocorrência`).
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
Verification: `GET /loans?reader=1' OR '1'='1` devolve só os empréstimos do leitor 1 (antes devolvia todos); `grep` por template string em SQL nos três arquivos não encontra ocorrências.
```

Exemplo de finding de autenticação. A Recommendation cobre cada consequência do Impact, mesmo mudando o contrato:

```
### [HIGH] Autenticação ou autorização ausente
File: src/server.js:40-212, src/server.js:58, src/server.js:77
Description: Nenhuma das 14 rotas verifica identidade; `DELETE /readers/:id` apaga qualquer leitor, `GET /loans` lista os empréstimos de todos, `POST /readers` aceita `role` do corpo e `POST /login` devolve o token fixo `"token-" + id`, que nenhuma rota confere.
Impact: Qualquer cliente anônimo apaga leitores, lê os empréstimos de todos e se cadastra como administrador.
Recommendation: `POST /login` passa a devolver, no campo novo `token`, um token assinado com a `SECRET_KEY` e válido por 8 horas. Um guard único exige `Authorization: Bearer <token>` e lê o papel do banco: `DELETE /readers/:id` e `GET /loans` passam a ser só de admin, `GET /readers/:id/loans` do próprio leitor ou de admin; sem token, 401; com papel insuficiente, 403. `POST /readers` grava sempre o papel `reader`, ignorando o `role` enviado. Continuam públicas: `POST /login`, `POST /readers`, `GET /books` e `GET /health`.
Verification: Sem token, `DELETE /readers/2` e `GET /loans` respondem 401; com token de leitor, 403; com token de admin, a resposta original. `POST /readers` com `"role": "admin"` cria um leitor com papel `reader`.
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
Resolved: <n> of <total> (Recommendation applied as written)
Not applied:
  - [<SEVERIDADE>] <nome do finding>: <ressalva feita pela pessoa na confirmação>

## Behavior Changes
  - <método e rota>: <o que mudou e por quê>

## Validation
  <✓ ou ✗> Application boots without errors
  <✓ ou ✗> All endpoints respond correctly (<iguais>/<total> unchanged, <n> intentional changes)
  <✓ ou ✗> Recommendations applied as written (<n>/<n>)
  <✓ ou ✗> Impact verified gone for every finding (<n>/<n>)
  <✓ ou ✗> Zero anti-patterns remaining
================================
```

### Regras de preenchimento

- **Árvore real.** Gere a árvore a partir do disco depois da refatoração, sem dependências nem arquivos gerados. Marque o entry point com `(composition root)`.
- **Todo finding tem destino, sem meio-termo.** Um finding está em `Resolved` quando a Recommendation foi aplicada por inteiro, em todas as ocorrências, e a `Verification` provou que o Impact não acontece mais. `Not applied` lista só as Recommendations que a pessoa excluiu ao confirmar, com a ressalva dela. Uma Recommendation aplicada pela metade, ou um Impact que ainda acontece, não cabe em nenhuma das duas: significa que a Fase 3 não terminou. Sem itens, escreva `Not applied: none`.
- **`Behavior Changes` completo.** Liste toda diferença de resposta entre antes e depois, mesmo as desejadas. Sem diferenças, escreva `none`.
- **`✓` só com prova.** Marque `✓` apenas no que foi verificado nesta execução: a aplicação subiu, o smoke test rodou, a nova varredura não achou ocorrências. Se uma verificação falhou ou não pôde ser feita, use `✗` e diga o que aconteceu na mesma linha. Um `✓` não verificado é pior que um `✗` honesto, porque esconde do usuário onde olhar.
- **Linha `Recommendations applied as written`.** `✓` só depois de conferir cada Recommendation contra o código final, ação por ação. O número é aplicadas sobre aprovadas (o total menos `Not applied`).
- **Linha `Impact verified gone for every finding`.** `✓` só depois de executar a `Verification` de cada finding com a aplicação nos padrões versionados e ver o Impact não acontecer.
- **Linha `Zero anti-patterns remaining`.** `✓` quando a nova varredura do catálogo não encontra ocorrências no código novo.
