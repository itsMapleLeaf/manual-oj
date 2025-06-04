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


@dataclass
class ContentData(DataClassJsonMixin):
    campaigns: dict[str, CampaignData]
    characters: dict[str, CharacterData]
    cards: dict[str, CardData]
    victory_campaign: str


class OrangeJuiceWorldBuilder(WorldBuilder):
    dlc_categories: dict[str, Category] = {}

    def resolve_dlc_category(self, name: str):
        if name in self.dlc_categories:
            return self.dlc_categories[name]

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

        return dlc_category

    def build(self):
        content = ContentData.from_json(
            Path("src/data/content.json").read_text(encoding="utf-8")
        )

        for campaign_name, campaign_info in content.campaigns.items():
            campaign_location_category = f"(Campaign) {campaign_name}"

            # making this a list allows cleanly appending it conditionally
            dlc_categories = (
                [self.resolve_dlc_category(campaign_info.dlc)]
                if campaign_info.dlc
                else []
            )

            campaign_unlock_item = self.item(
                (
                    f"{campaign_name} (Campaign)"
                    if campaign_name in content.characters
                    else campaign_name
                ),
                progression=True,
                category=["Campaigns", *dlc_categories],
            )

            if campaign_info.episodes:
                for episode_index in range(campaign_info.episodes):

                    self.location(
                        f"{campaign_name} (Episode {episode_index + 1})",
                        requires=campaign_unlock_item,
                        category=[campaign_location_category, *dlc_categories],
                    )

                self.location(
                    f"{campaign_name} (Final Episode)",
                    requires=campaign_unlock_item,
                    category=[campaign_location_category, *dlc_categories],
                )
            else:

                self.location(
                    campaign_name,
                    requires=campaign_unlock_item,
                    category=[campaign_location_category, *dlc_categories],
                )

        characters_category = self.category(
            "Characters",
            yaml_option=self.toggle_option(
                "randomize_characters",
                description="Add characters to the pool, requiring unlocking them to use them. Disable this to allow using all characters throughout the game.",
                default=True,
            ),
        )

        for character_name, character_info in content.characters.items():
            character_item = self.item(
                character_name,
                useful=True,
                category=characters_category,
            )

            if character_info.goal:
                self.location(
                    f"{character_name}: {character_info.goal}",
                    category=["(Goals)"],
                    requires=f"{{OptOne({character_item.name})}}",
                )

        cards_category = self.category(
            "Characters",
            yaml_option=self.toggle_option(
                "randomize_cards",
                description="Add cards to the pool, requiring unlocking them to use them. Disable this to allow using all cards throughout the game.",
                default=True,
            ),
        )

        for card_name, card_info in content.cards.items():
            self.item(
                card_name,
                count=card_info.count,
                useful=True,
                category=cards_category,
            )

        orange = self.item(
            "Orange",
            progression=True,
            count=50,
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
    words = re.findall(r"[A-Z]?[a-z]+", text)
    return "_".join(words).lower()


if __name__ == "__main__":
    load_dotenv()
    OrangeJuiceWorldBuilder().build()
