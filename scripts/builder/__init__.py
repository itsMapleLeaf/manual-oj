import os
import shutil
import dataclasses
from dataclasses_json import DataClassJsonMixin
import json
from pathlib import Path
from typing import Unpack

from .options import ToggleOption, ToggleOptionArgs
from .location import Location, LocationArgs
from .item import Item, ItemArgs
from .category import Category, CategoryArgs


@dataclasses.dataclass
class GameInfo(DataClassJsonMixin):
    game: str
    creator: str


class WorldBuilder:
    items: dict[str, Item] = {}
    locations: dict[str, Location] = {}
    categories: dict[str, Category] = {}
    options: dict[str, ToggleOption] = {}

    def item(self, name: str, **kwargs: Unpack[ItemArgs]):
        return self.__set_unique("Items", self.items, name, Item(name=name, **kwargs))

    def location(self, name: str, **kwargs: Unpack[LocationArgs]):
        return self.__set_unique(
            "Locations", self.locations, name, Location(name=name, **kwargs)
        )

    def category(self, name: str, **kwargs: Unpack[CategoryArgs]):
        return self.__set_unique(
            "Categories", self.categories, name, Category(name, **kwargs)
        )

    def toggle_option(self, name: str, **kwargs: Unpack[ToggleOptionArgs]):
        return self.__set_unique(
            "Options", self.options, name, ToggleOption(name, **kwargs)
        )

    def generate_data(self):
        computed_item_count = sum(
            item.data.get("count", 1) for item in self.items.values()
        )
        print(f"{computed_item_count} items")
        print(f"{len(self.locations)} locations")
        print(f"{len(self.categories)} categories")
        print(f"{len(self.options)} options")

        Path("src/data/items.json").write_text(
            json.dumps(
                [it.data for it in self.items.values()],
                indent=4,
            )
        )

        Path("src/data/locations.json").write_text(
            json.dumps(
                [it.data for it in self.locations.values()],
                indent=4,
            )
        )

        Path("src/data/categories.json").write_text(
            json.dumps(
                {k: opt.data for k, opt in self.categories.items()},
                indent=4,
            )
        )

        Path("src/data/options.json").write_text(
            json.dumps(
                {
                    "core": {},
                    "user": {k: opt.data for k, opt in self.options.items()},
                },
                indent=4,
            )
        )

        return BuilderOutput()

    @staticmethod
    def __set_unique[K, V](dict_name: str, dict: dict[K, V], key: K, value: V) -> V:
        if key in dict:
            raise Exception(f'key "{key}" already exists in "{dict_name}"')
        dict[key] = value
        return value


class BuilderOutput:
    def build_world(self):
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

        return self
