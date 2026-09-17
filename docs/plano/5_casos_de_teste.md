## 5. Descrição dos casos de teste

Os testes estão em `tests/test_valid_data.py` (TC-001 a TC-010) e
`tests/test_invalid_data.py` (TC-011 a TC-020). Cada função de teste leva o ID no nome
(ex.: `test_tc001_list_all_posts`). Os dados de entrada ficam em `data/payloads.json`, e a
coluna "Dados de entrada" mostra a chave usada e o valor.

| ID | Nome | Pré-condição | Dados de entrada | Ação | Resultado esperado |
|---|---|---|---|---|---|
| TC-001 | Listar todos os posts | API acessível | — | `GET /posts` | 200; lista com 100 posts, todos com `id`, `userId`, `title` e `body` |
| TC-002 | Buscar post nos limites válidos de ID | API acessível | `valid_boundary_post_ids`: 1 e 100 | `GET /posts/{id}` | 200; `id` igual ao solicitado e campos do post presentes (2 execuções, uma por limite) |
| TC-003 | Filtrar posts por usuário | API acessível | `user_posts_filter`: `userId=1` | `GET /posts?userId=1` | 200; 10 posts, todos com `userId=1` |
| TC-004 | Listar comentários de um post | API acessível; post 1 com comentários | `post_id_with_comments`: 1 | `GET /posts/1/comments` | 200; 5 comentários com `postId=1`, com `id`, `name`, `email` e `body` presentes e e-mail contendo `@` |
| TC-005 | Buscar usuário com objetos aninhados | API acessível; usuário 1 existente | `existing_user_id`: 1 | `GET /users/1` | 200; `id` igual ao solicitado; `address` (com `geo.lat` e `geo.lng` em texto não vazio) e `company` (`name`, `catchPhrase` e `bs`) presentes |
| TC-006 | Filtrar tarefas concluídas | API acessível | Filtro na query: `completed="true"` | `GET /todos?completed=true` | 200; lista não vazia de tarefas, todas com `completed=True` |
| TC-007 | Criar um novo post | API acessível | `valid_post`: objeto contendo `title`, `body` e `userId` | `POST /posts` | 201; presença de um `id` numérico gerado e o eco exato dos campos `title`, `body` e `userId` enviados |
| TC-008 | Substituir um post (PUT) | API acessível; post 1 existente | `updated_post`: objeto contendo `id`, `title`, `body` e `userId` | `PUT /posts/1` | 200; `id` retornado igual a 1 e todos os demais campos atualizados exatamente como enviados no corpo da requisição |
| TC-009 | Atualizar título do post (PATCH) | API acessível; post 1 com `userId=1` | `partial_patch`: objeto contendo apenas `title` | `PATCH /posts/1` | 200; campo `title` alterado de acordo com o enviado e o campo não enviado `userId` deve ser preservado intacto (mantendo o valor original 1) |
| TC-010 | Excluir um post | API acessível; post 1 existente | — | `DELETE /posts/1` | 200; corpo da resposta deve ser estritamente um objeto JSON vazio `{}` |
| TC-011 | *A preencher* | | | | |
| TC-012 | *A preencher* | | | | |
| TC-013 | *A preencher* | | | | |
| TC-014 | *A preencher* | | | | |
| TC-015 | *A preencher* | | | | |
| TC-016 | *A preencher* | | | | |
| TC-017 | *A preencher* | | | | |
| TC-018 | *A preencher* | | | | |
| TC-019 | *A preencher* | | | | |
| TC-020 | *A preencher* | | | | |
