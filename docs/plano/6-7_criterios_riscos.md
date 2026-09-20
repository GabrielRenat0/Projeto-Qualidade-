## 6. Critérios de aceite

A suíte é considerada aprovada quando:

- os 20 casos de teste (TC-001 a TC-020) passam, o que corresponde a 23 execuções no `pytest`, porque o TC-002 e o TC-011 são parametrizados;
- a suíte completa roda em menos de 60 segundos;
- a execução funciona a partir de um clone limpo, seguindo apenas o README;
- o relatório HTML é gerado em `reports/`.

## 7. Riscos e limitações

- **Sistema testado é um mock.** O JSONPlaceholder não persiste dados: no TC-020, um post excluído continua sendo devolvido com 200. O `id` gerado nas criações foi 101 nas duas execuções observadas (TC-016 e TC-017), então ele não identifica um recurso de verdade.
- **Sem validação de payload.** O TC-016 (corpo vazio) e o TC-017 (tipos errados) recebem 201, e a API devolve os campos exatamente como foram enviados. Uma API real recusaria essas entradas com 400.
- **Erros 500 com detalhes internos expostos.** O TC-018 (PUT em post inexistente) e o TC-019 (JSON malformado) devolvem 500 em HTML, com stack trace do Node e caminhos internos do servidor. Uma API real devolveria 404 e 400, sem expor esses detalhes.
- **Testes de caracterização.** Os TC-016 a TC-020 afirmam o comportamento observado do mock, e não o esperado de uma API real. Se o serviço mudar, esses testes podem falhar sem que haja um defeito no projeto. O TC-019 chega a depender do texto `SyntaxError` da resposta e do header `Content-Type: application/json` enviado pela fixture, porque sem o header o mock responde 201.
- **Dependência de internet e do serviço.** A suíte só roda com acesso à internet e com o JSONPlaceholder disponível. Uma queda ou lentidão do serviço faz os testes falharem por causa externa.
- **Sem ambiente controlado.** Não há como preparar dados, isolar o ambiente ou observar o servidor, então os testes se limitam a chamar a API pública.
- **Limites do teste de estresse.** O serviço é público e gratuito, então a carga do k6 é mantida modesta. Os resultados mostram o comportamento nesse limite, não a capacidade real do sistema.
