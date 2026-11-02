

Comparação do UV com outros gerenciadores de pacotes:

```mermaid
%%{init: {"xyChart": {"width": 350, "height": 150, "titleFontSize": 8}}}%%
xychart-beta horizontal
    title "Tempo de resolução (s)"
    x-axis ["uv", "poetry", "pdm", "pip-sync"]
    y-axis "segundos" 0 --> 5
    bar [0.06, 0.99, 1.90, 4.63]


Estrutura do Projeto
    src/
    ├── __main__.py       # argumentos CLI e fluxo principal
    ├── reader.py         # lê e valida os JSONs de entrada
    ├── models.py         # modelos Pydantic
    ├── vocabulary.py     # token_id → texto
    ├── decoder.py        # constrained decoding
    └── errors.py         # erros personalizados


greedy decoding -> PESQUISAR


More about pydantic:
- https://pydantic.dev/docs/validation/dev/concepts/fields/
- https://www.youtube.com/watch?v=FcWdzqCpj5c


UV:
- https://hub.asimov.academy/blog/uv-python/


Json:
- https://www.geeksforgeeks.org/python/json-dumps-in-python/