## 4. Ambiente

### 4.1 Sistema testado

| Item | Valor |
|---|---|
| Sistema | JSONPlaceholder, API REST pública e gratuita |
| URL base | `https://jsonplaceholder.typicode.com` |
| Autenticação | Não exige |
| Dependências externas | Acesso à internet e disponibilidade do serviço |

### 4.2 Tecnologias e versões

| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.11 (execução local com 3.11.9) | Linguagem da suíte de testes |
| pytest | 8.3.3 | Execução dos testes e seleção pelos markers `valid` e `invalid` |
| requests | 2.32.3 | Cliente HTTP das chamadas à API |
| pytest-html | 4.1.1 | Relatório de execução em `reports/report.html` |
| k6 | 2.2.0 | Teste de carga (bônus) |
| GitHub Actions | `actions/checkout`, `actions/setup-python` e `actions/upload-artifact` na versão 7 | Integração contínua |

As versões de `requests`, `pytest` e `pytest-html` estão fixadas no `requirements.txt`.
As dependências indiretas, como `pytest-metadata` e `Jinja2`, são instaladas
automaticamente pelo `pip`.

### 4.3 Ambientes de execução

| Ambiente | Sistema operacional | Como roda |
|---|---|---|
| Local | Windows 11 Pro | Ambiente virtual `.venv` com as dependências do `requirements.txt` |
| Integração contínua | GitHub Actions, `ubuntu-latest` | A cada pull request e a cada push na `main`, com Python 3.11 instalado do zero |

### 4.4 Como reproduzir

O `README.md` descreve a instalação e a execução: criar o ambiente virtual, instalar o
`requirements.txt` e rodar `pytest`. O teste de carga exige o k6 instalado e está
documentado na seção "Testes de Performance (bônus)" do README.
