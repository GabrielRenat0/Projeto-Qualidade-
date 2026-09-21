# Projeto — Testes Automatizados de API

[![API tests](https://github.com/GabrielRenat0/Projeto-Qualidade-/actions/workflows/tests.yml/badge.svg)](https://github.com/GabrielRenat0/Projeto-Qualidade-/actions/workflows/tests.yml)

**Disciplina:** Qualidade de Software  
**Instituição:** INATEL  
**Integrantes:**
- Gabriel Renato
- Fabio Henrique
- Ian Romancini
- Gabriel Baldoni

---

## 🎯 Descrição do SUT (System Under Test)

O sistema testado (SUT) é o **JSONPlaceholder** (https://jsonplaceholder.typicode.com). 
Trata-se de uma API REST pública e gratuita que simula um backend real com rotas de um blog (posts, comentários, usuários, tarefas, etc.). A API foi escolhida por permitir a realização de requisições reais (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) de forma consistente e sem a necessidade de autenticação.

Os recursos cobertos pela nossa suíte de testes incluem:
- `/posts`
- `/comments`
- `/users`
- `/todos`

---

## 💻 Pré-requisitos

Para rodar este projeto na sua máquina, você vai precisar de:
- **Python 3.11** (ou superior) instalado.
- **Git** (para clonar o repositório).

---

## 🚀 Instalação

1. Clone o repositório para a sua máquina:
```bash
git clone https://github.com/GabrielRenat0/Projeto-Qualidade-.git
cd Projeto-Qualidade-
```

2. (Recomendado) Crie e ative um ambiente virtual:
```bash
python -m venv .venv

# No Windows:
.venv\Scripts\activate

# No Linux/Mac:
source .venv/bin/activate
```

3. Instale as dependências (requests, pytest, pytest-html):
```bash
pip install -r requirements.txt
```

---

## ⚙️ Como Executar os Testes

O framework utilizado é o **Pytest**. Toda a suíte deve ser executada através de linha de comando.

Para executar a **suíte completa**:
```bash
pytest
```

Para rodar **apenas os testes de sucesso (caminho feliz)**:
```bash
pytest -m valid
```

Para rodar **apenas os testes de erro (dados inválidos)**:
```bash
pytest -m invalid
```

Para buscar **um caso de teste específico** (por exemplo, o TC-003):
```bash
pytest -k tc003
```

---

## 📊 Geração de Relatórios

O nosso projeto já está configurado para exportar relatórios formatados da execução de testes.
Sempre que você executar o comando padrão (`pytest`), o arquivo final será gerado de forma consolidada e autossuficiente (self-contained HTML).

📌 **Onde encontrar o relatório:** `reports/report.html` *(Basta abri-lo no seu navegador favorito)*

---

## ⚡ Testes de Performance (bônus)

Os testes de performance usam o **k6** e ficam na pasta `perf/`. Eles não rodam no CI: são executados manualmente, e os relatórios da execução oficial ficam versionados em `perf/results/`.

| Teste | Script | Cenário | Critérios de aprovação |
|---|---|---|---|
| Carga | `perf/k6_load.js` | 10 usuários virtuais por 30s, com 1s de pausa entre iterações | erros < 1%, checks > 99% e p(95) < 300 ms |

Como a API é um serviço público e gratuito, a carga é propositalmente modesta e faz apenas leituras (`GET`).

1. Instale o k6 (versão usada: 2.2.0; [instalação em outras plataformas](https://grafana.com/docs/k6/latest/set-up/install-k6/)):
```powershell
winget install k6 --source winget
```

2. Na raiz do projeto, rode o teste de carga gerando o relatório HTML.

No PowerShell:
```powershell
$env:K6_WEB_DASHBOARD = "true"
$env:K6_WEB_DASHBOARD_EXPORT = "perf/results/k6_load.html"
k6 run perf/k6_load.js
Remove-Item Env:K6_WEB_DASHBOARD, Env:K6_WEB_DASHBOARD_EXPORT
```

No Linux/Mac (bash):
```bash
K6_WEB_DASHBOARD=true K6_WEB_DASHBOARD_EXPORT=perf/results/k6_load.html k6 run perf/k6_load.js
```

Se algum critério de aprovação for violado, o k6 termina com código de saída diferente de zero.

📌 **Onde encontrar os relatórios:**
- `perf/results/k6_load.html`: painel com os gráficos da execução *(abra no navegador)*
- `perf/results/k6_load_summary.json`: métricas e resultado de cada critério

**Execução oficial (16/09/2026):** 837 requisições, p(95) de 35,6 ms, média de 29,4 ms, 0% de erros e 100% dos checks aprovados.

---

## 🗺️ Mapa de Casos de Teste (ID → Arquivo → Teste)

Os 20 casos de teste automatizados usam a massa compartilhada em `data/payloads.json` e estão mapeados individualmente abaixo:

| ID | Arquivo | Função de teste |
|---|---|---|
| TC-001 | `tests/test_valid_data.py` | `test_tc001_list_all_posts` |
| TC-002 | `tests/test_valid_data.py` | `test_tc002_get_post_at_valid_boundaries` |
| TC-003 | `tests/test_valid_data.py` | `test_tc003_filter_posts_by_user_id` |
| TC-004 | `tests/test_valid_data.py` | `test_tc004_list_comments_of_post` |
| TC-005 | `tests/test_valid_data.py` | `test_tc005_get_user_with_nested_objects` |
| TC-006 | `tests/test_valid_data.py` | `test_tc006_filter_completed_todos` |
| TC-007 | `tests/test_valid_data.py` | `test_tc007_create_post` |
| TC-008 | `tests/test_valid_data.py` | `test_tc008_update_post` |
| TC-009 | `tests/test_valid_data.py` | `test_tc009_patch_post_title` |
| TC-010 | `tests/test_valid_data.py` | `test_tc010_delete_post` |
| TC-011 | `tests/test_invalid_data.py` | `test_tc011_get_post_outside_valid_id_range` |
| TC-012 | `tests/test_invalid_data.py` | `test_tc012_get_post_with_non_numeric_id` |
| TC-013 | `tests/test_invalid_data.py` | `test_tc013_get_nonexistent_route` |
| TC-014 | `tests/test_invalid_data.py` | `test_tc014_filter_posts_by_nonexistent_user` |
| TC-015 | `tests/test_invalid_data.py` | `test_tc015_filter_comments_by_negative_post_id` |
| TC-016 | `tests/test_invalid_data.py` | `test_tc016_create_empty_post` |
| TC-017 | `tests/test_invalid_data.py` | `test_tc017_create_post_with_invalid_types` |
| TC-018 | `tests/test_invalid_data.py` | `test_tc018_update_nonexistent_post` |
| TC-019 | `tests/test_invalid_data.py` | `test_tc019_create_post_with_malformed_json` |
| TC-020 | `tests/test_invalid_data.py` | `test_tc020_get_post_after_delete` |

Os TCs parametrizados (TC-002 e TC-011) geram 23 execuções no total.

---

## 🤖 Declaração de Uso de Inteligência Artificial

Em conformidade com o **Item 11 do enunciado** do projeto, o grupo declara que fez uso de ferramentas baseadas em Inteligência Artificial para apoio pontual durante a construção deste repositório (ex: estruturação da arquitetura base, apoio no setup inicial e dicas de legibilidade no padrão do Pytest).

Ressaltamos que todo o grupo revisou ativamente o código sugerido e detém pleno entendimento de todos os comandos, lógicas e arquivos presentes nesta entrega, assumindo inteira responsabilidade por sua qualidade e corretude em arguição técnica.

# Declarações de Uso de Inteligência Artificial

## Declaração individual — Fabio Henrique

Em conformidade com o item 11 do enunciado, declaro que utilizei o Claude Opus 5 (via Claude Code, com esforço de raciocínio "Extra High") como ferramenta de apoio no projeto, nos seguintes pontos:

* **Testes de performance (k6):** recorri à IA para me auxiliar a montar os testes de carga e de estresse — a configuração compartilhada em `perf/lib/common.js`, os cenários de execução e os critérios de aprovação.

* **Estratégia de integração contínua:** pedi auxílio para definir a melhor abordagem de CI e montar o workflow do GitHub Actions.

* **Revisão final da entrega:** utilizei a IA para conferir o repositório contra o enunciado, corrigir o título do relatório consolidado em `conftest.py`, sincronizar a tabela de casos do Plano de Testes com as chaves da massa de dados e remontar o PDF do plano.

*Não utilizei IA para escrever os casos de teste.* Os testes sob minha responsabilidade (TC-001 a TC-005) foram escritos e revisados por mim.

Revisei todo o conteúdo produzido com apoio da ferramenta, compreendo o funcionamento de cada arquivo citado e assumo integral responsabilidade por sua qualidade e correção em arguição técnica.

## Declaração individual — Gabriel Renato Oliveira Lopes

**Ferramentas utilizadas:**

* **Claude (Anthropic), modelo Opus 4.6**

* **Codex (OpenAI), modelo 5.6 Luna**

Ambas foram usadas como assistentes de programação em modo de pair programming, com acesso ao repositório local.

### Finalidade e escopo do uso

1. **Claude Opus 4.6: testes, dados e documentação**

   * Criação dos payloads `valid_post`, `updated_post` e `partial_patch` em `data/payloads.json`, sem alterar as chaves já existentes.

   * Explicação das decisões de cada teste e orientação sobre a execução com Pytest no ambiente virtual (`.venv`).

2. **Codex 5.6 Luna: relatório consolidado**

   * Análise dos dois relatórios HTML gerados pelo `pytest-html` e implementação, no `conftest.py`, de hooks que unificam o relatório em um único arquivo (`reports/report.html`), com os resultados separados por integrante.

   * Ajuste do `.gitignore` para versionar o relatório consolidado.

Em ambas as ferramentas, as branches e os commits locais foram criados somente após a minha autorização expressa.

### Controles adotados

* Cada etapa terminava com uma parada obrigatória: a sugestão de codigos eram apresentados, e nenhum comando Git era executado sem a minha aprovação.

* Revisei o código gerado, pedi correções e fiz por conta própria etapas como o `push` para o GitHub, mantendo o controle de versão.

**Responsabilidade:** Declaro que todo o conteúdo produzido com apoio de IA na minha parte do projeto foi revisado, executado, testado e validado por mim, e assumo total responsabilidade pelo código, pela documentação e pelos resultados entregues.

## Declaração individual — Gabriel Baldoni

**Ferramentas utilizadas:**

* **Claude (Anthropic)**

### Finalidade e escopo do uso

* **Definição de escopo e planejamento:** Utilizei a IA como apoio nas tarefas do meu bloco (TC-011 a TC-015, seções 1 a 3 do Plano de Testes e a montagem do PDF). A ferramenta foi usada para definir melhor o escopo de como iríamos implementar os testes a partir das especificações que o grupo já havia fechado no planejamento.
* **Revisão de Pull Requests:** Usei a IA para auxiliar na averiguação dos PRs avaliados por mim, verificando se estavam 100% dentro do que havíamos planejado e se as alterações correspondiam ao definido nos arquivos `.md` do projeto.

*Não utilizei IA para escrever os casos de teste.* Fiz, revisei e executei todos os testes sob minha responsabilidade por conta própria.

## Declaração individual — Ian Romancini

**Ferramentas utilizadas:**

* **Claude (Anthropic)**

### Finalidade e escopo do uso

* **Tutoria e Orientação:** Utilizei a ferramenta como tutor nas tarefas do meu bloco (TC-016 a TC-020). Pedi inicialmente para me dar um norte sobre o que fazer no projeto, com a instrução expressa de gerar apenas explicações e orientações, sem nenhum código.
* **Revisão de Pull Requests:** Usei a IA para auxiliar na averiguação dos PRs avaliados por mim, verificando se estavam 100% dentro do que havíamos planejado e se as alterações correspondiam ao definido nos arquivos `.md` do projeto.

*Não utilizei IA para escrever os casos de teste.* Todos os testes sob minha responsabilidade foram feitos exclusivamente por mim.