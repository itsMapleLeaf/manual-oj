from dataclasses import dataclass
from typing import NotRequired, Optional, TypedDict, Unpack
from .item import Item
from .category import Category


class RequirementNode:
    def to_string(self):
        raise NotImplementedError()


@dataclass
class RequirementSubject(RequirementNode):
    name: str
    amount: Optional[str | int] = None
    is_category: bool = False

    @staticmethod
    def normalize(input: Item | Category, amount: str | int | None = None):
        return RequirementSubject(
            input.name, amount=amount, is_category=isinstance(input, Category)
        )

    def to_string(self):
        result = "|"

        if self.is_category:
            result += "@"

        result += self.name

        if self.amount != None:
            result += ":" + str(self.amount)

        result += "|"

        return result


@dataclass
class RequirementBinaryExpression(RequirementNode):
    children: list[RequirementNode]
    operator: str

    def to_string(self):
        infix = f" {self.operator} "
        members = infix.join(node.to_string() for node in self.children)
        return f"({members})"


type RequirementInput = str | Item | Category | RequirementNode


def serialize_requirement(input: RequirementInput) -> str:
    if isinstance(input, str):
        return input

    if isinstance(input, Item):
        return RequirementSubject(input.name).to_string()

    if isinstance(input, Category):
        return RequirementSubject(input.name, is_category=True).to_string()

    return input.to_string()


def some_of(subject: Item | Category, amount: str | int):
    return RequirementSubject.normalize(subject, amount)


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
            self.data["requires"] = serialize_requirement(requires)
