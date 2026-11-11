## 1. Escopo

### 1.1 Sistema testado

O JSONPlaceholder é uma API REST pública e gratuita que simula os recursos de um blog
(posts, comentários, usuários, tarefas, álbuns e fotos). Ele é mantido como serviço de
apoio para protótipos e treinamento, não exige autenticação e aceita tanto leitura quanto
escrita. As operações de escrita são simuladas: a resposta vem como se o recurso tivesse
sido criado ou alterado, mas o servidor não guarda a alteração.

Esse ponto delimita todo o trabalho. A suíte verifica o **contrato de resposta** da API,
não o estado do sistema depois de cada operação.

### 1.2 Recursos e endpoints cobertos

| Recurso | Endpoints exercitados | Casos de teste |
|---|---|---|
| `/posts` | `GET /posts`, `GET /posts/{id}`, `POST /posts`, `PUT /posts/{id}`, `PATCH /posts/{id}`, `DELETE /posts/{id}` | TC-001, TC-002, TC-003, TC-007 a TC-012, TC-014, TC-016 a TC-020 |
| `/comments` | `GET /posts/{id}/comments`, `GET /comments?postId=` | TC-004, TC-015 |
| `/users` | `GET /users/{id}` | TC-005 |
| `/todos` | `GET /todos?completed=` | TC-006 |
| Rota inexistente | `GET /nonexistent-resource` | TC-013 |

São 20 casos de teste, divididos em 10 com dados válidos e 10 com dados inválidos ou
inoportunos. Como o TC-002 e o TC-011 são parametrizados, o relatório mostra 23 execuções.

### 1.3 Fora do escopo

| Item | Motivo |
|---|---|
| Recursos `/albums` e `/photos` | Repetem o mesmo padrão de resposta já coberto por `/posts` e `/comments` |
| Autenticação e autorização | A API é aberta e não expõe nenhum mecanismo de acesso |
| Testes de interface | O sistema não possui interface gráfica |
| Testes de segurança | Não há credenciais, sessões ou dados sensíveis envolvidos |
| Persistência dos dados | O mock não grava alterações; essa limitação é documentada pelo TC-020 e tratada na seção 7 |
| Desempenho dentro da suíte `pytest` | Coberto à parte pelos testes de carga e estresse em k6 (bônus), com relatórios em `perf/results/` |

## 2. Objetivos

O objetivo geral é comprovar, por linha de comando e de forma repetível, que a API
responde conforme o contrato documentado e que o comportamento diante de entradas
inválidas é conhecido e registrado.

| Objetivo | Como é verificado | Casos de teste |
|---|---|---|
| Confirmar o contrato de resposta dos recursos | Presença dos campos esperados em cada item devolvido, incluindo os objetos aninhados `address.geo` e `company` | TC-001, TC-002, TC-004, TC-005 |
| Confirmar os códigos HTTP das operações bem-sucedidas | Asserção do status exato (200 ou 201) de cada operação | TC-001 a TC-010 |
| Confirmar os filtros por query string | Quantidade e conteúdo dos itens devolvidos para cada filtro | TC-003, TC-004, TC-006 |
| Confirmar as operações de escrita | Eco dos campos enviados e preservação dos campos não enviados | TC-007, TC-008, TC-009, TC-010 |
| Verificar o comportamento com entrada inválida | Status exato e corpo devolvidos para IDs fora da faixa válida, ID não numérico, rota inexistente e filtros sem resultado | TC-011 a TC-015 |
| Documentar as limitações do sistema testado | Asserção do comportamento observado, com o comportamento esperado de uma API real registrado em comentário no próprio teste | TC-016 a TC-020 |

Não é objetivo desta suíte apontar defeitos a corrigir no JSONPlaceholder: ele é um mock
declarado como tal, e as divergências encontradas alimentam a seção de riscos e
limitações, não um relatório de bugs.

## 3. Estratégia

### 3.1 Abordagem

A estratégia é de **caixa-preta**. Os testes atuam apenas pela interface HTTP pública, sem
acesso ao código-fonte, ao banco de dados ou aos logs do servidor, e a verificação recai
sobre o que a resposta expõe: status, headers e corpo. A escolha dos dados de entrada é
guiada por duas técnicas de projeto de teste, aplicadas em conjunto.

### 3.2 Particionamento de equivalência

Os dados de entrada são agrupados em classes que a API deveria tratar da mesma forma, e
cada classe é exercitada por pelo menos um caso de teste.

| Partição | Exemplo de dado | Classe | Casos de teste |
|---|---|---|---|
| ID de post dentro da faixa existente (1 a 100) | 1, 100 | Válida | TC-002, TC-004, TC-008, TC-009, TC-010 |
| ID de post abaixo da faixa | 0 | Inválida | TC-011 |
| ID de post acima da faixa | 101, 999999 | Inválida | TC-011, TC-018 |
| ID de post não numérico | `abc` | Inválida | TC-012 |
| Rota existente | `/posts`, `/users/1` | Válida | TC-001, TC-005 |
| Rota inexistente | `/nonexistent-resource` | Inválida | TC-013 |
| Filtro com resultado | `userId=1`, `completed=true` | Válida | TC-003, TC-006 |
| Filtro sem resultado | `userId=9999`, `postId=-1` | Inválida | TC-014, TC-015 |
| Corpo de requisição completo e bem tipado | `valid_post`, `updated_post` | Válida | TC-007, TC-008 |
| Corpo de requisição vazio, mal tipado ou malformado | `{}`, `title` numérico, JSON quebrado | Inválida | TC-016, TC-017, TC-019 |

### 3.3 Análise de valor limite

A faixa válida de IDs de post é de 1 a 100, então os testes atacam as duas fronteiras e os
valores imediatamente vizinhos, que é onde erros de comparação costumam aparecer.

| Valor | Posição em relação ao limite | Resultado esperado | Caso de teste |
|---|---|---|---|
| 0 | Imediatamente abaixo do limite inferior | 404 | TC-011 (`below_lower_bound`) |
| 1 | Limite inferior | 200 | TC-002 (`lower_bound`) |
| 100 | Limite superior | 200 | TC-002 (`upper_bound`) |
| 101 | Imediatamente acima do limite superior | 404 | TC-011 (`above_upper_bound`) |

O TC-011 ainda inclui o valor 999999 (`far_above_upper_bound`). Ele não é um limite: serve
para confirmar que um valor bem distante da faixa recebe o mesmo tratamento que o vizinho
imediato, ou seja, que a partição inválida é uniforme.

### 3.4 Testes de caracterização

Os TC-016 a TC-020 exercitam entradas que uma API real deveria recusar, mas que o mock
aceita. Como o objetivo é documentar o sistema como ele é, esses testes afirmam o
comportamento **observado** (201 onde caberia 400, 500 onde caberia 404, 200 onde caberia
404) e trazem, em comentário, o comportamento que seria esperado em produção. Essa escolha
é o que liga a suíte à seção 7 do plano.

### 3.5 Regras comuns a todos os casos

- Os testes ficam em dois arquivos, `tests/test_valid_data.py` (TC-001 a TC-010) e
  `tests/test_invalid_data.py` (TC-011 a TC-020), selecionáveis pelos markers `valid` e `invalid`.
- Cada teste carrega o identificador no nome da função e na primeira linha da docstring.
- Os casos são independentes entre si: nenhum depende da execução ou do resultado de outro,
  e a ordem de execução não altera o resultado.
- A massa de dados fica em `data/payloads.json` e chega aos testes pela fixture `payloads`,
  que entrega uma cópia por teste. O `parametrize` recebe apenas rótulos, e o valor é lido
  da fixture dentro do teste.
- Os asserts afirmam o status exato observado, nunca uma faixa como `>= 400`.
- Antes de qualquer verificação sobre todos os itens de uma lista, a suíte confirma o
  tamanho esperado dela, para que uma lista vazia não faça o teste passar sem testar nada.
