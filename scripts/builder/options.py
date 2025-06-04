from typing import Literal, TypedDict, Unpack


class ToggleOptionArgs(TypedDict):
    description: str | list[str]
    default: bool


class ToggleOptionData(ToggleOptionArgs):
    type: Literal["Toggle"]


class ToggleOption:
    name: str
    data: ToggleOptionData

    def __init__(self, name: str, **kwargs: Unpack[ToggleOptionArgs]) -> None:
        self.name = name
        self.data = {"type": "Toggle", **kwargs}
