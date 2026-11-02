#!/usr/bin/env python3

import json
from pathlib import Path


def unicode_to_byte() -> dict[str, int]:
    """
    com esse metodo eu vou fazer a conversao de
    unicode para um byte(como assim byte)
    usando a variavel "_bytes" eu crio uma
    lista com os caracters
    aceitos, depois eu itero num range
    de 256 bytes para cada caracter...

    Unicode:
        é um padrao usado para associar simbolos ou caracteres a valores
        numericos
        ex:
            ord("A") = "65"
            ord("ç") = "311"
    """
#   criei uma lista com todos os caracteres validos
    _bytes = (
        list(range(33, 127))  # entre "!" a "~"
        + list(range(161, 173))  # entre "¡" e "¬" pulando o caracter "173"
        + list(range(174, 256))  # entre "®" e "ÿ"
    )

    chars = _bytes[:]
    extra = 0
    for b in range(256):
        if b not in _bytes:
            _bytes.append(b)
            chars.append(256 + extra)
            extra += 1

    result: dict[str, int] = {}

#   percorro as duas listas para dar o index certo
#   tipo chr(33) = "!"
    for b, c in zip(_bytes, chars):
        result[chr(c)] = b

    return result


class Vocabulary:
    """

    Load and decode a language model vocabulary.

    The vocabulary file maps token strings to IDs. SOme
    token stringes use Unicode character as representations of
    raw bytes. This class converts those representations back into their
    original text, including spaces, line breaks and other special chacteres.

    Tokens that cant be converted into valid UFT-8 text are ignored
    and not added to the vocabulary. this provents invalid tokens from
    being selected or decoded by the decoder.

    """
    def __init__(self, path: str | Path) -> None:
        """

        Load the vocabulary from a Json file.

        the file is read using UTF-8 enconding. Each token is converted
        from its unicode byte representations into raw bytes then decoded
        as UTF-8 text.

        Path:
            Path to the vocabulary file.

        """
        with open(path, "r", encoding="utf-8") as f:
            llm_vocab: dict[str, int] = json.load(f)

        table = unicode_to_byte()
        self.id_to_str: dict[int, str] = {}

        for t, t_id in llm_vocab.items():
            try:
                data = bytes(table[char] for char in t)
                self.id_to_str[t_id] = data.decode("utf-8")
            except (KeyError, UnicodeDecodeError):
                continue

    def text_of(self, t_id: int) -> str | None:
        """

        return the decoded text associated with a token ID.

        """
        return self.id_to_str.get(t_id)
