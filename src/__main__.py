from llm_sdk import Small_LLM_Model

from .reader_writer import load_functions, load_prompts, save_results
from .models import FunctionResult
from .contrained_decoder import ConstrainedDecoder, choose_function
from pathlib import Path


def main() -> None:

    try:
        functions = load_functions(
            Path("data/input/functions_definition.json")
        )

        prompts = load_prompts(
            Path("data/input/function_calling_tests.json")
        )

        model = Small_LLM_Model()
        decoder = ConstrainedDecoder(model)
        result: list[FunctionResult] = []

        for item in prompts:
            func_names = choose_function(decoder, item.prompt, functions)

            result.append(
                FunctionResult(
                    prompt=item.prompt,
                    name=func_names,
                    parameters={},
                )
            )

        save_results(result, Path("data/output/resultado.json"))
    except KeyboardInterrupt as e:
        print(e)

if __name__ == "__main__":
    main()
