#!/usr/bin/env python3

"""

Utilitários de decodificação de vocabulário para geração restrita em
modelos de linguagem.

Este módulo carrega o vocabulário do modelo de linguagem e converte cada
token da sua representação Unicode em nível de byte para texto UTF-8
legível.

O arquivo de vocabulário mapeia strings de tokens para IDs numéricos.
Alguns tokens contêm caracteres Unicode que representam valores de bytes
brutos. A função ``unicode_to_byte`` reconstrói esses valores de byte, e
a classe ``Vocabulary`` os decodifica em texto e armazena o mapeamento:

    ID do token -> texto decodificado

A classe ``Vocabulary`` é usada pelo decoder restrito depois que o modelo
produz os logits. Ela permite ao decoder descobrir o texto representado
por cada token candidato e restringir a geração a nomes de função válidos.

Este módulo é necessário porque o modelo trabalha com IDs numéricos de
tokens, enquanto o decoder precisa interpretar esses tokens como texto ao
validar o nome da função gerado.


"""

import json
from pathlib import Path


def unicode_to_byte() -> dict[str, int]:
    """

    BUilds a table that converts the characters used by the vocabulary
    int their corresponding byte values.

    Some of the bytes can be represented directly by regular characters.
    The remaining bytes values are represented by artificial Unicode
    characters start at Unicode point 256.

    Returns:
        A dictionary in the following format:

        vocabulary character -> original byte value

    """

#   lista de bytes que possam ser representados diretamente:
    _bytes = (
        list(range(33, 127))  # entre "!" a "~"
        + list(range(161, 173))  # entre "¡" e "¬" pulando o caracter "173"
        + list(range(174, 256))  # entre "®" e "ÿ"
    )

#   copia da lista
    chars = _bytes[:]
    extra = 0
    for b in range(256):
        if b not in _bytes:
            _bytes.append(b)
            chars.append(256 + extra)
            extra += 1

    result: dict[str, int] = {}

#   percorre as duas listas para dar o index certo
#   tipo chr(33) = "!"
    for b, c in zip(_bytes, chars):
        result[chr(c)] = b

    return result


class Vocabulary:
    """

    Load and decode a language model vocabulary.

    The vocabulary file maps token strings to IDs. Some
    token strings uses Unicode character as representations of
    raw bytes. This class converts those representations back into their
    original text, including spaces, line breaks and other special chacteres.

    Tokens that cant be converted into valid UFT-8 text are ignored
    and not added to the vocabulary. this provents invalid tokens from
    being selected or decoded by the decoder.

    UFT-8:
        Unicode trasnformation format: é um padrao de codificacao
        de caracteres de comprimento variavel que consegue representar
        todos os simbolos padrao "Unicode"

    """

    def __init__(self, path: str | Path) -> None:
        """

        Loads the vocabulary from a JSON file.

        Args:
            path: Path to the vocabulary JSON file.

        Each token is converted from its Unicode representation into raw
        bytes and then decoded into UTF-8 text.


        """
        with open(path, "r", encoding="utf-8") as f:
            llm_vocab: dict[str, int] = json.load(f)

        table = unicode_to_byte()
        self.id_to_str: dict[int, str] = {}

        # t = texto/representaocao do token
        # t_id = ID numerio do token no vocabulario
        for t, t_id in llm_vocab.items():
            try:
                # byte_values = [10]
                # data = bytes([10])
                # self.id_to_str = "\n"
                byte_values: list[int] = []

                for char in t:
                    byte_values.append(table[char])

                data = bytes(byte_values)
                self.id_to_str[t_id] = data.decode("utf-8")

            except (KeyError, UnicodeDecodeError):
                continue

    def text_of(self, t_id: int) -> str | None:
        """

        Returns the decoded text associated with a token ID.

        Args:
            t_id: Numeric ID of the token.

        Returns:
            The decoded token text, or None if the token ID is not present
            in the vocabulary.

        """
        return self.id_to_str.get(t_id)

# if __name__ == "__main__":
#    model = Small_LLM_Model()
#    vocabulary = Vocabulary(
#        model.get_path_to_vocab_file()
#    )
#    table = unicode_to_byte()

#    print("Teste da tabela:")
#    for char in ["A", "Ċ", "Ā"]:
#        print(
#            f"{repr(char)} -> "
#            f"byte {table[char]} -> "
#            f"Unicode {ord(char)}"
#        )

#    print("\nTeste do Vocabulary:")

#    for token_id in [0, 1, 2, 10, 42]:
#        print(
#            f"ID {token_id} -> "
#            f"{repr(vocabulary.text_of(token_id))}"
#        )