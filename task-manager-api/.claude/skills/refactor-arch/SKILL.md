---
name: refactor-arch
description: Audita e refatora a arquitetura de um projeto backend para o padrão MVC, em qualquer linguagem ou framework. Roda em 3 fases - análise da stack e da arquitetura atual, auditoria de anti-patterns com relatório por severidade (arquivo e linha exatos) e refatoração validada com boot da aplicação e teste dos endpoints. Use sempre que o usuário pedir para auditar a arquitetura, procurar code smells ou anti-patterns, gerar um relatório de auditoria de código, organizar um projeto legado em camadas ou refatorar para MVC, mesmo que ele não cite MVC pelo nome.
---

# refactor-arch

Você vai atuar como um arquiteto de software que herdou um projeto legado. O trabalho tem três fases, sempre nesta ordem: entender o projeto, auditar e mostrar o que encontrou, e só então refatorar para MVC e provar que a aplicação continua funcionando.

Quatro compromissos valem do começo ao fim, porque são o que torna seguro rodar esta skill em um projeto que alguém usa:

1. **Nada é alterado antes da confirmação.** As Fases 1 e 2 são somente leitura. A pessoa precisa ver o relatório e decidir antes de qualquer arquivo ser criado, editado ou apagado.
2. **O que a Fase 2 recomenda é o que a Fase 3 faz.** Cada `Recommendation` do relatório é uma ação concreta que a pessoa aprova ao confirmar. A Fase 3 aplica cada uma por inteiro, como escrita, e nada fora delas. E a Recommendation elimina tudo o que o `Impact` do finding descreve: se alguma consequência continua acontecendo depois da refatoração, o finding não foi resolvido. Segurança não é decisão de produto: autenticação, autorização e privilégio citados num finding são corrigidos nesta refatoração, mesmo quando mudam o contrato. Um relatório que promete o que a refatoração não entrega engana quem o aprovou.
3. **O resto do comportamento é preservado.** A refatoração muda a organização interna. Rotas, payloads, status codes e o comando de start continuam os mesmos, exceto nas mudanças que as Recommendations aprovadas descrevem. Preservar o contrato nunca é motivo para aplicar só parte de uma Recommendation.
4. **O resultado é reportado como foi.** Cada `✓` do resumo final corresponde a uma verificação feita nesta execução. O que falhou ou não foi verificado aparece como tal.

## Arquivos de referência

O conhecimento de domínio está em `references/`, dentro da pasta desta skill. Leia cada arquivo por inteiro no início da fase que o usa; eles são a fonte dos critérios, dos formatos e dos exemplos.

| Arquivo | Quando ler | O que contém |
|---|---|---|
| `references/project-analysis.md` | Início da Fase 1 | Heurísticas para detectar linguagem, framework, banco e arquitetura; formato do resumo |
| `references/anti-patterns-catalog.md` | Início da Fase 2 | 22 anti-patterns com sinais de detecção e severidade; tabela de APIs deprecated |
| `references/report-template.md` | Fase 2, antes de escrever o relatório; fim da Fase 3 | Formato do relatório de auditoria e do resumo final |
| `references/mvc-guidelines.md` | Início da Fase 3 | Camadas do MVC alvo, responsabilidades, regra de dependência, contrato a preservar |
| `references/refactoring-playbook.md` | Fase 2, ao escrever as Recommendations; início da Fase 3 | Regras gerais, ordem de execução, smoke test, 17 transformações com código antes e depois, limites da refatoração |

O script `scripts/http_smoke.py` grava e compara as respostas dos endpoints. O uso está descrito no playbook.

## Convenções

- **Projeto alvo:** o diretório de trabalho atual, a menos que o usuário indique outro.
- **Idioma:** os rótulos dos blocos impressos são fixos, em inglês. O texto livre acompanha o idioma em que o usuário está falando.
- **Destino do relatório:** se o usuário informou um caminho ao invocar a skill, é lá que o relatório de auditoria será salvo. Sem caminho, use `reports/audit-report.md` na raiz do projeto alvo.
- **Stack desconhecida:** as referências dão exemplos em Python e JavaScript. Em outra stack, aplique o mesmo raciocínio com os mecanismos equivalentes do framework em uso.

## Fase 1 — Análise

Objetivo: saber o que é o projeto antes de julgá-lo.

1. Leia `references/project-analysis.md`.
2. Liste e conte os arquivos de código do projeto, sem dependências, arquivos gerados e a pasta da própria skill.
3. Leia todos os arquivos contados, por inteiro, além do manifesto de dependências, do README e de exemplos de requisição.
4. Determine linguagem, framework e versão, dependências, banco de dados e tabelas, domínio, entry point e comando de start.
5. Monte o inventário de rotas (método, caminho, função). Ele é o contrato que a Fase 3 precisa preservar.
6. Monte o mapa de responsabilidades por arquivo e classifique a arquitetura atual.
7. Imprima o bloco `PHASE 1: PROJECT ANALYSIS` no formato da referência e siga direto para a Fase 2.

Não instale dependências nem suba a aplicação nesta fase: isso cria arquivos no projeto.

## Fase 2 — Auditoria

Objetivo: um relatório em que cada problema pode ser conferido abrindo o arquivo na linha indicada.

1. Leia `references/anti-patterns-catalog.md` e `references/report-template.md`.
2. Percorra o catálogo inteiro, entrada por entrada, contra o código lido. Para cada anti-pattern, procure os sinais de detecção e registre todas as ocorrências. Use busca textual para não depender da memória da leitura.
3. Verifique as APIs deprecated contra a tabela do catálogo e as versões levantadas na Fase 1. Esse item entra sempre, mesmo que o resultado seja nenhuma ocorrência.
4. Atribua a severidade pela escala do catálogo, ajustando pelo contexto quando houver motivo.
5. **Escreva cada Recommendation a partir do playbook.** Leia em `references/refactoring-playbook.md` as "Regras gerais", a seção "Limites da refatoração" e, para cada finding, a transformação que o catálogo indica. A Recommendation descreve exatamente o que a Fase 3 vai fazer: todas as ações, para todas as ocorrências de `File:`, sem alternativas ("ou", "avaliar", "decidir depois") e dizendo que resposta da API muda. Releia o `Impact` depois de escrever: cada consequência que ele descreve precisa desaparecer com a Recommendation; se alguma não desaparece, a Recommendation está incompleta. Nada de CRITICAL ou HIGH fica para depois. Escreva também a linha `Verification`: como a Fase 3 vai provar que o Impact deixou de acontecer (a requisição e a resposta esperada, ou a checagem no código).
6. Confira cada arquivo e linha relendo o trecho com numeração de linha, imediatamente antes de escrever.
7. Imprima o relatório exatamente no formato do template, com os findings ordenados de CRITICAL a LOW.
8. Encerre a resposta com a pergunta de confirmação do template e pare.

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Essa pausa é o ponto de controle da pessoa sobre o próprio código. Até receber uma resposta afirmativa explícita, não crie, edite nem apague arquivos, e não rode comandos que alterem o projeto. Perguntas ou comentários do usuário sobre o relatório não são confirmação: responda e pergunte de novo.

- Resposta negativa: não altere o código. Ofereça salvar o relatório no destino definido e encerre.
- Resposta afirmativa com ressalvas ("sim, mas não remova X"): as Recommendations excluídas não são aplicadas e aparecem em `Not applied` no resumo final, com a ressalva. Todas as outras são aplicadas por inteiro.

Se a sessão não é interativa e não há como receber a resposta, encerre ao fim da Fase 2.

## Fase 3 — Refatoração

Objetivo: o projeto no padrão MVC, com os findings resolvidos e a prova de que os endpoints continuam respondendo.

1. Leia `references/mvc-guidelines.md` e `references/refactoring-playbook.md`.
2. **Salve o relatório** da Fase 2 no destino definido, precedido do resumo da Fase 1.
3. **Verifique o estado do repositório.** Se houver mudanças não commitadas no projeto, avise o usuário de que elas vão se misturar com a refatoração e siga. Não faça commits, não troque de branch e não descarte mudanças.
4. **Grave o comportamento original**, antes de tocar no código: monte o arquivo de requisições a partir do inventário de rotas, suba a aplicação e rode o smoke test (seção "Smoke test" do playbook).
5. **Defina a estrutura alvo** conforme a classificação da Fase 1: estrutura completa para um monolito, só o que falta para um projeto parcialmente organizado. Mostre a árvore planejada em poucas linhas e prossiga, sem pedir nova confirmação.
6. **Aplique cada Recommendation por inteiro, na ordem do playbook**: config, banco e models, services, controllers, routes, middlewares, entry point, limpeza. Use a transformação indicada no catálogo e faça tudo o que a Recommendation escreveu, em todas as ocorrências: se ela diz remover uma rota, a rota deixa de existir; se diz tratar os dependentes na exclusão, a exclusão deixa de produzir órfãos; se diz exigir um campo, a requisição sem ele é recusada. Não troque uma Recommendation por uma versão mais branda (proteger em vez de remover, registrar em vez de corrigir, proteger só parte das rotas citadas, deixar o guard desligado por padrão) e não faça o que ela não pede. Se uma delas se mostrar inviável como escrita, porque quebra o boot ou contradiz outra, pare e pergunte, apresentando a alternativa; não decida sozinho. A cada camada concluída, confirme que o código ainda carrega.
7. **Remova os arquivos substituídos** e atualize o que dependia deles: imports em scripts de seed e testes, manifesto, `.env.example`, `.gitignore` e as instruções de execução do README, se o projeto as tiver.
8. **Valide:**
   - Suba a aplicação com o mesmo comando de antes, sem configurar nenhuma variável de ambiente nova. Ela precisa iniciar sem erro.
   - Marque as mudanças esperadas no arquivo de requisições, rode o smoke test de novo com o mesmo estado inicial de dados e compare com a gravação original.
   - Rode os testes automatizados do projeto, se existirem.
   - Confira cada Recommendation aprovada contra o código final, ação por ação e ocorrência por ocorrência. Uma Recommendation aplicada pela metade é um finding não resolvido.
   - Execute a `Verification` de cada finding com a aplicação nos padrões versionados (sem variável de ambiente nova): reproduza o Impact, com a mesma requisição ou checagem, e confirme que ele não acontece mais. Para autenticação, isso significa chamar cada rota protegida sem token (401), com token de usuário comum onde a rota é de admin (403) e com o token certo (resposta original). Um Impact que ainda acontece é um finding não resolvido.
   - Repita a varredura do catálogo sobre o código novo e percorra o checklist das guidelines de MVC.
9. **Corrija e repita.** Mudança inesperada no smoke test, erro no boot, Recommendation não aplicada por inteiro, Impact que ainda acontece ou anti-pattern remanescente significam que a fase não terminou: corrija o código e valide outra vez. Se depois de três rodadas ainda houver falha, pare e reporte o que está quebrado em vez de continuar tentando às cegas.
10. **Encerre os processos** que subiu e apague os arquivos temporários do smoke test.
11. Imprima o bloco `PHASE 3: REFACTORING COMPLETE` no formato do template.

O que a skill não muda sem pedido explícito está em "Limites da refatoração", no playbook: padronizar formato de resposta, renomear campos do contrato e trocar de tecnologia. Esses itens nunca servem de motivo para deixar parte de um Impact acontecendo.
