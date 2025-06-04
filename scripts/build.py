from dataclasses import dataclass
import re
from dataclasses_json import DataClassJsonMixin
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from .builder.location import some_of
from .builder import WorldBuilder, Category, Item


@dataclass
class CampaignData:
    episodes: Optional[int] = None
    dlc: Optional[str] = None


@dataclass
class CardData:
    count: int


@dataclass
class CharacterData:
    goal: Optional[str] = None
    dlc: Optional[str] = None


@dataclass
class ContentData(DataClassJsonMixin):
    campaigns: dict[str, CampaignData]
    characters: dict[str, CharacterData]
    card_packs: dict[str, dict[str, CardData]]
    victory_campaign: str


class OrangeJuiceWorldBuilder(WorldBuilder):
    dlc_categories: dict[str, Category] = {}

    def resolve_dlc_category(self, name: str | None) -> list[Category]:
        if not name:
            return []

        if name in self.dlc_categories:
            return [self.dlc_categories[name]]

        dlc_category = self.category(
            f"{name} DLC",
            hidden=True,
            yaml_option=self.toggle_option(
                f"enable_{to_snake_case(name)}_dlc",
                description=f"Enables the {name} DLC.",
                default=True,
            ),
        )

        self.dlc_categories[name] = dlc_category

        return [dlc_category]

    def build(self):
        content = ContentData.from_json(
            Path("src/data/content.json").read_text(encoding="utf-8")
        )

        characters_category = self.category(
            "Characters",
            yaml_option=self.toggle_option(
                "include_characters",
                description="Add characters to the pool, requiring unlocking them to use them. Disable this to allow using all characters throughout the game.",
                default=True,
            ),
        )

        cards_category = self.category(
            "Cards",
            yaml_option=self.toggle_option(
                "include_cards",
                description="Add cards to the pool, requiring unlocking them to use them. Disable this to allow using all cards throughout the game.",
                default=True,
            ),
        )

        for campaign_name, campaign_info in content.campaigns.items():
            campaign_location_category = f"(Campaign) {campaign_name}"

            campaign_unlock_item = self.item(
                (
                    f"{campaign_name} (Campaign)"
                    if campaign_name in content.characters
                    else campaign_name
                ),
                progression=True,
                category=["Campaigns", *self.resolve_dlc_category(campaign_info.dlc)],
            )

            if campaign_info.episodes:
                for episode_index in range(campaign_info.episodes):

                    self.location(
                        f"{campaign_name} (Episode {episode_index + 1})",
                        requires=campaign_unlock_item,
                        category=[
                            campaign_location_category,
                            *self.resolve_dlc_category(campaign_info.dlc),
                        ],
                    )

                self.location(
                    f"{campaign_name} (Final Episode)",
                    requires=campaign_unlock_item,
                    category=[
                        campaign_location_category,
                        *self.resolve_dlc_category(campaign_info.dlc),
                    ],
                )
            else:
                self.location(
                    campaign_name,
                    requires=campaign_unlock_item,
                    category=[
                        campaign_location_category,
                        *self.resolve_dlc_category(campaign_info.dlc),
                    ],
                )

        for character_name, character_info in content.characters.items():
            if not character_info.goal:
                character_item = self.item(
                    character_name,
                    useful=True,
                    category=[
                        characters_category,
                        *self.resolve_dlc_category(character_info.dlc),
                    ],
                )
            else:
                character_item = self.item(
                    character_name,
                    progression=True,
                    category=[
                        characters_category,
                        *self.resolve_dlc_category(character_info.dlc),
                    ],
                )

                character_goal_requires = f"|{character_item.name}|"

                # grosest shit i've ever written
                character_dlc_category = self.resolve_dlc_category(character_info.dlc)
                if len(character_dlc_category) > 0:
                    character_goal_requires = f"|@{character_dlc_category[0].name}| and {character_goal_requires}"

                self.location(
                    f"{character_name}: {character_info.goal}",
                    category=["(Goals)"],
                    requires=f"{{OptAll({character_goal_requires})}}",
                )

        for card_pack_name, card_pack_dict in content.card_packs.items():
            for card_name, card_info in card_pack_dict.items():
                card_pack_dlc_category = (
                    self.resolve_dlc_category(card_pack_name)
                    if card_pack_name != "Base Pack"
                    else []
                )
                self.item(
                    card_name,
                    count=card_info.count,
                    useful=True,
                    category=[cards_category, *card_pack_dlc_category],
                )

        orange = self.item(
            "Orange",
            progression=True,
            filler=True,
            count=30,
            category=["Oranges"],
        )

        self.location(
            f"{content.victory_campaign} (Victory)",
            victory=True,
            requires=some_of(orange, "70%"),
            category=["((Victory))"],
        )

        self.generate_data().build_world()


def to_snake_case(text: str):
    words = re.findall(r"[A-Z0-9]?[a-z0-9]+", text)
    return "_".join(words).lower()


if __name__ == "__main__":
    load_dotenv()
    OrangeJuiceWorldBuilder().build()
