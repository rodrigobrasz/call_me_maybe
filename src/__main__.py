from pathlib import Path

from llm_sdk import Small_LLM_Model

from .contrained_decoder import (
    ConstrainedDecoder,
    choose_func,
)
from .reader import load_functions, load_prompts


def main() -> None:

    functions = load_functions(
        Path("data/input/functions_definition.json")
    )

    prompts = load_prompts(
        Path("data/input/function_calling_tests.json")
    )

    model = Small_LLM_Model()
    decoder = ConstrainedDecoder(model)

    for prompt in prompts:
        function_list = "\n".join(
            f"- {function.name}: {function.description}"
            for function in functions
        )

        selection_prompt = (
            f"{function_list}\n\n"
            f"User request: {prompt.prompt}\n"
            "Function name:"
        )
        function_name = choose_func(
            decoder,
            selection_prompt,
            functions,
        )

        print(
            {
                "prompt": prompt.prompt,
                "name": function_name,
            }
        )


if __name__ == "__main__":
    main()


#    dadasdasdsa