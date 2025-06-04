from typing import NotRequired, TypedDict, Unpack

from .category import Category, CategoryInput


class ItemBase(TypedDict):
    count: NotRequired[int]
    progression: NotRequired[bool]
    progression_skip_balancing: NotRequired[bool]
    useful: NotRequired[bool]
    trap: NotRequired[bool]
    filler: NotRequired[bool]
    early: NotRequired[bool]
    local: NotRequired[bool]
    local_early: NotRequired[bool]
    value: NotRequired[dict[str, int]]


class ItemArgs(ItemBase):
    category: NotRequired[list[CategoryInput]]


class ItemData(ItemBase):
    name: str
    category: NotRequired[list[str]]


class Item:
    name: str
    data: ItemData

    def __init__(self, name: str, **kwargs: Unpack[ItemArgs]) -> None:
        category_input = kwargs.pop("category", None)
        self.name = name
        self.data = {"name": name, **kwargs}
        if category_input:
            self.data["category"] = Category.from_list_input(category_input)
