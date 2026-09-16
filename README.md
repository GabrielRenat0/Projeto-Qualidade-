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
git clone <URL_DO_SEU_REPOSITORIO>
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