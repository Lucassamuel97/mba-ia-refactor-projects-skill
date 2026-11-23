# Skill `refactor-arch` — Refatoração Arquitetural Automatizada

Entrega do desafio de Skills do MBA da Full Cycle: uma skill do Claude Code que analisa, audita e refatora um projeto para o padrão MVC, aplicada a três projetos legados.

O enunciado completo está em [desafio.md](desafio.md).

## Etapas da entrega

| # | Etapa | O que é entregue | Status |
|---|---|---|---|
| 0 | Linha de base | Respostas de todos os endpoints dos 3 projetos, gravadas antes de qualquer mudança | Concluída |
| 1 | Análise manual | Problemas de cada projeto, documentados na seção "Análise Manual" | Pendente |
| 2 | Criação da skill | `SKILL.md` e arquivos de referência em `code-smells-project/.claude/skills/refactor-arch/` | Pendente |
| 3 | Execução no projeto 1 | `code-smells-project` refatorado e `reports/audit-project-1.md` | Pendente |
| 4 | Execução no projeto 2 | `ecommerce-api-legacy` refatorado e `reports/audit-project-2.md` | Pendente |
| 5 | Execução no projeto 3 | `task-manager-api` refatorado e `reports/audit-project-3.md` | Pendente |
| 6 | Documentação final | As quatro seções deste README preenchidas, no repositório público | Pendente |

### Etapa 0 — Linha de base

- [x] Os 3 projetos sobem sem erro no estado original
- [x] Respostas de todos os endpoints gravadas em [baseline/](baseline/) (40, 11 e 40 requisições)
- [x] Segunda execução com banco zerado produz saída idêntica

### Etapa 1 — Análise manual

Para cada um dos 3 projetos:

- [ ] No mínimo 5 problemas documentados
- [ ] Pelo menos 1 de severidade CRITICAL ou HIGH
- [ ] Pelo menos 2 de severidade MEDIUM
- [ ] Pelo menos 2 de severidade LOW
- [ ] Cada problema com arquivo, linha e justificativa de por que é relevante

### Etapa 2 — Criação da skill

- [ ] `SKILL.md` com 3 fases sequenciais: Análise, Auditoria e Refatoração
- [ ] Referência de análise de projeto: heurísticas para linguagem, framework, banco de dados e arquitetura
- [ ] Catálogo com no mínimo 8 anti-patterns, com sinais de detecção e severidade distribuída entre CRITICAL, HIGH, MEDIUM e LOW
- [ ] Catálogo cobre APIs deprecated e recomenda o equivalente moderno
- [ ] Template do relatório de auditoria
- [ ] Guidelines do MVC alvo: responsabilidades de Models, Views/Routes e Controllers
- [ ] Playbook com no mínimo 8 transformações, com código antes e depois
- [ ] A Fase 2 pausa e pede confirmação antes de modificar qualquer arquivo
- [ ] A Fase 3 valida o resultado: boot da aplicação e endpoints respondendo
- [ ] A skill é agnóstica de tecnologia: nada nela depende de um projeto específico

### Etapas 3, 4 e 5 — Execução nos projetos

Para cada projeto (nos projetos 2 e 3, depois de copiar a pasta da skill para dentro dele):

- [ ] Fase 1 detecta linguagem, framework e domínio corretamente
- [ ] Fase 2 encontra no mínimo 5 findings, com pelo menos 1 CRITICAL ou HIGH
- [ ] Fase 2 pausa e pede confirmação
- [ ] Relatório da Fase 2 salvo em `reports/audit-project-<n>.md`
- [ ] Fase 3 cria a estrutura MVC, com config extraída e error handling centralizado
- [ ] Aplicação inicia sem erros e os endpoints originais respondem
- [ ] Checklist de validação do [enunciado](desafio.md#validação) preenchido
- [ ] Código refatorado commitado

No projeto 1, a Fase 2 também precisa encontrar pelo menos 5 dos problemas da análise manual.

### Etapa 6 — Documentação final

- [ ] Seção "Análise Manual" preenchida
- [ ] Seção "Construção da Skill" preenchida
- [ ] Seção "Resultados" preenchida
- [ ] Seção "Como Executar" preenchida
- [ ] A mesma versão da skill está nos 3 projetos
- [ ] Tudo publicado no fork público

### Critérios de aceite

Todos valem para os 3 projetos:

| Critério | Requisito |
|---|---|
| Fase 1 detecta a stack corretamente | Obrigatório (3/3) |
| Fase 2 encontra 5 ou mais findings | Obrigatório (3/3) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | Obrigatório (3/3) |
| Aplicação funciona após a Fase 3 | Obrigatório (3/3) |

## Análise Manual

Pendente (etapa 1). Deve conter, para cada projeto, a lista de problemas identificados manualmente, a severidade de cada um e a justificativa.

## Construção da Skill

Pendente (etapa 2). Deve conter:

- Como o `SKILL.md` e os arquivos de referência foram estruturados
- Quais anti-patterns entraram no catálogo e por quê
- Como a skill foi mantida agnóstica de tecnologia
- Desafios encontrados e como foram resolvidos

## Resultados

Pendente (etapas 3 a 5). Deve conter:

- Quantidade de findings por severidade em cada projeto
- Estrutura de cada projeto antes e depois
- Checklist de validação preenchido para cada projeto
- Logs ou screenshots das aplicações rodando após a refatoração
- Observações sobre o comportamento da skill em stacks diferentes

## Como Executar

Os comandos da skill entram aqui na etapa 2. O que já funciona hoje é a linha de base.

### Pré-requisitos

- Claude Code instalado e configurado
- Python 3 e Node.js
- Dependências de cada projeto instaladas:

```bash
cd code-smells-project && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ..
cd task-manager-api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ..
cd ecommerce-api-legacy && npm install && cd ..
```

### Validar que a refatoração não quebrou os endpoints

`bash baseline/run.sh <n>` zera o banco do projeto `n`, sobe a aplicação, executa as requisições de `baseline/requests-project-<n>.json` e derruba o processo. Para comparar com o comportamento original:

```bash
bash baseline/run.sh 1 /tmp/depois-1.txt
diff baseline/project-1.txt /tmp/depois-1.txt
```

As únicas diferenças esperadas são nas requisições marcadas com "deve mudar", que cobrem falhas de segurança corrigidas pela refatoração (senhas expostas, SQL injection, rotas administrativas sem autenticação).

Se a refatoração mudar o entry point, informe o novo comando em `START_CMD` (e `SEED_CMD`, no projeto 3):

```bash
START_CMD=".venv/bin/python src/app.py" bash baseline/run.sh 1 /tmp/depois-1.txt
```
