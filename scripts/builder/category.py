from typing import NotRequired, TypedDict, Unpack


class CategoryArgs(TypedDict):
    hidden: NotRequired[bool]
    yaml_option: NotRequired[list[str]]


type CategoryInput = str | Category


class Category:
    name: str
    data: CategoryArgs

    def __init__(self, name: str, **kwargs: Unpack[CategoryArgs]) -> None:
        self.name = name
        self.data = {**kwargs}

    @staticmethod
    def from_input(input: CategoryInput):
        return input if isinstance(input, str) else input.name

    @staticmethod
    def from_list_input(input: list[CategoryInput]):
        return [Category.from_input(it) for it in input]
