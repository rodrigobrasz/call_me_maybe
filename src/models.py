#!/usr/bin/env python3

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal
from typing import Any

ParameterType = Literal[
    "string",
    "number",
    "integer",
    "boolean"
]


def validate_blank(cont: str) -> str:
    """

    Validates whether the checked content is empty or contains only spaces.

    Returns:
        The original string if it contains non-whitespace characters.

    """
    if not cont.strip():
        raise ValueError("Value cannot be empty.")
    return cont


class TypeDefinition(BaseModel):
    """
    Checks whether the types of the models/returns are correct

    extra=forbid
        -> Controls what pydantic does when it finds a key that
        is not declared in the class

    description = does not validate anything, it only serves as documentation
    """

    model_config = ConfigDict(extra="forbid")

    type: ParameterType = Field(..., description="The data type")


class FunctionDefinition(BaseModel):
    """

    Represent a function available for the language model

    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    parameters: dict[str, TypeDefinition]
    returns: TypeDefinition

    validate_name = field_validator("name")(validate_blank)

    validate_discription = field_validator("description")(validate_blank)

    @field_validator("parameters")
    @classmethod
    def validate_parameter(
                           cls, cont: dict[str, TypeDefinition]
                          ) -> dict[str, TypeDefinition]:
        """

        Exactly the same check as before, but for the content of parameters

        """

        for parameter_name in cont:
            if not parameter_name.strip():
                raise ValueError(
                                  "parameters cannot be empty or"
                                  "whitespaces only"
                                 )
        return cont


class PromptInput(BaseModel):
    """

    Represent one natural-language input prompt

    """

    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1,
                        description="The natural language prompt")

    validate_prompt = field_validator("prompt")(validate_blank)


class FunctionResult(BaseModel):
    """
    ...
    """

    model_config = ConfigDict(extra="forbid")

    prompt: str
    name: str
    parameters: dict[str, Any]
