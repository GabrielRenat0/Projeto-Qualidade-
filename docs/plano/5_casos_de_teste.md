## 5. DescriÃ§Ã£o dos casos de teste

Os testes estÃ£o em `tests/test_valid_data.py` (TC-001 a TC-010) e
`tests/test_invalid_data.py` (TC-011 a TC-020). Cada funÃ§Ã£o de teste leva o ID no nome
(ex.: `test_tc001_list_all_posts`). Os dados de entrada ficam em `data/payloads.json`, e a
coluna "Dados de entrada" mostra a chave usada e o valor.

| ID | Nome | PrÃ©-condiÃ§Ã£o | Dados de entrada | AÃ§Ã£o | Resultado esperado |
|---|---|---|---|---|---|
| TC-001 | Listar todos os posts | API acessÃ­vel | â€” | `GET /posts` | 200; lista com 100 posts, todos com `id`, `userId`, `title` e `body` |
| TC-002 | Buscar post nos limites vÃ¡lidos de ID | API acessÃ­vel | `valid_boundary_post_ids`: 1 e 100 | `GET /posts/{id}` | 200; `id` igual ao solicitado e campos do post presentes (2 execuÃ§Ãµes, uma por limite) |
| TC-003 | Filtrar posts por usuÃ¡rio | API acessÃ­vel | `user_posts_filter`: `userId=1` | `GET /posts?userId=1` | 200; 10 posts, todos com `userId=1` |
| TC-004 | Listar comentÃ¡rios de um post | API acessÃ­vel; post 1 com comentÃ¡rios | `post_id_with_comments`: 1 | `GET /posts/1/comments` | 200; 5 comentÃ¡rios com `postId=1`, com `id`, `name`, `email` e `body` presentes e e-mail contendo `@` |
| TC-005 | Buscar usuÃ¡rio com objetos aninhados | API acessÃ­vel; usuÃ¡rio 1 existente | `existing_user_id`: 1 | `GET /users/1` | 200; `id` igual ao solicitado; `address` (com `geo.lat` e `geo.lng` em texto nÃ£o vazio) e `company` (`name`, `catchPhrase` e `bs`) presentes |
| TC-006 | Filtrar tarefas concluÃ­das | API acessÃ­vel | Filtro na query: `completed="true"` | `GET /todos?completed=true` | 200; lista nÃ£o vazia de tarefas, todas com `completed=True` |
| TC-007 | Criar um novo post | API acessÃ­vel | `valid_post`: objeto contendo `title`, `body` e `userId` | `POST /posts` | 201; presenÃ§a de um `id` numÃ©rico gerado e o eco exato dos campos `title`, `body` e `userId` enviados |
| TC-008 | Substituir um post (PUT) | API acessÃ­vel; post 1 existente | `updated_post`: objeto contendo `id`, `title`, `body` e `userId` | `PUT /posts/1` | 200; `id` retornado igual a 1 e todos os demais campos atualizados exatamente como enviados no corpo da requisiÃ§Ã£o |
| TC-009 | Atualizar tÃ­tulo do post (PATCH) | API acessÃ­vel; post 1 com `userId=1` | `partial_patch`: objeto contendo apenas `title` | `PATCH /posts/1` | 200; campo `title` alterado de acordo com o enviado e o campo nÃ£o enviado `userId` deve ser preservado intacto (mantendo o valor original 1) |
| TC-010 | Excluir um post | API acessÃ­vel; post 1 existente | â€” | `DELETE /posts/1` | 200; corpo da resposta deve ser estritamente um objeto JSON vazio `{}` |
| TC-011 | Buscar post com ID fora da faixa vÃ¡lida | API acessÃ­vel | `out_of_range_post_ids`: 0 (abaixo do limite inferior), 101 (acima do limite superior) e 999999 (bem acima da faixa) | `GET /posts/{id}` | 404; corpo em JSON com um objeto vazio `{}` (3 execuÃ§Ãµes, uma por valor) |
| TC-012 | Buscar post com ID nÃ£o numÃ©rico | API acessÃ­vel | `invalid_type_post_id`: texto `abc` | `GET /posts/abc` | 404; corpo em JSON com um objeto vazio `{}` |
| TC-013 | Acessar uma rota inexistente | API acessÃ­vel | `nonexistent_resource`: `nonexistent-resource` | `GET /nonexistent-resource` | 404; corpo em JSON com um objeto vazio `{}` |
| TC-014 | Filtrar posts por usuÃ¡rio inexistente | API acessÃ­vel; nenhum post do usuÃ¡rio 9999 | `nonexistent_user_filter`: `userId=9999` | `GET /posts?userId=9999` | 200; lista vazia `[]`, e nÃ£o um erro |
| TC-015 | Filtrar comentÃ¡rios por ID de post negativo | API acessÃ­vel | `negative_comment_filter`: `postId=-1` | `GET /comments?postId=-1` | 200; lista vazia `[]`, e nÃ£o um erro |
| TC-016 | Criar post com corpo vazio | API acessÃ­vel | `empty_post`: objeto vazio `{}` | `POST /posts` | 201; resposta com `id` numÃ©rico e sem `title`, `body` e `userId`. Comportamento observado do mock: nÃ£o valida o payload (uma API real devolveria 400) |
| TC-017 | Criar post com tipos de campo invÃ¡lidos | API acessÃ­vel | `post_with_invalid_types`: `title` numÃ©rico (2026) e `userId` em texto | `POST /posts` | 201; `id` numÃ©rico gerado; `title` e `userId` devolvidos com os mesmos valores e tipos enviados (`int` e `str`). Comportamento observado: sem validaÃ§Ã£o de schema (uma API real devolveria 400) |
| TC-018 | Atualizar post inexistente (PUT) | API acessÃ­vel; post 999999 inexistente | `nonexistent_post_id`: 999999; `update_nonexistent_post`: `title`, `body` e `userId` vÃ¡lidos, sem `id` | `PUT /posts/999999` | 500; corpo em HTML (`text/html`) com stack trace. Comportamento observado: o mock quebra ao atualizar recurso inexistente (uma API real devolveria 404) |
| TC-019 | Criar post com JSON malformado | API acessÃ­vel; cliente envia `Content-Type: application/json` | `malformed_json`: texto `{title: broken json`, enviado cru | `POST /posts` com o corpo em `data=` | 500; corpo em HTML com `SyntaxError` do parse. Sem o header JSON o mock responde 201. Comportamento observado: erro de parse nÃ£o tratado (uma API real devolveria 400) |
| TC-020 | Consultar post depois de excluÃ­-lo | API acessÃ­vel; post 1 existente | `post_id_to_delete`: 1 | `DELETE /posts/1` seguido de `GET /posts/1` | DELETE 200; GET ainda 200 com `id` igual a 1. Comportamento observado: o mock nÃ£o persiste a exclusÃ£o (uma API real devolveria 404) |
