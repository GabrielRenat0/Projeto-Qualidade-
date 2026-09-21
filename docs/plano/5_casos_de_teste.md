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
| TC-006 | Filtrar tarefas concluídas | API acessível | `completed_todos_filter`: `completed="true"` | `GET /todos?completed=true` | 200; lista não vazia de tarefas, todas com `completed=True` |
| TC-007 | Criar um novo post | API acessível | `valid_post`: objeto contendo `title`, `body` e `userId` | `POST /posts` | 201; presença de um `id` numérico gerado e o eco exato dos campos `title`, `body` e `userId` enviados |
| TC-008 | Substituir um post (PUT) | API acessível; post 1 existente | `updated_post`: objeto contendo `id`, `title`, `body` e `userId` | `PUT /posts/1` | 200; `id` retornado igual a 1 e todos os demais campos atualizados exatamente como enviados no corpo da requisição |
| TC-009 | Atualizar título do post (PATCH) | API acessível; post 1 com `userId=1` | `partial_patch`: objeto contendo apenas `title`; `partial_patch_case`: `post_id` 1 e `expected_user_id` 1 | `PATCH /posts/1` | 200; campo `title` alterado de acordo com o enviado e o campo não enviado `userId` deve ser preservado intacto (mantendo o valor original 1) |
| TC-010 | Excluir um post | API acessível; post 1 existente | `valid_post_id_to_delete`: 1 | `DELETE /posts/1` | 200; corpo da resposta deve ser estritamente um objeto JSON vazio `{}` |
| TC-011 | Buscar post com ID fora da faixa válida | API acessível | `out_of_range_post_ids`: 0 (abaixo do limite inferior), 101 (acima do limite superior) e 999999 (bem acima da faixa) | `GET /posts/{id}` | 404; corpo em JSON com um objeto vazio `{}` (3 execuções, uma por valor) |
| TC-012 | Buscar post com ID não numérico | API acessível | `invalid_type_post_id`: texto `abc` | `GET /posts/abc` | 404; corpo em JSON com um objeto vazio `{}` |
| TC-013 | Acessar uma rota inexistente | API acessível | `nonexistent_resource`: `nonexistent-resource` | `GET /nonexistent-resource` | 404; corpo em JSON com um objeto vazio `{}` |
| TC-014 | Filtrar posts por usuário inexistente | API acessível; nenhum post do usuário 9999 | `nonexistent_user_filter`: `userId=9999` | `GET /posts?userId=9999` | 200; lista vazia `[]`, e não um erro |
| TC-015 | Filtrar comentários por ID de post negativo | API acessível | `negative_comment_filter`: `postId=-1` | `GET /comments?postId=-1` | 200; lista vazia `[]`, e não um erro |
| TC-016 | Criar post com corpo vazio | API acessível | `empty_post`: objeto vazio `{}` | `POST /posts` | 201; resposta com `id` numérico e sem `title`, `body` e `userId`. Comportamento observado do mock: não valida o payload (uma API real devolveria 400) |
| TC-017 | Criar post com tipos de campo inválidos | API acessível | `post_with_invalid_types`: `title` numérico (2026) e `userId` em texto | `POST /posts` | 201; `id` numérico gerado; `title` e `userId` devolvidos com os mesmos valores e tipos enviados (`int` e `str`). Comportamento observado: sem validação de schema (uma API real devolveria 400) |
| TC-018 | Atualizar post inexistente (PUT) | API acessível; post 999999 inexistente | `nonexistent_post_id`: 999999; `update_nonexistent_post`: `title`, `body` e `userId` válidos, sem `id` | `PUT /posts/999999` | 500; corpo em HTML (`text/html`) com stack trace. Comportamento observado: o mock quebra ao atualizar recurso inexistente (uma API real devolveria 404) |
| TC-019 | Criar post com JSON malformado | API acessível; cliente envia `Content-Type: application/json` | `malformed_json`: texto `{title: broken json`, enviado cru | `POST /posts` com o corpo em `data=` | 500; corpo em HTML com `SyntaxError` do parse. Sem o header JSON o mock responde 201. Comportamento observado: erro de parse não tratado (uma API real devolveria 400) |
| TC-020 | Consultar post depois de excluí-lo | API acessível; post 1 existente | `post_id_to_delete`: 1 | `DELETE /posts/1` seguido de `GET /posts/1` | DELETE 200; GET ainda 200 com `id` igual a 1. Comportamento observado: o mock não persiste a exclusão (uma API real devolveria 404) |
