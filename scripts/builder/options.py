from typing import Literal, TypedDict, Unpack


class Option:
    name: str


class ToggleOptionArgs(TypedDict):
    description: str | list[str]
    default: bool


class ToggleOptionData(ToggleOptionArgs):
    type: Literal["Toggle"]


class ToggleOption(Option):
    data: ToggleOptionData

    def __init__(self, name: str, **kwargs: Unpack[ToggleOptionArgs]) -> None:
        self.name = name
        self.data = {"type": "Toggle", **kwargs}


# TODO: other options lol
