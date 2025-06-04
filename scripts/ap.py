import os
import shutil
import dataclasses
from dataclasses_json import DataClassJsonMixin
import json
from pathlib import Path
from typing import Any, Literal, NotRequired, Optional, TypedDict, Unpack


class CategoryArgs(TypedDict):
    hidden: NotRequired[bool]
    yaml_option: NotRequired[str]


class Category(CategoryArgs):
    type: Literal["category"]
    name: str


class ItemArgs(TypedDict):
    count: NotRequired[int]
    value: NotRequired[dict[str, int]]
    progression: NotRequired[bool]
    progression_skip_balancing: NotRequired[bool]
    useful: NotRequired[bool]
    trap: NotRequired[bool]
    filler: NotRequired[bool]
    early: NotRequired[bool]
    local: NotRequired[bool]
    local_early: NotRequired[bool]


class Item(ItemArgs):
    type: Literal["item"]
    name: str
    category: NotRequired[list[str]]


class LocationArgs(TypedDict):
    region: NotRequired[str]
    place_item: NotRequired[list[str]]
    place_item_category: NotRequired[list[str]]
    victory: NotRequired[bool]


class Location(LocationArgs):
    type: Literal["location"]
    name: str
    category: NotRequired[list[str]]
    requires: NotRequired[str]


class ToggleOption(TypedDict):
    name: str
    description: str | list[str]
    default: bool


@dataclasses.dataclass
class AmountRequirement:
    subject: Item | Category
    amount: str


def some_of(subject: Item | Category, amount: int | str):
    return AmountRequirement(
        subject=subject,
        amount=amount if isinstance(amount, str) else str(amount),
    )


type RequiresInput = str | Item | Category | AmountRequirement


@dataclasses.dataclass
class GameInfo(DataClassJsonMixin):
    game: str
    creator: str


def without_keys(dict: dict | Any, *keys: str):
    return {k: v for k, v in dict.items() if k not in keys}


def remove_item_keys(items: list[dict | Any], *keys: str):
    return [without_keys(dict, *keys) for dict in items]


class Builder:
    items: dict[str, Item] = {}
    locations: dict[str, Location] = {}
    categories: dict[str, Category] = {}
    options: dict[str, ToggleOption] = {}

    def item(
        self,
        name: str,
        category: list[str | Category] = [],
        **kwargs: Unpack[ItemArgs],
    ):
        if name in self.items:
            raise Exception(f"Item {name} already exists")

        item = Item(name=name, type="item", **kwargs)

        if category:
            item["category"] = self.normalize_categories(category)

        self.items[name] = item
        return item

    def location(
        self,
        name: str,
        category: Optional[list[str | Category]] = None,
        requires: Optional[RequiresInput] = None,
        **kwargs: Unpack[LocationArgs],
    ):
        if name in self.locations:
            raise Exception(f"Location {name} already exists")

        location = Location(name=name, type="location", **kwargs)

        if category:
            location["category"] = self.normalize_categories(category)

        if requires:
            location["requires"] = self.normalize_requires(requires)

        self.locations[name] = location
        return location

    def category(
        self,
        name: str,
        **kwargs: Unpack[CategoryArgs],
    ):
        if name in self.categories:
            raise Exception(f"Category {name} already exists")

        category = Category(name=name, type="category", **kwargs)
        self.categories[name] = category
        return category

    def toggle_option(
        self,
        name: str,
        description: str | list[str],
        default: bool,
    ):
        if name in self.options:
            raise Exception(f"Option {name} already exists")

        option = ToggleOption(name=name, description=description, default=default)
        self.options[name] = option
        return option

    def build(self):
        print(f"{len(self.items)} items")
        print(f"{len(self.locations)} locations")
        print(f"{len(self.categories)} categories")
        print(f"{len(self.options)} options")

        Path("src/data/items.json").write_text(
            json.dumps(
                remove_item_keys([*self.items.values()], "type"),
                indent=4,
            )
        )

        Path("src/data/locations.json").write_text(
            json.dumps(
                remove_item_keys([*self.locations.values()], "type"),
                indent=4,
            )
        )

        Path("src/data/categories.json").write_text(
            json.dumps(
                {
                    k: without_keys(opt, "name", "type")
                    for k, opt in self.categories.items()
                },
                indent=4,
            )
        )

        Path("src/data/options.json").write_text(
            json.dumps(
                {
                    "core": {},
                    "user": {
                        k: without_keys(opt, "name", "type")
                        for k, opt in self.categories.items()
                    },
                },
                indent=4,
            )
        )

        game_info = GameInfo.from_json(Path("src/data/game.json").read_text("utf-8"))
        world_name = f"manual_{game_info.game}_{game_info.creator}"

        source_dir = Path("src")
        dist_dir = Path("dist")
        temp_dir = dist_dir / world_name

        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        shutil.copytree(source_dir, temp_dir)

        output_zip = shutil.make_archive(
            world_name, "zip", root_dir=dist_dir, base_dir="."
        )
        output_folder = (
            os.getenv("OUTPUT_FOLDER") or "C:/ProgramData/Archipelago/custom_worlds"
        )
        output_path = Path(output_folder) / f"{world_name}.apworld"
        shutil.move(output_zip, output_path)
        print(f"saved world to {output_path}")

    @staticmethod
    def normalize_categories(input: list[str | Category]):
        return [it if isinstance(it, str) else it["name"] for it in input]

    @staticmethod
    def normalize_requires(input: RequiresInput) -> str:
        if isinstance(input, str):
            return input

        if isinstance(input, AmountRequirement):
            subject = Builder.normalize_require_subject(input.subject)
            return f"|{subject}:{input.amount}|"

        return f"|{Builder.normalize_require_subject(input)}|"

    @staticmethod
    def normalize_require_subject(input: Item | Category) -> str:
        if input.get("type") == "category":
            return f"@{input["name"]}"
        return input["name"]
