#!/usr/bin/env python3

from .models import FunctionDefinition
from llm_sdk import Small_LLM_Model
from typing import Any
from .vocabulary import Vocabulary
import json


class ConstrainedDecoder:
    def __init__(self, model: Small_LLM_Model) -> None:
        self.model = model
        self.vocabulary = Vocabulary(
            model.get_path_to_vocab_file()
        )

    def generated_from_candidates(
            self,
            input_ids: list[int],
            candidates: list[str],
    ) -> str:
        """"

        palmeiras

        """

        if not candidates:
            raise ValueError("No candidates avalible")

        # nome da função: id
        candidate_ids = {
            candidate: self.model.encode(" " + candidate)[0].tolist()
            for candidate in candidates
        }

        # busca a maior quantidade de tokens por funcao para usar na iteração
        max_tokens = max(len(ids) for ids in candidate_ids.values())

        generated_ids: list[int] = []

        for _ in range(max_tokens):
            valid_ids: set[int] = set()

            # percorre por todos os ids das funcoes
            for tokens in candidate_ids.values():
                # posicao do proximo token
                prefix_size = len(generated_ids)

                # pega o prefix do token dos candidatos e compara
                # com os que ja foram gerados
                if tokens[:prefix_size] == generated_ids:
                    if prefix_size < len(tokens):
                        valid_ids.add(tokens[prefix_size])

            if not valid_ids:
                raise ValueError("No valid id found")

            logits = self.model.get_logits_from_input_ids(
                input_ids + generated_ids
            )

            best_id = max(valid_ids, key=lambda token_id: logits[token_id])
            generated_ids.append(best_id)

            if any(ids == generated_ids
                   for ids in candidate_ids.values()):
                break

        decoded = self.model.decode(generated_ids).strip()
        if decoded not in candidates:
            raise ValueError(f"Invalid generated candidated {decoded!r}")

        return decoded


def choose_function(
        decoder: ConstrainedDecoder,
        prompt: str,
        functions: list[FunctionDefinition],
) -> str:
    """
    func_names:
        Guarda o nome de todas as funcoes disponiveis.

    avaliable functions:
        Guarda o nome da função junto de sua descrição.
        Ex:
           ->fn_add_numers: Add two numbers together and return their sum.

    template:
        Vai ser usado como base para a LLM saber qual é o token mais provavel
        para cada prompt

    input_ids:
        Vai ter para cada prompt o seu template.

    Avaliable functions - fn_add_numbers: Add two numbers together and return
    their sum.
    - fn_greet: Generate a greeting message for a person by name.
    - fn_reverse_string: Reverse a string and return the reversed result.
    - fn_get_square_root: Calculate the square root of a number.
    - fn_substitute_string_with_regex: Replace all occurrences matching a
    regex pattern in a string.User
    request: What is the sum of 2 and 3?Function name:
    Choose the function that best matches de request.
    Return only the function name.
    Tudo isso sera tokenizado e enviado a LLM

    """

    # nome de todas funcoes
    func_names = [f.name for f in functions]

    if not func_names:
        raise ValueError("No function avalible")

    # nome da funcao e sua descricao
    func_name_description = "\n".join(
        f"- {function.name}: {function.description}"
        for function in functions
    )

    template = (
        "Choose the function that better fits to this prompt. \n"
        "Return only the function name. \n\n"
        "Do not solve the "
        f"Avaliable functions {func_name_description}\n"
        f"User request: {prompt}\n"
        "Function name:"
    )

    input_ids = decoder.model.encode(template)[0].tolist()

    return decoder.generated_from_candidates(
        input_ids=input_ids,
        candidates=func_names,
    )
