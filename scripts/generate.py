from os import environ
import os
import shutil
from dataclasses import is_dataclass
import dataclasses
from dataclasses_json import DataClassJsonMixin, dataclass_json
import json
from pathlib import Path
from typing import Dict, List, Optional, cast
from dotenv import load_dotenv
from pydantic import BaseModel


@dataclasses.dataclass
class Item(DataClassJsonMixin):
    name: str
    category: Optional[list[str]] = None
    count: Optional[int] = None
    value: Optional[dict[str, int]] = None
    progression: Optional[bool] = None
    progression_skip_balancing: Optional[bool] = None
    useful: Optional[bool] = None
    trap: Optional[bool] = None
    filler: Optional[bool] = None
    early: Optional[bool] = None
    local: Optional[bool] = None
    local_early: Optional[bool] = None


@dataclass_json
@dataclasses.dataclass
class Location(DataClassJsonMixin):
    name: str
    category: Optional[list[str]] = None
    requires: Optional[str] = None
    region: Optional[str] = None
    place_item: Optional[list[str]] = None
    place_item_category: Optional[list[str]] = None
    victory: Optional[bool] = None


@dataclass_json
@dataclasses.dataclass
class GameContent(DataClassJsonMixin):
    campaigns: Dict[str, List[str]]
    characters: List[str]
    cards: List[str]
    goals: List[str]


@dataclass_json
@dataclasses.dataclass
class GameInfo(DataClassJsonMixin):
    game: str
    creator: str


def remove_none(data):
    if isinstance(data, dict):
        return {k: remove_none(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_none(item) for item in data]
    else:
        return data


if __name__ == "__main__":
    load_dotenv()

    content = GameContent.from_json(
        Path("src/data/content.json").read_text(encoding="utf-8")
    )

    items: list[Item] = []
    locations: list[Location] = []

    campaigns = content.campaigns.copy()
    extras = campaigns["Extras"]
    campaigns.pop("Extras")

    for campaign, episodes in campaigns.items():
        unlock_item = Item(
            campaign,
            category=["Campaigns"],
            progression=True,
        )
        items.append(unlock_item)

        for episode in episodes:
            locations.append(
                Location(
                    f"{campaign}: {episode}",
                    category=[f"(Campaign) {campaign}"],
                    requires=f"|{unlock_item.name}|",
                )
            )

        completion_item = Item(
            f"{campaign} (All Episodes)",
            category=["Completed Campaigns"],
            progression=True,
        )
        items.append(completion_item)

        locations.append(
            Location(
                completion_item.name,
                category=[f"(Campaign Completion) {campaign}"],
                requires=f"|{unlock_item.name}|",
                place_item=[completion_item.name],
            )
        )

    for campaign in extras:
        unlock_item = Item(
            campaign,
            category=["Campaigns"],
            progression=True,
        )
        items.append(unlock_item)

        completion_item = Item(
            f"{campaign} (Complete)",
            category=["Completed Campaigns"],
            progression=True,
        )
        items.append(completion_item)

        # one location for finding a randomized item, and another for the actual progression
        locations.append(
            Location(
                campaign,
                category=["(Extras)"],
                requires=f"|{unlock_item.name}|",
            )
        )
        locations.append(
            Location(
                f"{campaign} (All Episodes)",
                category=["(Extras Completion)"],
                requires=f"|{unlock_item.name}|",
                place_item=[completion_item.name],
            )
        )

    for character in content.characters:
        items.append(
            Item(
                character,
                category=["Characters"],
                useful=True,
            )
        )

    for card in content.cards:
        items.append(Item(card, category=["Cards"], useful=True, count=2))

    for goal in content.goals:
        locations.append(Location(goal, category=["(Goals)"]))

    locations.append(
        Location(
            "69,420,000,000 Oranges",
            category=["((Victory))"],
            requires="|@Completed Campaigns:80%|",
            victory=True,
        )
    )

    Path("src/data/items.json").write_text(
        json.dumps(
            [remove_none(dataclasses.asdict(item)) for item in items],
            indent=4,
        )
    )

    Path("src/data/locations.json").write_text(
        json.dumps(
            [remove_none(dataclasses.asdict(item)) for item in locations],
            indent=4,
        )
    )

    game_info = GameInfo.from_json(Path("src/data/game.json").read_text("utf-8"))
    world_name = f"manual_{game_info.game}_{game_info.creator}"

    source_dir = Path("src")
    temp_dir = Path("dist") / world_name

    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    shutil.copytree(source_dir, temp_dir)

    output_zip = shutil.make_archive(world_name, "zip", root_dir="dist", base_dir=".")
    output_folder = (
        os.getenv("OUTPUT_FOLDER") or "C:/ProgramData/Archipelago/custom_worlds"
    )
    shutil.move(
        output_zip,
        Path(output_folder) / f"{world_name}.apworld",
    )
