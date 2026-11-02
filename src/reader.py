import json

from pathlib import Path
from typing import Any

from pydantic import ValidationError
from .models import PromptInput, FunctionDefinition
from .errors import InputFileError


def load_json(path: Path) -> Any:
    """
    Carrego o ficheiro passado como parametro e tento abri-lo
    verificando alguns erros.
    """

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, OSError, json.JSONDecodeError) as e:
        error = type(e).__name__

#       "from e" para preservar a causa original da excessao.
        if error == "FileNotFoundError":
            raise InputFileError(f"File not found '{path}'") from e

        if error == "JSONDecodeError":
            raise InputFileError(
                                f"Invalid Json File: {path}: {e}"
                                f"Line {e.lineno}"
                                ) from e
        raise InputFileError(f"Could not read '{path}': {e}") from e


def load_functions(path: Path) -> list[FunctionDefinition]:
    """
    Esse metodo eu estou carregando as funcoes do arquivo json
    enviado em "path"
    """
    function_data = load_json(path)
    # colocar um try para verificar se esse caminho existe

    if not isinstance(function_data, list):
        raise InputFileError(
            f"Expected a Json list in {path}"
        )

    functions: list[FunctionDefinition] = []

    for i, item in enumerate(function_data):
        try:
            function = FunctionDefinition.model_validate(item)
        except ValidationError as e:
            raise InputFileError(
                                f"INvalid function index {i} in path {path}"
                                f"error: {e}"
                                ) from e

        functions.append(function)
    return functions


def load_prompts(path: Path) -> list[PromptInput]:
    """
    Mesma coisa que o metodo anterior porem esse é para os prompts
    """
    prompt_data = load_json(path)

    if not isinstance(prompt_data, list):
        raise InputFileError(
                            f"Expected a Json file in {path}"
                            )

    prompts: list[PromptInput] = []

    for i, item in enumerate(prompt_data):

        try:
            prompt = PromptInput.model_validate(item)
        except ValidationError as e:
            raise InputFileError(
                                f"Invalid prompt as index {i} in path {path}"
                                f"error: {e}"
                                ) from e

        prompts.append(prompt)
    return prompts
