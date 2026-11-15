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

O Jenkins roda em container e é configurado só por código: o usuário admin, o job e as etapas
do pipeline estão versionados no repositório, e nada é criado pela interface.

### Acesso

```bash
docker compose up -d jenkins
```

Depois de cerca de um minuto, abra `http://localhost:8080` e entre com o `JENKINS_ADMIN_ID` e o
`JENKINS_ADMIN_PASSWORD` do `.env`. A porta é publicada só na própria máquina (`127.0.0.1`).

### Configuração como código

A configuração fica em dois lugares: a imagem, construída pelo `jenkins/Dockerfile` com os
plugins do `plugins.txt`, e a pasta `jenkins/casc/`, que o plugin Configuration as Code (JCasC)
lê inteira quando o Jenkins sobe:

| Arquivo | O que faz |
|---|---|
| `jenkins/Dockerfile` | Jenkins LTS (JDK 21) com tag fixa, Python 3 com `venv` e os plugins instalados, sem o assistente de instalação |
| `jenkins/plugins.txt` | Os plugins da imagem, todos com versão fixada |
| `jenkins/casc/security.yaml` | Cria o usuário admin, libera o acesso só para quem está logado e define os executores e a URL do Jenkins |
| `jenkins/casc/jobs.yaml` | Cria o job `projeto-qualidade` com Job DSL |

Nenhum desses arquivos guarda senha, e-mail ou o endereço do repositório: esses valores vêm do
`.env`, pelo Compose, como `${JENKINS_ADMIN_PASSWORD}` e `${REPO_URL}`. O `tests/unit/test_jenkins_config.py` falha se um
plugin ficar sem versão, se um segredo for escrito direto no arquivo ou se o job sair do contrato.

### O job `projeto-qualidade`

- lê o `Jenkinsfile` do repositório definido em `REPO_URL`;
- tem o parâmetro `BRANCH`, com padrão `main`: em **Construir com parâmetros**, dá para rodar o
  pipeline de qualquer branch;
- verifica o GitHub a cada 5 minutos (`H/5 * * * *`) e roda sozinho quando há commit novo. O
  polling usa a `BRANCH` do último build: depois de um build manual de outra branch, ele passa
  a olhar essa branch até um novo build com `BRANCH=main`.

### O pipeline

O `Jenkinsfile` é declarativo, com limite de 30 minutos por build, horário em cada linha do log
e os 20 builds mais recentes guardados.

| Etapa | O que faz | O que gera |
|---|---|---|
| Declarative: Checkout SCM | Clona o repositório na branch escolhida | Workspace |
| Setup | Apaga relatórios e pacotes de builds anteriores, cria o venv e instala o `requirements.txt` | `.venv/` |
| Test | Roda `pytest --junitxml=reports/junit.xml`; o gate de 90% de cobertura vem do `pytest.ini`. Publica o JUnit e arquiva `reports/**` mesmo quando um teste falha | Test Result e `reports/` |
| Build | Roda `python -m build` e arquiva o pacote com fingerprint | `dist/*.tar.gz` e `dist/*.whl` |
| Declarative: Post Actions | Em sucesso ou falha, chama `python3 scripts/notify_email.py --status <resultado>` | E-mail com o resultado |

Na página do job, o **Stage View** mostra cada etapa. Na página de cada build ficam o **Test
Result** e os **Artifacts**: o pacote e os relatórios. Tudo isso fica no volume
`jenkins_home` e continua lá depois de um `docker compose down` e `up`.

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

**Ferramenta:** Claude Opus 5.5, pelo Claude Code (extensão do VS Code), com acesso ao
repositório local.

**Como trabalhei com a ferramenta:** usei a IA como par de programação. A maior parte do código
da minha parte foi escrita por ela, em etapas pequenas que eu pedia na ordem do plano, uma
branch por item. Em cada etapa, a ferramenta explicava o que tinha feito e como tinha testado;
eu revisava o código, tirava as dúvidas, testava na minha máquina e pedia ajustes quando algo
não estava como eu queria. Eu mesmo criava as branches, fazia os commits e o push e abria os
PRs, e revisei cada PR antes de pedir a revisão do grupo.

**Para que usei:**

- planejamento da minha parte: o que era meu, a ordem de implementação e as dependências com
  os outros integrantes;
- código e testes: a estrutura do README da NP2, o serviço `jenkins` no Compose, o
  `jenkins/casc/jobs.yaml`, o `tests/unit/test_helpers.py`, o `reporting.py` e os testes dele,
  a origem do e-mail no `scripts/notify_email.py` e o envio pelo container `tests`;
- verificações: rodar a suíte e o Compose, subir um Jenkins temporário para testar o job e
  conferir a imagem publicada no Docker Hub;
- revisão dos PRs do Gabriel Renato (#22, #29, #30, #31, #39 e #42), testando cada um numa
  cópia separada do repositório;
- textos dos commits, dos PRs e desta seção.

**Prompts** (resumidos):

1. **Planejamento da minha parte**

   > "me explica o que é da minha parte no plano, em que ordem fazer e do que eu dependo dos
   > outros integrantes, para eu poder executar"

   **Resposta:** uma tabela com os meus itens, uma ordem sugerida e as dependências. O
   esqueleto do README e o job do Jenkins vieram primeiro, porque o Ian e o Gabriel Renato
   precisavam deles para testar as partes deles.

   **Resultado:** aceito. Segui essa ordem.

2. **Job do Jenkins criado por código**

   > "agora o job do Jenkins pelo `jobs.yaml`, seguindo o contrato: nome `projeto-qualidade`,
   > parâmetro `BRANCH` e repositório vindo do `REPO_URL`"

   **Resposta:** um script de Job DSL lido pelo JCasC. A IA explicou por que a branch fica como
   `*/^${BRANCH}`: sem o `^`, o JCasC trocaria a variável quando o Jenkins sobe, e o parâmetro
   escolhido em cada build seria ignorado. Ela testou num Jenkins temporário, e o build com
   `BRANCH=main` terminou em SUCCESS.

   **Resultado:** aceito. Depois, rodei o pipeline completo no Jenkins do Compose.

3. **Relatório consolidado no `reporting.py`**

   > "tira a lógica do relatório do `conftest.py` para o `reporting.py`, com testes, sem mudar
   > o relatório que todo mundo usa"

   **Resposta:** o `conftest.py` ficou só com os hooks do pytest, e a contagem por integrante
   virou uma classe testável. Os testes unitários ganharam um grupo próprio no relatório, e a
   cobertura do `conftest.py` subiu de 86% para 98%. A IA manteve o `import os` que o Gabriel
   Renato tinha acabado de adicionar, como ele pediu.

   **Resultado:** aceito. Abri o `reports/report.html` e conferi o título, a coluna e o resumo.

4. **Origem do e-mail e envio pelo container `tests`**

   > "o assunto do e-mail precisa dizer se veio do Jenkins ou do container `tests`, e o
   > `tests` precisa mandar o e-mail sem perder o código de saída da suíte"

   **Resposta:** antes de escrever o código, a IA explicou o plano: o Jenkins define
   `JENKINS_URL` em todo build, e o Docker cria `/.dockerenv` em todo container. No Compose, o
   `tests` roda a suíte, guarda o código de saída, chama o script e termina com esse código.
   Ela provou a falha apontando a API para um endereço inválido: o container terminou com
   código 1, e o e-mail de FAILURE chegou ao Mailpit.

   **Resultado:** aceito. Como o PR mexia no script do Ian e no bloco do Fabio, pedi a revisão
   dos dois.

5. **Revisão do PR #29 do Gabriel Renato**

   > "o Gabriel Renato disse que corrigiu o PR #29 em que eu pedi alteração; verifica comigo
   > se a correção resolveu antes de eu aprovar"

   **Resposta:** na primeira revisão, li o Jenkinsfile com a IA e pedi que ela gerasse o pacote
   da suíte, para conferir o que ia dentro dele. Faltavam o `scripts/notify_email.py` e o
   `.coveragerc`, e o `pytest` rodado a partir do pacote falharia. Depois da correção do
   Gabriel Renato, a mesma verificação achou um problema novo: o meu `reporting.py`, que tinha
   acabado de entrar na `main`, faltava no `pyproject.toml`.

   **Resultado:** aceito. Marquei o PR como "Request changes" duas vezes, escrevi no comentário
   o erro e a correção sugerida e só aprovei quando a suíte passou rodando a partir do pacote.

**O que fiz sem IA:**

- criei as branches, fiz os commits e o push e abri os PRs;
- ajustei à mão o texto de alguns PRs, escolhi os revisores e tomei as decisões de aprovar e
  mergear;
- configurei o Docker Hub: confirmei a conta, fiz o login e o push das tags `1.0.0` e `latest`
  e preenchi a descrição e o overview no site;
- operei o Docker Desktop e o Jenkins: subi o serviço, rodei o primeiro build do pipeline com
  parâmetros e simulei uma máquina limpa, baixando a imagem do Docker Hub;
- preenchi o `.env` local (que não é versionado);
- percebi que os comentários de revisão misturavam dois PRs e pedi um comentário para cada um.

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
