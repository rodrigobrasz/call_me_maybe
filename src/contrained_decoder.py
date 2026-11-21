#!/usr/bin/env python3

from .models import FunctionDefinition
from llm_sdk import Small_LLM_Model
from typing import Any
from .vocabulary import Vocabulary
import torch


class ConstrainedDecoder:
    NUMBER_CHAR = set("0123456789.- ")

    def __init__(self, model: Small_LLM_Model) -> None:
        self.model = model
        self.vocabulary = Vocabulary(
            model.get_path_to_vocab_file()
        )

    def build_mask(self, kind: str) -> str:
        size = len(self.gen_logit_ids(self.constrained_encode("a")))

        ids: set[int] = set()
        stop: set[int] = set()

        for token_id, txt in self.vocabulary.id_to_str.items():
            if not txt:
                continue

            if kind == "number":
                if set(txt) <= self.NUMBER_CHAR:
                    ids.add(token_id)
                if txt.lstrip()[:1] in (",", "}"):
                    stop.add(token_id)
            else:  # "string"
                if '"' in txt:
                    stop.add(token_id)
                elif "\n" not in txt:
                    ids.add(token_id)

        mask = self.make_mask(ids | stop, size)
        mask_no_stop = self.make_mask(ids, size)
        return mask, mask_no_stop, stop

        

    def constrained_decode(self, ids: list[int]) -> str:
        return (self.model.decode(ids))

    def constrained_encode(self, text: str) -> list[int]:
        return (self.model.encode(text)[0].tolist())

    def gen_logit_ids(self, input_ids: list[int]) -> list[float]:
        return self.model.get_logits_from_input_ids(input_ids)

    @staticmethod
    def make_mask(ids: list[int], size: int) -> torch.Tensor:
        mask = torch.full((size,), float("-inf"))
        mask[list(ids)] = 0.0
        return mask

    def constrained_loop(
            self,
            input_ids: list[int],
            kind: str,
            max_tokens: int = 32,
    ) -> str:
        genereted: list[int] = []

        allow_stop = len(genereted) > 0
        best, best_score = None, float("-inf")

        for _ in range(max_tokens):
            logits = self.gen_logit_ids(input_ids + genereted)
            allow_stop = len(genereted) > 0

            best, best_score = None, float("-inf")
            best_is_stop = False

            for token_id, score in enumerate(torch.as_tensor(logits).tolist()):
                txt = self.vocabulary.text_of(token_id)
                if not txt:
                    continue

                if kind == "number":
                    is_stop = txt.lstrip()[:1] in (",", "}")
                    is_valid = all(c in self.NUMBER_CHAR for c in txt)
                else:
                    is_stop = '"' in txt
                    is_valid = '"' not in txt and "\n" not in txt

                if is_stop and not allow_stop:
                    continue

                if (is_valid or is_stop) and score > best_score:
                    best, best_score = token_id, score
                    best_is_stop = is_stop

            if best is None:
                break

            if best_is_stop:
                txt = self.vocabulary.text_of(best) or ""
                tail = txt.split('"')[0] if '"' in txt else ""
                break

            genereted.append(best)

        return self.constrained_decode(genereted) + tail

    def generated_numbers(self, content: str) -> str:
        input_ids = self.constrained_encode(content)
        raw = self.constrained_loop(input_ids, "number", max_tokens=32).strip()
        try:
            float(raw)
        except ValueError:
            raise ValueError(f"Invalid number: {raw!r}")
        return raw

    def generated_string(self, content: str) -> str:
        input_ids = self.constrained_encode(content + ' "')
        return self.constrained_loop(input_ids, "string", max_tokens=32)

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

        # nome da funcao: id
        candidate_ids = {
            candidate: self.constrained_encode(" " + candidate)
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

        decoded = self.constrained_decode(generated_ids).strip()
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

    function_template = (
        "Choose the function that better fits to this prompt. \n"
        "Return only the function name. \n\n"
        "Do not solve the "
        f"Avaliable functions {func_name_description}\n"
        f"User request: {prompt}\n"
        "Function name:"
    )

    input_ids = decoder.constrained_encode(function_template)

    return decoder.generated_from_candidates(
        input_ids=input_ids,
        candidates=func_names,
    )


def choose_parameters(
        decoder: ConstrainedDecoder,
        prompt: str,
        function: FunctionDefinition
        ) -> dict[str, Any]:

    param_desc = "\n".join(
        f"- {name}: {info.type}"
        for name, info in function.parameters.items()
    )

    prefix = (
        "<|im_start|>system\n"
        "Extract the function arguments from the user request.\n"
        "Copy values exactly as written in the request.\n"
        "For regex parameters use the standard regex syntax\n"
        "(e.g. \\d+, \\s+ for whitespaces).<|im_end|>\n"
        "<|im_start|>user\n"
        f"Function: {function.name}\n"
        f"Description: {function.description}\n"
        f"Parameters:\n{param_desc}\n"
        f"Request: {prompt}\n"
        "Extract only the parameter values from the request.<|im_end|>\n"
        "<|im_start|>assistant\n"
        "JSON: {"
    )

    results: dict[str, Any] = {}

    for i, (name, info) in enumerate(function.parameters.items()):
        key = ("" if i == 0 else ", ") + f'"{name}":'

        if info.type == "number":
            raw = decoder.generated_numbers(prefix + key)

            try:
                results[name] = float(raw)
            except ValueError:
                raise ValueError(f"Invalid number for {name!r}: {raw!r}")

            prefix += f"{key} {raw}"

        elif info.type == "integer":
            raw = decoder.generated_numbers(prefix + key)

            try:
                results[name] = int(raw)
            except ValueError:
                raise ValueError(f"Invalid integer for {name!r}: {raw!r}")

            prefix += f"{key} {raw}"

        elif info.type == "boolean":
            raw = decoder.generated_string(prefix + key).lower()

            if raw not in {"true", "false"}:
                raise ValueError(f"Invalid boolean for {name!r}: {raw!r}")

            results[name] = raw == "true"
            prefix += f'{key} "{raw}"'

        else:
            raw = decoder.generated_string(prefix + key)
            results[name] = raw
            prefix += f'{key} "{raw}"'

    return results
