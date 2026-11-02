#!/usr/bin/env python3

from .models import FunctionDefinition
from typing import Callable
from llm_sdk import Small_LLM_Model
from .vocabulary import Vocabulary


class ConstrainedDecoder:
    def __init__(self, model: Small_LLM_Model) -> None:
        self.model = model
        self.vocabulary = Vocabulary(
            model.get_path_to_vocab_file()
        )

    def choose_next_token(
            self,
            input_ids: list[int],
            generated: str,
            is_valid: Callable[[str, str], bool]
    ) -> tuple[int, str]:
        """

        esse metodo escolhe o token com maior logit para ser o proximo
        token gerado

        input_ids: tokens que ja foram enviados a LLM

        generated: texto gerado ate agora

        is_valid: funcao que decide se o token pode ser adicionado
        retorna uma tupla (id do token, texto do token)

        """

        logits = self.model.get_logits_from_input_ids(input_ids)

        best_id: int | None = None
        best_score = float("-inf")
        best_txt: str = ""

        for t_id, score in enumerate(logits):
            # pego o id numerico do token e procuro o texto
            # correspondente do vocabulario
            t_text = self.vocabulary.text_of(t_id)

            if t_text is None:
                continue

            if not is_valid(generated, t_text):
                continue

            if score > best_score:
                best_id = t_id
                best_score = score
                best_txt = t_text

        if best_id is None:
            raise ValueError("No valid token was found.")

        return best_id, best_txt

    def text_generator(
            self,
            input_ids: list[int],
            is_valid: Callable[[str, str], bool],
            is_complete: Callable[[str], bool],
            max_new_tokens: int = 128,
    ) -> str:
        """

        Sua funcao é:
            controla o ciclo
            consulta os logits

        """
        cur_ids = list(input_ids)
        generated = ""

        for _ in range(max_new_tokens):
            t_id, t_text = self.choose_next_token(
                cur_ids,
                generated,
                is_valid,
            )

            cur_ids.append(t_id)
            generated += t_text

            if is_complete(generated):
                break

        return generated


def choose_func_name(
        decoder: ConstrainedDecoder,
        prompt: str,
        functions: list[FunctionDefinition],
) -> str:
    """

    select a valid function name using contrained decoding.

    """

    func_names = [function.name for function in functions]
#   print(func_names)

    if not func_names:
        raise ValueError("No functions available")

    input_ids = decoder.model.encode(prompt)[0].tolist()

    def is_valid(genereted: str, t_next: str) -> bool:
        """
        genereted: texto gerado ate agora

        t_next: proximo token candidato
        """
        candidated = (genereted + t_next).strip()
        # check se candidated é prefixo de pelomenos um nome valido
        return any(name.startswith(candidated) for name in func_names)

    def is_complete(generated: str) -> bool:
        return generated.strip() in func_names

    result = decoder.text_generator(
        input_ids=input_ids,
        is_valid=is_valid,
        is_complete=is_complete,
        max_new_tokens=32,
    ).strip()

    if result not in func_names:
        raise ValueError(
            f"Invalid function name: {result!r}"
        )

    return result