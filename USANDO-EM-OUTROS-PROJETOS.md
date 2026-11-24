# Como usar a skill `refactor-arch` em outros projetos

A skill `refactor-arch` audita um projeto backend e o refatora para o padrão MVC, em três fases: análise, auditoria com relatório e refatoração validada. Ela não depende dos projetos deste repositório; este guia mostra como instalá-la e usá-la em qualquer outro.

## Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado.
- Python 3 disponível no terminal. A skill o usa para comparar as respostas dos endpoints antes e depois; sem ele, a comparação é feita com `curl`.
- O projeto alvo rodando na sua máquina: dependências instaláveis e um comando de start que funciona.
- Git, com o trabalho em andamento commitado. A refatoração mexe em muitos arquivos, e uma árvore limpa permite revisar o resultado com `git diff` e desfazer tudo se for preciso.

## Instalação

A skill é uma pasta. Instalar é copiá-la para onde o Claude Code procura skills.

Primeiro, obtenha a pasta:

```bash
git clone https://github.com/Lucassamuel97/mba-ia-refactor-projects-skill.git /tmp/refactor-arch-src
```

Depois escolha onde instalar.

**Opção A — em um projeto.** A skill fica disponível só nele e pode ser versionada junto com o código, para o time inteiro usar:

```bash
cd /caminho/do/seu/projeto
mkdir -p .claude/skills
cp -r /tmp/refactor-arch-src/code-smells-project/.claude/skills/refactor-arch .claude/skills/
```

**Opção B — na sua conta.** A skill fica disponível em todos os projetos que você abrir:

```bash
mkdir -p ~/.claude/skills
cp -r /tmp/refactor-arch-src/code-smells-project/.claude/skills/refactor-arch ~/.claude/skills/
```

Para conferir, abra o Claude Code na pasta do projeto e digite `/`: `refactor-arch` deve aparecer na lista de comandos.

## Passo a passo de uso

1. **Crie uma branch** para a refatoração, a partir de uma árvore limpa.

   ```bash
   git switch -c refatoracao-mvc
   ```

2. **Abra o Claude Code na raiz do projeto**, em modo interativo. A skill pausa no meio e espera a sua resposta, o que não funciona em modo não interativo (`claude -p`).

   ```bash
   claude "/refactor-arch"
   ```

   O argumento é opcional e indica onde salvar o relatório: `claude "/refactor-arch docs/auditoria.md"`. Sem ele, o relatório vai para `reports/audit-report.md`.

3. **Confira a Fase 1.** A skill imprime o bloco `PHASE 1: PROJECT ANALYSIS` com linguagem, framework, banco, domínio, arquitetura atual e número de rotas. Se algo estiver errado aqui (o framework, o número de arquivos), corrija antes de seguir: as outras fases dependem disso.

4. **Leia o relatório da Fase 2.** Cada finding traz severidade, arquivo e linha, descrição, impacto e recomendação. Nenhum arquivo foi alterado até este ponto.

5. **Responda à pergunta de confirmação.**

   | Resposta | O que acontece |
   |---|---|
   | `y` | A skill segue para a refatoração |
   | `y`, com ressalvas ("sim, mas não mexa no módulo de pagamentos") | Refatora respeitando as ressalvas e as lista no resumo final |
   | `n` | Nada é alterado; a skill oferece salvar o relatório |
   | Uma pergunta sobre o relatório | A skill responde e pergunta de novo; dúvida não conta como confirmação |

   Se você só quer a auditoria, responda `n`.

6. **Acompanhe a Fase 3.** A skill grava as respostas de todos os endpoints, refatora camada por camada, sobe a aplicação de novo e compara as respostas. O Claude Code pode pedir permissão para rodar comandos e editar arquivos, conforme o modo de permissão que você usa.

7. **Revise o resumo final** (`PHASE 3: REFACTORING COMPLETE`) antes de commitar:

   - `Behavior Changes` lista toda diferença de resposta entre antes e depois. Leia com atenção: é ali que aparece o que seus clientes vão notar.
   - `Partial` e `Deferred` listam o que não foi corrigido e por quê.
   - `Validation` mostra `✓` só para o que foi verificado; um `✗` vem com a explicação.
   - Rode os testes do projeto e leia o `git diff`.

8. **Commite** quando estiver satisfeito. A skill não faz commits nem troca de branch.

## O que a skill faz e o que não faz

Faz:

- Preserva rotas, payloads, status codes, mensagens e o comando de start.
- Tira segredos do código, sem exigir configuração nova para a aplicação subir.
- Corrige injeção de SQL, senhas sem hash, exposição de dados sensíveis, N+1, falta de transação e de validação, entre os 22 anti-patterns do catálogo.
- Protege rotas administrativas e destrutivas com um token lido do ambiente. Sem o token configurado, elas respondem 403.

Não faz sem pedido explícito:

- Exigir autenticação nas rotas de negócio, mudar o formato das respostas, renomear campos da API ou remover rotas. Tudo isso quebraria os clientes atuais, então entra no relatório e fica em `Deferred`.
- Trocar de framework, de banco ou introduzir um ORM.
- Commitar ou alterar o histórico do git. Segredos que já foram versionados continuam no histórico e precisam ser rotacionados por você.

## Vantagens

- **Você decide antes de qualquer mudança.** As duas primeiras fases são somente leitura, e a refatoração só começa depois da sua confirmação.
- **Relatório conferível.** Cada problema aponta arquivo e linha, com as linhas relidas antes de o relatório ser escrito. Nos três projetos deste repositório, todas as referências de linha conferidas existiam no código original.
- **Prova de que nada quebrou.** A validação compara as respostas reais dos endpoints antes e depois, em vez de confiar em inspeção. As mudanças esperadas são declaradas antes da comparação, para uma regressão não passar como intencional.
- **Funciona em stacks diferentes.** A mesma pasta, sem alteração, refatorou dois projetos Flask e um Express, um deles um monolito e outro já parcialmente organizado.
- **Adapta-se ao ponto de partida.** Em um monolito cria a estrutura completa; em um projeto com camadas, mantém o que está certo e cria só o que falta.
- **Não esconde o que ficou pendente.** O resumo final separa o que foi resolvido, o que foi resolvido em parte e o que foi adiado, com o motivo.
- **Detecta APIs deprecated** e troca pelo equivalente moderno, cuidando para o resultado continuar igual (por exemplo, o formato das datas).
- **É personalizável sem código.** O catálogo, as guidelines e o playbook são arquivos Markdown.

## Personalização

Os arquivos em `references/` definem o comportamento. Edite-os para ajustar a skill ao seu time:

| Para mudar | Edite |
|---|---|
| Quais problemas são detectados e com que severidade | `anti-patterns-catalog.md` |
| A estrutura de pastas alvo e o que cabe em cada camada | `mvc-guidelines.md` |
| Como cada problema é corrigido, e o que nunca é aplicado sozinho | `refactoring-playbook.md` |
| O formato do relatório e do resumo final | `report-template.md` |
| Como a stack e as rotas são detectadas | `project-analysis.md` |

Ao acrescentar um anti-pattern ao catálogo, indique a transformação do playbook que o resolve.

## Limites conhecidos

- **Escala testada.** A skill foi validada em três APIs pequenas, de 180 a 1.200 linhas, em Python/Flask e Node.js/Express. Projetos maiores e outras stacks seguem as mesmas instruções, mas não foram testados; comece por um módulo ou responda `n` na primeira vez para avaliar só a auditoria.
- **Banco externo.** A comparação de endpoints cria e apaga dados. Com um banco local e descartável isso é seguro; se a aplicação aponta para um banco compartilhado, a skill limita o teste às rotas de leitura, e a validação fica mais fraca.
- **Projetos sem API HTTP.** A validação é feita por requisições HTTP. Em bibliotecas, CLIs ou workers, a auditoria funciona, mas a prova de comportamento não se aplica.
- **Sem testes automatizados, a rede de segurança é o smoke test.** Ele cobre o que as requisições exercitam; fluxos que dependem de falha de banco ou de serviços externos não são verificados.
- **Tempo e custo.** Uma execução completa lê o projeto inteiro e sobe a aplicação duas vezes. No projeto Express deste repositório, a Fase 3 levou cerca de 9 minutos.
- **Outras ferramentas.** A skill foi escrita e testada no Claude Code. A estrutura (um `SKILL.md` e arquivos de referência em Markdown) é a mesma usada por ferramentas equivalentes, mas o uso fora do Claude Code não foi testado.
