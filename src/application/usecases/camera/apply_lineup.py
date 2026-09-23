"""
Application-layer use cases for camera lineups.

A lineup is a JSON file that assigns one recipe to each custom slot (C1–Cn) of a
camera. It exists so a camera's whole setup lives in version control and can be
rebuilt on any machine, instead of only in the local database.

File format::

    {
      "camera": "X-T30 II",
      "note": "free text",
      "slots": {
        "C1": {"name": "...", "description": "...", "sensors": ["X-Trans IV"],
               "film_simulation": "...", ...every FujifilmRecipeData field...},
        ...
      }
    }

Verification is by read-back, never by the push's own error report: on the
X-T30 II the camera answers some writes with an error even though it applied
them, and accepts others that a slot's D-Range Priority then overrides. What
the slot reads back is the only reliable answer.
"""

from __future__ import annotations

import json
import pathlib
import time
from collections.abc import Iterable

import attrs

from src.application.usecases.camera import push_recipe as push_recipe_uc
from src.data import models
from src.domain.camera import device_config
from src.domain.camera import queries as camera_queries
from src.domain.images import dataclasses as image_dataclasses
from src.domain.recipes import normalization as recipe_normalization
from src.domain.recipes import operations as recipe_operations
from src.domain.settings import queries as settings_queries

# Fields that describe a recipe rather than configure the camera, so a slot
# cannot store them and read-back cannot compare them.
_NOT_ON_CAMERA = frozenset({"sensors", "description"})


@attrs.frozen
class Lineup:
    camera: str
    slots: dict[int, image_dataclasses.FujifilmRecipeData]


@attrs.frozen
class SlotCheck:
    """
    The result of reading one slot back and comparing it to the lineup.

    ``mismatches`` maps a field name to ``(expected, found)``. ``write_warning``
    carries the push's own error report, kept for information only.
    """

    slot: int
    name: str
    mismatches: dict[str, tuple[object, object]]
    write_warning: str = ""

    @property
    def ok(self) -> bool:
        return not self.mismatches


@attrs.frozen
class LineupCameraMismatchError(Exception):
    """
    Raised when the connected camera is not the model the lineup was made for.
    """

    expected: str
    found: str


def load_lineup(path: pathlib.Path) -> Lineup:
    """
    Parse a lineup file.

    :raises ValueError: If a slot key is not of the form ``C<n>`` or a recipe
        name breaks the camera's naming rules.
    """
    raw = json.loads(path.read_text())
    slots: dict[int, image_dataclasses.FujifilmRecipeData] = {}
    for key, fields in raw["slots"].items():
        if not (key.startswith("C") and key[1:].isdigit()):
            raise ValueError(f"Slot keys must look like 'C1', got {key!r}")
        slots[int(key[1:])] = image_dataclasses.FujifilmRecipeData(
            **{**fields, "sensors": tuple(fields.get("sensors", ()))}
        )
    return Lineup(camera=raw["camera"], slots=dict(sorted(slots.items())))


def import_lineup(lineup: Lineup) -> list[tuple[int, models.FujifilmRecipe, bool]]:
    """
    Make sure every recipe in the lineup exists in the database.

    Returns ``(slot, recipe, created)`` per slot. A recipe whose settings
    already exist is reused as it is, keeping its current name and description.
    """
    results = []
    for slot, data in lineup.slots.items():
        recipe, created = recipe_operations.get_or_create_recipe_from_data(data=data)
        results.append((slot, recipe, created))
    return results


def push_lineup(lineup: Lineup, *, slots: Iterable[int] | None = None) -> list[SlotCheck]:
    """
    Write the lineup's recipes to the camera, then read every slot back.

    Only *slots* are written (all of them by default); every slot in the lineup
    is verified, so the result always describes the whole camera.

    :raises LineupCameraMismatchError: Before anything is written, if the
        connected camera is not the lineup's model.
    """
    _check_camera(lineup)
    selected = set(lineup.slots if slots is None else slots)
    unknown = selected - set(lineup.slots)
    if unknown:
        raise ValueError(f"The lineup has no slot(s) {sorted(unknown)}")

    warnings: dict[int, str] = {}
    for slot, recipe, _ in import_lineup(lineup):
        if slot not in selected:
            continue
        try:
            push_recipe_uc.push_recipe_to_camera(recipe, slot_index=slot)
        except push_recipe_uc.RecipeWriteError as exc:
            warnings[slot] = str(exc)
    return verify_lineup(lineup, write_warnings=warnings)


def verify_lineup(
    lineup: Lineup,
    *,
    write_warnings: dict[int, str] | None = None,
) -> list[SlotCheck]:
    """
    Read every slot in the lineup back from the camera and compare it.

    Read-only apart from moving the slot cursor.
    """
    write_warnings = write_warnings or {}
    device = device_config.get_device()
    device.connect()
    try:
        checks = []
        for position, (slot, expected) in enumerate(lineup.slots.items()):
            if position:
                time.sleep(settings_queries.get_camera_inter_slot_delay_s())
            found = camera_queries.slot_recipe(device, slot)
            checks.append(
                SlotCheck(
                    slot=slot,
                    name=found.name,
                    mismatches=_compare(expected, found),
                    write_warning=write_warnings.get(slot, ""),
                )
            )
        return checks
    finally:
        device.disconnect()


def _check_camera(lineup: Lineup) -> None:
    device = device_config.get_device()
    device.connect()
    try:
        found = device.camera_name
    finally:
        device.disconnect()
    if found != lineup.camera:
        raise LineupCameraMismatchError(expected=lineup.camera, found=found)


def _compare(
    expected: image_dataclasses.FujifilmRecipeData,
    found: image_dataclasses.FujifilmRecipeData,
) -> dict[str, tuple[object, object]]:
    want = attrs.asdict(recipe_normalization.normalize_recipe_data(expected))
    got = attrs.asdict(found)
    return {
        field: (want[field], got[field])
        for field in want
        if field not in _NOT_ON_CAMERA and str(want[field]) != str(got[field])
    }
