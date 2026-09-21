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

---

## 🗺️ Mapa de Casos de Teste (ID → Arquivo)

Nossos 20 casos de testes automatizados (TC) estão distribuídos em 2 principais blocos e utilizam os dados estáticos isolados no arquivo `data/payloads.json`:

| Cenário de Teste | ID dos Testes | Arquivo Responsável |
|---|---|---|
| **Testes com Dados Válidos (Sucesso)** | TC-001 ao TC-010 | `tests/test_valid_data.py` |
| **Testes com Dados Inválidos/Inoportunos** | TC-011 ao TC-020 | `tests/test_invalid_data.py` |

---

## 🤖 Declaração de Uso de Inteligência Artificial

Em conformidade com o **Item 11 do enunciado** do projeto, o grupo declara que fez uso de ferramentas baseadas em Inteligência Artificial para apoio pontual durante a construção deste repositório (ex: estruturação da arquitetura base, apoio no setup inicial e dicas de legibilidade no padrão do Pytest).

Ressaltamos que todo o grupo revisou ativamente o código sugerido e detém pleno entendimento de todos os comandos, lógicas e arquivos presentes nesta entrega, assumindo inteira responsabilidade por sua qualidade e corretude em arguição técnica.