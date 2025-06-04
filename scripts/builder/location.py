import dataclasses
from typing import NotRequired, Optional, TypedDict, Unpack
from .item import Item
from .category import Category


type RequirementInput = str | Item | Category | AmountRequirement


@dataclasses.dataclass
class AmountRequirement:
    subject: Item | Category
    amount: str


def some_of(subject: Item | Category, amount: int | str):
    return AmountRequirement(
        subject=subject,
        amount=amount if isinstance(amount, str) else str(amount),
    )


class Requirement:
    @staticmethod
    def from_input(input: RequirementInput) -> str:
        if isinstance(input, str):
            return input

        if isinstance(input, AmountRequirement):
            subject = Requirement.__format_subject(input.subject)
            return f"|{subject}:{input.amount}|"

        return f"|{Requirement.__format_subject(input)}|"

    @staticmethod
    def __format_subject(input: Item | Category) -> str:
        if isinstance(input, Category):
            return f"@{input.name}"
        return input.name


class LocationBase(TypedDict):
    region: NotRequired[str]
    place_item: NotRequired[list[str]]
    place_item_category: NotRequired[list[str]]
    victory: NotRequired[bool]


class LocationData(LocationBase):
    name: str
    category: NotRequired[list[str]]
    requires: NotRequired[str]


class LocationArgs(LocationBase):
    category: NotRequired[list[str | Category]]
    requires: NotRequired[Optional[RequirementInput]]


class Location:
    name: str
    data: LocationData

    def __init__(self, name: str, **kwargs: Unpack[LocationArgs]) -> None:
        category = kwargs.pop("category", None)
        requires = kwargs.pop("requires", None)

        self.name = name
        self.data = {"name": name, **kwargs}

        if category:
            self.data["category"] = Category.from_list_input(category)

        if requires:
            self.data["requires"] = Requirement.from_input(requires)
