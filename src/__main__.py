#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

from llm_sdk import Small_LLM_Model
from src.models import FunctionResult
from .reader_writer import load_functions, load_prompts, save_results
from src.contrained_decoder import ConstrainedDecoder, choose_function, choose_parameters


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Function calling with constrained decoding"
    )
    parser.add_argument(
        "--functions_definition",
        type=Path,
        default=Path("data/input/functions_definition.json"),
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/input/function_calling_tests.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/function_calling_results.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        functions = load_functions(args.functions_definition)
        prompts = load_prompts(args.input)
    except Exception as e:
        sys.exit(f"Error: {e}")

    by_name = {function.name: function for function in functions}

    model = Small_LLM_Model()
    decoder = ConstrainedDecoder(model)

    results: list[FunctionResult] = []

    for prompt_input in prompts:
        prompt = prompt_input.prompt

        try:
            name = choose_function(decoder, prompt, functions)
            parameters = choose_parameters(
                decoder,
                prompt,
                by_name[name],
            )

            results.append(
                FunctionResult(
                    prompt=prompt,
                    name=name,
                    parameters=parameters,
                )
            )
        except (ValueError, KeyError) as e:
            print(
                f"Skipping prompt {prompt!r}: {e}",
                file=sys.stderr,
            )
            continue

    save_results(results, args.output)


if __name__ == "__main__":
    main()