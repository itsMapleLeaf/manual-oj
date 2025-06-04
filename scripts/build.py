from dataclasses import dataclass
import re
from dataclasses_json import DataClassJsonMixin
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from .builder.location import some_of
from .builder import WorldBuilder, Category, Item


@dataclass
class GameCampaign(DataClassJsonMixin):
    episodes: int
    dlc: Optional[str] = None


@dataclass
class GameExtra(DataClassJsonMixin):
    dlc: Optional[str] = None


@dataclass
class GameCard:
    count: int


@dataclass
class GameContent(DataClassJsonMixin):
    campaigns: dict[str, GameCampaign]
    extra_episodes: dict[str, GameExtra]
    characters: list[str]
    cards: dict[str, GameCard]
    goals: dict[str, str]


class OrangeJuiceWorldBuilder:
    builder = WorldBuilder()
    dlc_categories: dict[str, Category] = {}

    def resolve_dlc_category(self, name: str):
        if name in self.dlc_categories:
            return self.dlc_categories[name]

        dlc_option = self.builder.toggle_option(
            f"enable_{to_snake_case(name)}_dlc",
            description=f"Enables the {name} DLC.",
            default=True,
        )
        dlc_category = self.builder.category(
            f"{name} DLC",
            hidden=True,
            yaml_option=[dlc_option.name],
        )
        self.dlc_categories[name] = dlc_category
        return dlc_category

    def build(self):
        content = GameContent.from_json(
            Path("src/data/content.json").read_text(encoding="utf-8")
        )

        completed_campaigns_category = self.builder.category(
            "Completed Campaigns", hidden=True
        )

        for campaign_name, campaign_info in content.campaigns.items():
            dlc_categories = (
                [self.resolve_dlc_category(campaign_info.dlc)]
                if campaign_info.dlc
                else []
            )

            campaign_unlock_item = self.builder.item(
                (
                    f"{campaign_name} (Campaign)"
                    if campaign_name in content.characters
                    else campaign_name
                ),
                progression=True,
                category=["Campaigns", *dlc_categories],
            )

            for episode_index in range(campaign_info.episodes):
                self.builder.location(
                    f"{campaign_name} (Episode {episode_index + 1})",
                    requires=campaign_unlock_item,
                    category=[f"(Campaign) {campaign_name}", *dlc_categories],
                )

            self.builder.location(
                f"{campaign_name} (Final Episode)",
                requires=campaign_unlock_item,
                category=[f"(Campaign) {campaign_name}", *dlc_categories],
            )

            campaign_completion_item = self.builder.item(
                f"{campaign_name} (All Episodes)",
                progression=True,
                category=[completed_campaigns_category, *dlc_categories],
            )

            self.builder.location(
                campaign_completion_item.name,
                place_item=[campaign_completion_item.name],
                requires=campaign_unlock_item,
                category=[f"(Campaign Completion) {campaign_name}", *dlc_categories],
            )

        for episode_name, episode_info in content.extra_episodes.items():
            dlc_categories = (
                [self.resolve_dlc_category(episode_info.dlc)]
                if episode_info.dlc
                else []
            )

            episode_unlock_item = self.builder.item(
                f"{episode_name} (Extra)",
                progression=True,
                category=["Campaigns", *dlc_categories],
            )

            episode_completion_item = self.builder.item(
                f"{episode_name} (Complete)",
                progression=True,
                category=[completed_campaigns_category, *dlc_categories],
            )

            # one location for finding a randomized item, and another for the actual progression
            self.builder.location(
                episode_name,
                requires=episode_unlock_item,
                category=["(Extras)", *dlc_categories],
            )
            self.builder.location(
                f"{episode_name} (Completion)",
                place_item=[episode_completion_item.name],
                requires=episode_unlock_item,
                category=["(Extras Completion)", *dlc_categories],
            )

        character_items: dict[str, Item] = {}
        for character in content.characters:
            character_items[character] = self.builder.item(
                character,
                useful=True,
                category=["Characters"],
            )

        for card_name, card_info in content.cards.items():
            self.builder.item(
                card_name,
                count=card_info.count,
                useful=True,
                category=["Cards"],
            )

        for character_name, goal in content.goals.items():
            goal_character = character_items.get(character_name)
            if not goal_character:
                print(
                    f'Warning: failed to find character "{character_name}" for goal "{goal}"'
                )

            self.builder.location(
                f"{character_name}: {goal}",
                category=["(Goals)"],
                requires=goal_character,
            )

        self.builder.location(
            "69,420,000,000 Oranges",
            victory=True,
            requires=some_of(completed_campaigns_category, "80%"),
            category=["((Victory))"],
        )

        self.builder.generate_data().build_world()


def to_snake_case(text: str):
    words = re.findall(r"[A-Z]?[a-z]+", text)
    return "_".join(words).lower()


if __name__ == "__main__":
    load_dotenv()
    OrangeJuiceWorldBuilder().build()
