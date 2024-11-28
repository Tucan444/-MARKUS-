import pygame.transform
from pygame import Surface

from scripts.AssetClasses.UI.ui_element import UI_Element
from scripts.GameTypes import UISheetPosition, HitboxType, Percentage


class ProgressBar(UI_Element):
    def __init__(self, game: 'Game', ui_sheet: 'UI_Sheet', name: str,
                 position: UISheetPosition, layer: int, active: bool,
                 hitbox_type: HitboxType, empty: Surface, full: Surface,
                 horizontal: bool, flip_direction: bool,
                 progress: Percentage, progress_range: float=1):
        super().__init__(game, ui_sheet, empty.get_size(), name, position, layer, active,
                         hitbox_type=hitbox_type)

        self.empty: Surface = empty
        self.full: Surface = full
        self.horizontal: bool = horizontal
        self.flip_direction: bool = flip_direction
        self.progress: Percentage = progress
        self.progress_range: float = progress_range
        self.progress_range_inverse: float = 1 / progress_range

        self._progress_bar_processed: Surface = empty
        self.processed_bar_processed_up_to_date: bool = False

        assert(0 <= self.progress <= 1)
        assert(self.empty.get_size() == self.full.get_size())
        if self.hitbox_type == HitboxType.CIRCLE:
            assert(self.size[0] == self.size[1])

    @property
    def as_json(self) -> dict:
        json_form: dict = self.element_json

        image_names: dict[Surface, str] = self.game.assets.image_names

        json_form["type"] = "progress bar"
        json_form["empty"] = image_names[self.empty]
        json_form["full"] = image_names[self.full]
        json_form["horizontal"] = self.horizontal
        json_form["flip direction"] = self.flip_direction
        json_form["progress"] = self.progress
        json_form["progress range"] = self.progress_range

        return json_form

    @property
    def as_string(self) -> str:
        return (f"name: {self.name}, sheet name: {self.ui_sheet.name}, position: {self.position}, "
                f"progress: {self.progress}, horizontal: {self.horizontal}, flip direction: {self.flip_direction}, "
                f"active: {self.active}, layer: {self.layer}, hitbox type: {self.hitbox_type}")

    def __repr__(self):
        return self.as_string

    def __str__(self):
        return self.as_string

    @property
    def progress_bar_processed(self) -> Surface:
        if self.processed_bar_processed_up_to_date:
            return self._progress_bar_processed

        if self.horizontal:
            cutoff: int = int(self.progress * self.size[0])

            full: Surface = Surface((cutoff, self.size[1]))
            full.blit(self.full, (0, 0))

            empty: Surface = Surface((self.size[0] - cutoff, self.size[1]))
            empty.blit(self.empty, (-cutoff, 0))

            self._progress_bar_processed = Surface(self.size)
            self._progress_bar_processed.blit(full, (0, 0))
            self._progress_bar_processed.blit(empty, (cutoff, 0))

            if self.flip_direction:
                self._progress_bar_processed = pygame.transform.flip(
                    self._progress_bar_processed, True, False
                )
        else:
            cutoff: int = int(self.progress * self.size[1])

            full: Surface = Surface((self.size[0], cutoff))
            full.blit(self.full, (0, 0))

            empty: Surface = Surface((self.size[0], self.size[1] - cutoff))
            empty.blit(self.empty, (0, -cutoff))

            self._progress_bar_processed = Surface(self.size)
            self._progress_bar_processed.blit(full, (0, 0))
            self._progress_bar_processed.blit(empty, (0, cutoff))

            if not self.flip_direction:
                self._progress_bar_processed = pygame.transform.flip(
                    self._progress_bar_processed, False, True
                )

        self.processed_bar_processed_up_to_date = True
        return self._progress_bar_processed

    def _clip_progress(self) -> None:
        self.progress = min(1., max(0., self.progress))

    def add_progress(self, value: Percentage) -> None:
        past_progress: Percentage = self.progress

        self.progress += value
        self._clip_progress()

        if past_progress != self.progress:
            self.processed_bar_processed_up_to_date = False

    def add_progress_ranged(self, value: float) -> None:
        past_progress: Percentage = self.progress
        self.progress = (self.progress * self.progress_range) + value
        self.progress *= self.progress_range_inverse
        self._clip_progress()

        if past_progress != self.progress:
            self.processed_bar_processed_up_to_date = False

    def blit(self):
        self.game.window.display.blit(self.progress_bar_processed, self.display_position)
