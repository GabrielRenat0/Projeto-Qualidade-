def assert_campos(objeto, campos):
    for campo in campos:
        assert campo in objeto, f"Campo '{campo}' não encontrado no objeto"

def assert_json(resposta):
    assert "application/json" in resposta.headers.get("Content-Type", ""), "Response is not JSON"
    return resposta.json()
