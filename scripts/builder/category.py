from typing import NotRequired, TypedDict, Unpack

from .options import ToggleOption


type OptionInput = str | ToggleOption


class CategoryArgs(TypedDict):
    hidden: NotRequired[bool]
    yaml_option: NotRequired[OptionInput | list[OptionInput]]


class CategoryData(TypedDict):
    hidden: NotRequired[bool]
    yaml_option: NotRequired[list[str]]


type CategoryInput = str | Category


class Category:
    name: str
    data: CategoryData

    def __init__(self, name: str, **kwargs: Unpack[CategoryArgs]) -> None:
        yaml_option = kwargs.pop("yaml_option", [])

        self.name = name
        self.data = {**kwargs}

        self.resolve_yaml_option_input(yaml_option)

    def resolve_yaml_option_input(self, input: OptionInput | list[OptionInput]):
        if isinstance(input, str):
            self.data["yaml_option"] = self.data.get("yaml_option") or []
            self.data["yaml_option"].append(input)
        elif isinstance(input, ToggleOption):
            self.data["yaml_option"] = self.data.get("yaml_option") or []
            self.data["yaml_option"].append(input.name)
        else:
            for input_item in input:
                self.resolve_yaml_option_input(input_item)

    @staticmethod
    def from_input(input: CategoryInput):
        return input if isinstance(input, str) else input.name

    @staticmethod
    def from_list_input(input: list[CategoryInput]):
        return [Category.from_input(it) for it in input]
