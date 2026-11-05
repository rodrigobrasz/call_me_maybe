import json

from llm_sdk import Small_LLM_Model
from src.vocabulary import Vocabulary

model = Small_LLM_Model()
vocab_path = model.get_path_to_vocab_file()
v = Vocabulary(vocab_path)
with open(vocab_path, encoding="utf-8") as f:
    raw = json.load(f)

print("tokens no vocab.json:", len(raw))
print("tokens decodificados:", len(v.id_to_str))
print("descartados:", len(raw) - len(v.id_to_str))

print(repr(v.text_of(0)))                  # esperado: '!'
print(repr(v.text_of(raw["ĠParis"])))      # esperado: ' Paris'
print(repr(v.text_of(raw["Ċ"])))           # esperado: '\n'