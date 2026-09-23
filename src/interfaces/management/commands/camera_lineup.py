"""
Django management command: camera_lineup

Rebuild a camera's custom slots from a lineup file kept in version control.
See lineups/README.md for the file format and the lineups in this repo.

Usage:
    python manage.py camera_lineup verify lineups/x-t30-ii/lineup-mist.json
    python manage.py camera_lineup push   lineups/x-t30-ii/lineup-mist.json
    python manage.py camera_lineup push   lineups/x-t30-ii/lineup.json --slots 2 4 5
    python manage.py camera_lineup import lineups/x-t30-ii/lineup.json

verify reads the slots and compares them (read-only apart from the slot cursor).
push writes the recipes, then verifies every slot by reading it back.
import only adds the recipes to the local database; the camera is not touched.

Camera setup: USB RAW CONV./BACKUP RESTORE mode, as for camera_info.
"""

import pathlib
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from src.application.usecases.camera import apply_lineup as apply_lineup_uc
from src.domain.camera import ptp_device

_DRP_HINT = (
    "The camera refused to change D-Range Priority on that slot, and while it is "
    "not Off it also ignores Dynamic Range, Highlight and Shadow. Fix it on the camera: "
    "IMAGE QUALITY SETTING > EDIT/SAVE CUSTOM SETTING > (a slot with D-Range Priority "
    "Off) > COPY > (the failing slot), then run push again for that slot."
)


class Command(BaseCommand):
    help = "Push, verify or import a camera lineup (one recipe per custom slot) from a JSON file."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("action", choices=["push", "verify", "import"])
        parser.add_argument("lineup", type=pathlib.Path, help="Path to a lineup JSON file.")
        parser.add_argument(
            "--slots",
            type=int,
            nargs="+",
            help="push only: write just these slot numbers (every slot is still verified).",
        )

    def handle(self, *args: object, **options: Any) -> None:
        lineup = apply_lineup_uc.load_lineup(options["lineup"])
        action = options["action"]

        if action == "import":
            for slot, recipe, created in apply_lineup_uc.import_lineup(lineup):
                status = "created" if created else "exists "
                self.stdout.write(f"  C{slot}: {status} {recipe.name!r} (id {recipe.id})")
            return

        try:
            if action == "push":
                checks = apply_lineup_uc.push_lineup(lineup, slots=options["slots"])
            else:
                checks = apply_lineup_uc.verify_lineup(lineup)
        except apply_lineup_uc.LineupCameraMismatchError as exc:
            raise CommandError(
                f"This lineup is for the {exc.expected}, but the camera is a {exc.found}."
            )
        except ptp_device.CameraConnectionError as exc:
            raise CommandError(f"Camera connection failed: {exc}")

        for check in checks:
            label = self.style.SUCCESS("OK      ") if check.ok else self.style.ERROR("MISMATCH")
            self.stdout.write(f"  C{check.slot}: {label} {check.name}")
            for field, (expected, found) in check.mismatches.items():
                self.stdout.write(f"      {field}: expected {expected!r}, camera has {found!r}")
            if check.write_warning and check.ok:
                self.stdout.write(f"      (camera reported {check.write_warning}; read-back is correct)")

        failed = [c for c in checks if not c.ok]
        if any("d_range_priority" in c.mismatches for c in failed):
            self.stdout.write(self.style.WARNING(_DRP_HINT))
        if failed:
            raise CommandError(f"{len(failed)} slot(s) do not match the lineup.")
        self.stdout.write(self.style.SUCCESS(f"All {len(checks)} slots match the lineup."))
