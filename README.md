# Projeto Qualidade — Esteira DevOps da suíte de testes de API

**Disciplina:** S07 - Gerência de Configuração e Evolução de Software  
**Instituição:** INATEL  
**Integrantes:**
- Fabio Henrique
- Gabriel Renato
- Gabriel Baldoni
- Ian Romancini

---

## Sumário

1. [Descrição](#descrição)
2. [Pré-requisitos](#pré-requisitos)
3. [Instalação](#instalação)
4. [Execução](#execução)
5. [Uso](#uso)
6. [Funcionalidades](#funcionalidades)
7. [Jenkins](#jenkins)
8. [Testes e cobertura](#testes-e-cobertura)
9. [Docker e Compose](#docker-e-compose)
10. [E-mail](#e-mail)
11. [Uso de IA](#uso-de-ia)
12. [Histórico da NP1](#histórico-da-np1)

---

## Descrição

> Seção em construção. Responsável: Ian Romancini.

---

## Pré-requisitos

> Seção em construção. Responsável: Ian Romancini.

---

## Instalação

> Seção em construção. Responsável: Ian Romancini.

---

## Execução

> Seção em construção. Responsável: Ian Romancini.

---

## Uso

> Seção em construção. Responsável: Ian Romancini.

---

## Funcionalidades

> Seção em construção. Responsável: Ian Romancini.

---

## Jenkins

> Seção em construção. Responsável: Gabriel Baldoni.

### Imagem no Docker Hub

A imagem do Jenkins está publicada em
[baldonigabriel/projeto-qualidade-jenkins](https://hub.docker.com/r/baldonigabriel/projeto-qualidade-jenkins),
com a tag fixa `1.0.0`, que é a usada pelo `docker-compose.yml`, e a `latest` apontando para a
mesma versão. Ela é construída a partir da pasta `jenkins/`: o `Dockerfile`, os plugins do
`plugins.txt` e a configuração como código de `jenkins/casc/`, com o admin no `security.yaml`
e o job no `jobs.yaml`.

Para baixar a imagem e subir o Jenkins:

```bash
docker compose pull jenkins
docker compose up -d jenkins
```

Para publicar uma versão nova (só quem tem acesso à conta do Docker Hub):

```bash
docker build -t baldonigabriel/projeto-qualidade-jenkins:1.0.0 -t baldonigabriel/projeto-qualidade-jenkins:latest jenkins/
docker login
docker push baldonigabriel/projeto-qualidade-jenkins:1.0.0
docker push baldonigabriel/projeto-qualidade-jenkins:latest
```

Toda mudança no `jenkins/Dockerfile`, no `plugins.txt` ou em `jenkins/casc/` gera uma tag nova
(por exemplo, `1.1.0`), e o `docker-compose.yml` passa a usar essa tag. A `1.0.0` continua
publicada, para dar para voltar à versão anterior.

---

## Testes e cobertura

A suíte tem dois grupos de testes:

- **Os 20 casos de teste (TCs) da NP1**, que chamam a API pública do JSONPlaceholder. Geram 23
  execuções, porque o TC-002 e o TC-011 são parametrizados, e usam os markers `valid` e `invalid`.
- **Os testes unitários da NP2**, com o marker `unit`, que conferem o código e a configuração do
  projeto sem acessar a internet.

O mesmo comando, `pytest`, roda na máquina, no container `tests` e no stage Test do Jenkins. Nos
dois últimos, ele ganha só o `--junitxml=reports/junit.xml`, para gerar o resultado em JUnit. O
resto da configuração fica no `pytest.ini` (relatórios e markers) e no `.coveragerc` (cobertura).

### Como rodar

Com o ambiente virtual ativo e o `requirements.txt` instalado:

| Para | Comando |
|---|---|
| Rodar a suíte completa, com cobertura e o gate de 90% | `pytest` |
| Rodar só os testes unitários, sem internet | `pytest -m unit --no-cov` |
| Rodar só os TCs com dados válidos ou só os com dados inválidos | `pytest -m valid --no-cov` ou `pytest -m invalid --no-cov` |
| Rodar um caso específico, por exemplo o TC-003 | `pytest --no-cov -k tc003` |
| Gerar também o resultado em JUnit, como o Jenkins | `pytest --junitxml=reports/junit.xml` |

Os comandos parciais precisam do `--no-cov`. O gate de cobertura vale para qualquer execução, e um
teste sozinho executa pouco do código: `pytest -k tc003` passa no teste, mas falha no gate.

**Apontar a suíte para outra API.** A URL vem da variável `API_BASE_URL`. Sem ela, ou com ela
vazia, a suíte usa `https://jsonplaceholder.typicode.com`.

```powershell
# PowerShell
$env:API_BASE_URL = "https://outra-api.example.com"
pytest
Remove-Item Env:API_BASE_URL
```

```bash
# Linux/macOS
API_BASE_URL=https://outra-api.example.com pytest
```

No Compose, o container `tests` recebe a mesma variável do `.env`.

### Gate de cobertura (90%)

- **O que é medido:** só o código que escrevemos, isto é, `conftest.py`, `helpers.py`,
  `reporting.py` e a pasta `scripts/` (o `source` do `.coveragerc`). A API é de terceiros e os
  testes não são medidos.
- **O gate:** com `fail_under = 90`, uma execução abaixo de 90% termina com erro. No Jenkins, o
  stage Test fica FAILURE, o Build é pulado e o e-mail de falha sai do mesmo jeito.
- **Arquivo novo sem teste:** como `scripts/` entra como pasta, um arquivo novo nela que nenhum
  teste importa aparece com 0% e baixa o total.
- **Hoje:** a cobertura passa de 99%, e só duas linhas ficam sem cobertura. Uma é a do hook do
  `conftest.py` que monta o resumo do relatório HTML, porque o pytest-html o chama depois que a
  cobertura termina. Por isso a lógica desse resumo fica no `reporting.py`, que tem testes
  próprios. A outra é o `sys.exit(main())` do script de e-mail, que só roda quando o script é
  chamado direto.

### Relatórios

| Arquivo | O que é |
|---|---|
| `reports/report.html` | Relatório consolidado do pytest-html, com cada teste no seu grupo: um integrante (TC-001 a TC-020) ou os testes unitários. Também vai anexado ao e-mail |
| `reports/coverage/index.html` | Cobertura navegável, linha a linha |
| `reports/coverage.xml` | Cobertura em XML, lida pelo script de e-mail |
| `reports/junit.xml` | Resultado em JUnit, gerado quando o comando tem `--junitxml` (Jenkins e container `tests`) |

Onde ver:

- **Na máquina:** abra os arquivos de `reports/` no navegador.
- **No Jenkins:** em cada build, o JUnit aparece em *Test Result*, e a pasta `reports/` inteira fica
  em *Artifacts*, mesmo quando um teste falha.
- **Pelo Compose:** o container `tests` grava os relatórios no volume `reports`, e o serviço
  `reports` mostra esse volume em http://localhost:8081. Os resumos do `k6` (perfil `perf`)
  também aparecem ali.
- **No e-mail:** o corpo traz um resumo como este:

  ```
  Tests: 154 (passed: 154, failed: 0, errors: 0, skipped: 0)
  Coverage: 99.20%
  ```

  Quando um relatório não existe, por exemplo porque o build quebrou antes dos testes, a linha
  avisa que ele não foi gerado. O `report.html` vai anexado quando existe e tem até 10 MB.

### Testes unitários e de configuração

| Arquivo | O que confere |
|---|---|
| `tests/unit/test_helpers.py` | Os caminhos de erro do `helpers.py`: massa de dados ausente ou inválida e respostas que não são JSON |
| `tests/unit/test_reporting.py` | O grupo de cada teste, o título e o resumo do relatório consolidado |
| `tests/unit/test_notify_email.py` | O script de e-mail: configuração, origem, assunto, corpo, envio e códigos de saída, com um servidor SMTP falso |
| `tests/unit/test_email_report_summary.py` | O resumo dos testes e da cobertura no corpo do e-mail, com relatórios presentes, ausentes ou corrompidos |
| `tests/unit/test_email_attachment.py` | O anexo do `report.html` no e-mail: relatório presente, ausente, ilegível ou acima do limite de 10 MB |
| `tests/unit/test_no_hardcoded_email.py` | Que nenhum e-mail real está fixo no pipeline: os destinatários vêm de `NOTIFY_EMAIL_TO` |
| `tests/unit/test_jenkins_config.py` | A configuração do Jenkins: plugins com versão fixada, senhas só por variável em `jenkins/casc/` e o job `projeto-qualidade` com o parâmetro `BRANCH` |

Os testes de configuração leem os arquivos do pipeline (`Jenkinsfile`, `docker-compose.yml` e
`jenkins/`). Se alguém quebrar o que o grupo combinou, por exemplo com um plugin sem versão ou uma
senha escrita no arquivo, o stage Test falha.

### Rodar a partir do pacote

O `.tar.gz` gerado pelo stage Build leva a suíte inteira: os testes, a massa de dados, a
configuração e os arquivos que os testes de configuração leem. Para conferir:

```bash
python -m build --sdist
tar -xzf dist/projeto_qualidade-2.0.0.tar.gz
cd projeto_qualidade-2.0.0
pytest
```

### Mapa de casos de teste (ID → Arquivo → Teste)

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

## Docker e Compose

> Seção em construção. Responsável: Fabio Henrique.

---

## E-mail

> Seção em construção. Responsável: Ian Romancini.

---

## Uso de IA

> Tabela-resumo dos modelos usados pelo grupo em construção. Responsável: Ian Romancini.

### Declaração individual — Fabio Henrique

> Em construção.

### Declaração individual — Gabriel Renato

**Ferramenta:** Claude Opus 5.5 e Claude Fable 5.2, pelo Claude Code (extensão do VS Code), com
acesso ao repositório local.

**Como trabalhei com a ferramenta:** usei a IA como par de programação. A maior parte do código
da minha parte foi escrita por ela, em etapas pequenas, na ordem do plano. Antes de cada etapa,
ela mostrava quais arquivos ia mexer, quais não ia tocar e como ia verificar, e só seguia com o
meu "ok". Depois, rodava as verificações (testes, Docker, um Jenkins descartável) e explicava cada
parte do código e as perguntas que o professor poderia fazer. Eu revisava, tirava as dúvidas e
pedia ajustes. Todos os commits, pushes e PRs foram feitos por mim, e nada foi para o GitHub sem a
minha aprovação.

**Para que usei:**

- o `Jenkinsfile` (o esqueleto e os stages Setup, Test e Build, com o arquivamento), o
  `pyproject.toml` e o `MANIFEST.in`, o `pytest.ini` e o `.coveragerc`, o `API_BASE_URL` no
  `conftest.py` e o serviço `reports`, com o `nginx/reports.conf`;
- na Fase 2, o resumo dos testes e da cobertura no e-mail e o
  `tests/unit/test_jenkins_config.py`;
- verificações: Jenkins e Mailpit descartáveis no Docker, provas de falha, o `pytest` rodado de
  dentro do pacote e a simulação de merge dos PRs abertos;
- revisão dos PRs do Gabriel Baldoni e do #40 do Ian;
- textos de commits, de PRs e de mensagens para o grupo;
- escrita da seção "Testes e cobertura" e desta declaração.

**Prompts** (resumidos e reescritos):

1. **Listagem de arquivos no serviço `reports`**

   > "Com base no plano da NP2, compare as duas formas de ligar a listagem de arquivos do nginx no
   > serviço `reports` e recomende uma."

   **Resposta:** a IA recomendou um arquivo de configuração próprio, o `nginx/reports.conf`,
   montado só para leitura, em vez de um comando dentro do Compose. Os motivos: é mais fácil de
   ler e de explicar, segue o padrão de configuração versionada do plano e mantém a imagem oficial
   do nginx sem mudar o comando de inicialização dela.

   **Resultado:** aceito. Antes do commit, a IA subiu o serviço e provou a listagem no 8081, o
   volume só para leitura e o container `tests` gravando os relatórios nele.

2. **Roteiro de validação isolada**

   > "Monte um roteiro para validar isoladamente cada item da minha Fase 1, conforme a seção
   > 'Como testar sozinho' do plano."

   **Resposta:** a IA montou um roteiro com os comandos para testar cada item da Fase 1, que rodei
   na minha máquina.

   **Resultado:** ajustado. O `jobs.yaml` de exemplo do roteiro estava errado: sem o `^` antes do
   `${BRANCH}`, o Jenkins aceitava qualquer branch. O erro só apareceu quando revisei o PR do
   Gabriel Baldoni (#34), e descartei o arquivo.

3. **Pacote incompleto no PR #29**

   > "Analise o pedido de mudança do Gabriel Baldoni no PR #29: o pacote gerado com a branch
   > integrada à `main` não inclui o `scripts/` nem o `.coveragerc`."

   **Resposta:** o `MANIFEST.in` que eu tinha feito com a IA deixava arquivos de fora do
   `.tar.gz`. A IA reproduziu o erro e mostrou que a correção sugerida ainda deixava um teste
   falhando.

   **Resultado:** ajustado. Usei a versão completa e, na segunda revisão, ainda acrescentei o
   `reporting.py`. Passei a conferir o pacote rodando o `pytest` de dentro dele.

4. **Integração do resumo ao script de e-mail**

   > "Apresente as duas opções de integração do resumo ao script de e-mail, não só a recomendada.
   > Não inicie a implementação antes de eu confirmar o alinhamento com o Ian, responsável pelo
   > script."

   **Resposta:** a IA tinha mostrado só a opção que recomendava, que mexia numa linha do script do
   Ian. Ela comparou as duas opções e escreveu uma mensagem para eu alinhar com ele.

   **Resultado:** ajustado. Escolhi a opção 1, mas só depois de combinar com o Ian.

5. **Escopo do teste da configuração do Jenkins**

   > "Implemente o teste da configuração do Jenkins com os três pontos do plano (plugins, segredos
   > e job), sem a checagem extra do `^` no parâmetro `BRANCH`."

   **Resposta:** além do que o plano pede, a IA tinha sugerido conferir também o `^` antes do
   `${BRANCH}` no `jobs.yaml`, para o erro do roteiro não voltar.

   **Resultado:** descartado. Mantive o teste só com o que o plano pede: plugins com versão fixada,
   senhas só por variável em `jenkins/casc/` e o job do contrato.

**O que fiz sem IA:**

- todos os commits e pushes, a abertura dos PRs e a escolha dos revisores;
- as decisões de cada item: o arquivo de configuração do nginx no `reports`, a opção 1 do resumo
  no e-mail e deixar fora do teste do Jenkins a checagem do `^` que a IA sugeriu;
- o alinhamento com o Ian: sobre a mudança no `main()` do script de e-mail, antes de mexer nele, e
  sobre a correção do TC-018 (#24);
- a postagem das revisões nos PRs do Gabriel Baldoni e do Ian;
- o roteiro para a validação isolada e o Docker Desktop, rodados na minha máquina.

### Declaração individual — Gabriel Baldoni

> Em construção.

### Declaração individual — Ian Romancini

> Em construção.

---

## Histórico da NP1

Na NP1, o projeto era só a suíte de testes automatizados da API, com o GitHub Actions como CI.
O conteúdo abaixo descreve aquela entrega (tag `v1.0.0`) e fica registrado como histórico. O
Plano de Testes da NP1 está em [`docs/np1/`](docs/np1/), com o PDF montado em
[`docs/np1/Plano_de_Testes.pdf`](docs/np1/Plano_de_Testes.pdf).

### Descrição do SUT (System Under Test)

O sistema testado (SUT) é o **JSONPlaceholder** (https://jsonplaceholder.typicode.com). 
Trata-se de uma API REST pública e gratuita que simula um backend real com rotas de um blog (posts, comentários, usuários, tarefas, etc.). A API foi escolhida por permitir a realização de requisições reais (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) de forma consistente e sem a necessidade de autenticação.

Os recursos cobertos pela nossa suíte de testes incluem:
- `/posts`
- `/comments`
- `/users`
- `/todos`

### Pré-requisitos

Para rodar este projeto na sua máquina, você vai precisar de:
- **Python 3.11** (ou superior) instalado.
- **Git** (para clonar o repositório).

### Instalação

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

### Como executar os testes

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

### Geração de relatórios

O nosso projeto já está configurado para exportar relatórios formatados da execução de testes.
Sempre que você executar o comando padrão (`pytest`), o arquivo final será gerado de forma consolidada e autossuficiente (self-contained HTML).

📌 **Onde encontrar o relatório:** `reports/report.html` *(Basta abri-lo no seu navegador favorito)*

### Testes de performance (bônus)

Os testes de performance usam o **k6** e ficam na pasta `perf/`. Eles não rodam no CI: são executados manualmente, e os relatórios da execução oficial ficam versionados em `perf/results/`.

| Teste | Script | Cenário | Critérios de aprovação |
|---|---|---|---|
| Carga | `perf/k6_load.js` | 10 usuários virtuais por 30s, com 1s de pausa entre iterações | erros < 1%, checks > 99% e p(95) < 300 ms |
| Estresse | `perf/k6_stress.js` | rampa de 0 a 30 usuários virtuais em 1 min (15s subindo até 15, 20s até 30, 15s mantendo 30 e 10s descendo) | erros < 1%, checks > 99% e p(95) < 500 ms |

O limite de tempo do teste de estresse é maior porque ali a degradação é esperada: o que se
verifica é se a API continua respondendo corretamente sob pressão, não se ela continua tão
rápida quanto na carga nominal.

Como a API é um serviço público e gratuito, a carga é propositalmente modesta e faz apenas leituras (`GET`).

1. Instale o k6 (versão usada: 2.2.0; [instalação em outras plataformas](https://grafana.com/docs/k6/latest/set-up/install-k6/)):
```powershell
winget install k6 --source winget
```

2. Na raiz do projeto, rode o teste gerando o relatório HTML.

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

Para rodar o teste de estresse, troque `k6_load` por `k6_stress` nos dois lugares do comando
(no nome do relatório e no caminho do script).

Se algum critério de aprovação for violado, o k6 termina com código de saída diferente de zero.

📌 **Onde encontrar os relatórios:**
- `perf/results/k6_load.html` e `perf/results/k6_stress.html`: painéis com os gráficos de cada execução *(abra no navegador)*
- `perf/results/k6_load_summary.json` e `perf/results/k6_stress_summary.json`: métricas e resultado de cada critério

**Execução oficial de carga (16/09/2026):** 837 requisições, p(95) de 35,6 ms, média de 29,4 ms, 0% de erros e 100% dos checks aprovados.

**Execução oficial de estresse (21/09/2026):** 3.267 requisições em 1.089 iterações (53,8 req/s), p(95) de 29,2 ms, média de 23,4 ms, máximo de 417,3 ms, 0% de erros e 100% dos checks aprovados.

Vale registrar o que o teste de estresse mostrou: com o triplo da concorrência do teste de
carga, o p(95) não piorou (29,2 ms contra 35,6 ms). A API absorveu a rampa sem degradar, então
o resultado estabelece um piso de capacidade — não o limite do serviço, que exigiria uma carga
maior do que é razoável aplicar a uma API pública e gratuita.

### Declaração de uso de Inteligência Artificial (NP1)

Em conformidade com o **Item 11 do enunciado** do projeto, o grupo declara que fez uso de ferramentas baseadas em Inteligência Artificial para apoio pontual durante a construção deste repositório (ex: estruturação da arquitetura base, apoio no setup inicial e dicas de legibilidade no padrão do Pytest).

Ressaltamos que todo o grupo revisou ativamente o código sugerido e detém pleno entendimento de todos os comandos, lógicas e arquivos presentes nesta entrega, assumindo inteira responsabilidade por sua qualidade e corretude em arguição técnica.

#### Declaração individual — Fabio Henrique

Em conformidade com o item 11 do enunciado, declaro que utilizei o Claude Opus 5 (via Claude Code, com esforço de raciocínio "Extra High") como ferramenta de apoio no projeto, nos seguintes pontos:

* **Testes de performance (k6):** recorri à IA para me auxiliar a montar os testes de carga e de estresse — a configuração compartilhada em `perf/lib/common.js`, os cenários de execução e os critérios de aprovação.

* **Estratégia de integração contínua:** pedi auxílio para definir a melhor abordagem de CI e montar o workflow do GitHub Actions.

* **Revisão final da entrega:** utilizei a IA para conferir o repositório contra o enunciado, corrigir o título do relatório consolidado em `conftest.py`, sincronizar a tabela de casos do Plano de Testes com as chaves da massa de dados e remontar o PDF do plano.

*Não utilizei IA para escrever os casos de teste.* Os testes sob minha responsabilidade (TC-001 a TC-005) foram escritos e revisados por mim.

Revisei todo o conteúdo produzido com apoio da ferramenta, compreendo o funcionamento de cada arquivo citado e assumo integral responsabilidade por sua qualidade e correção em arguição técnica.

#### Declaração individual — Gabriel Renato Oliveira Lopes

**Ferramentas utilizadas:**

* **Claude (Anthropic), modelo Opus 4.6**

* **Codex (OpenAI), modelo 5.6 Luna**

Ambas foram usadas como assistentes de programação em modo de pair programming, com acesso ao repositório local.

**Finalidade e escopo do uso**

1. **Claude Opus 4.6: testes, dados e documentação**

   * Criação dos payloads `valid_post`, `updated_post` e `partial_patch` em `data/payloads.json`, sem alterar as chaves já existentes.

   * Explicação das decisões de cada teste e orientação sobre a execução com Pytest no ambiente virtual (`.venv`).

2. **Codex 5.6 Luna: relatório consolidado**

   * Análise dos dois relatórios HTML gerados pelo `pytest-html` e implementação, no `conftest.py`, de hooks que unificam o relatório em um único arquivo (`reports/report.html`), com os resultados separados por integrante.

   * Ajuste do `.gitignore` para versionar o relatório consolidado.

Em ambas as ferramentas, as branches e os commits locais foram criados somente após a minha autorização expressa.

**Controles adotados**

* Cada etapa terminava com uma parada obrigatória: a sugestão de codigos eram apresentados, e nenhum comando Git era executado sem a minha aprovação.

* Revisei o código gerado, pedi correções e fiz por conta própria etapas como o `push` para o GitHub, mantendo o controle de versão.

**Responsabilidade:** Declaro que todo o conteúdo produzido com apoio de IA na minha parte do projeto foi revisado, executado, testado e validado por mim, e assumo total responsabilidade pelo código, pela documentação e pelos resultados entregues.

#### Declaração individual — Gabriel Baldoni

**Ferramentas utilizadas:**

* **Claude (Anthropic)**

**Finalidade e escopo do uso**

* **Definição de escopo e planejamento:** Utilizei a IA como apoio nas tarefas do meu bloco (TC-011 a TC-015, seções 1 a 3 do Plano de Testes e a montagem do PDF). A ferramenta foi usada para definir melhor o escopo de como iríamos implementar os testes a partir das especificações que o grupo já havia fechado no planejamento.
* **Revisão de Pull Requests:** Usei a IA para auxiliar na averiguação dos PRs avaliados por mim, verificando se estavam 100% dentro do que havíamos planejado e se as alterações correspondiam ao definido nos arquivos `.md` do projeto.

*Não utilizei IA para escrever os casos de teste.* Fiz, revisei e executei todos os testes sob minha responsabilidade por conta própria.

#### Declaração individual — Ian Romancini

**Ferramentas utilizadas:**

* **Claude (Anthropic)**

**Finalidade e escopo do uso**

* **Tutoria e Orientação:** Utilizei a ferramenta como tutor nas tarefas do meu bloco (TC-016 a TC-020). Pedi inicialmente para me dar um norte sobre o que fazer no projeto, com a instrução expressa de gerar apenas explicações e orientações, sem nenhum código.
* **Revisão de Pull Requests:** Usei a IA para auxiliar na averiguação dos PRs avaliados por mim, verificando se estavam 100% dentro do que havíamos planejado e se as alterações correspondiam ao definido nos arquivos `.md` do projeto.

*Não utilizei IA para escrever os casos de teste.* Todos os testes sob minha responsabilidade foram feitos exclusivamente por mim.
