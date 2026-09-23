"""
Integration tests for the camera lineup use cases.

The lineup files under lineups/ are the real, committed data, so the first
group of tests guards them against drifting into something the camera or the
database would reject.
"""
import json
import pathlib

import pytest

from src.application.usecases.camera import apply_lineup
from src.data.camera import constants
from src.domain.recipes import normalization, validation
from tests.fakes import FakePTPDevice

LINEUPS = sorted((pathlib.Path(__file__).resolve().parents[4] / "lineups").rglob("*.json"))


class SlottedFakePTPDevice(FakePTPDevice):
    """
    FakePTPDevice with one property store per custom slot, selected by the
    slot cursor, so a push to C2 does not overwrite what was pushed to C1.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._slot_stores: dict[int, tuple[dict, dict]] = {}

    def _select(self, slot: int) -> None:
        self._int_store, self._str_store = self._slot_stores.setdefault(slot, ({}, {}))

    def set_property_uint16(self, code, value):
        if code == constants.PROP_SLOT_CURSOR:
            self._select(value)
            return 0
        return super().set_property_uint16(code, value)

    def set_property_int(self, code, value):
        if code == constants.PROP_SLOT_CURSOR:
            self._select(value)
            return 0
        return super().set_property_int(code, value)


@pytest.fixture
def camera(settings):
    device = SlottedFakePTPDevice(camera_name="X-T30 II")
    settings.PTP_DEVICE = lambda: device
    return device


@pytest.fixture
def lineup_file(tmp_path):
    source = next(p for p in LINEUPS if p.name == "lineup-mist.json")
    path = tmp_path / "lineup.json"
    path.write_text(source.read_text())
    return path


class TestCommittedLineups:
    def test_lineup_files_exist(self):
        assert {p.name for p in LINEUPS} >= {
            "lineup.json",
            "lineup-mist.json",
            "previous-slots-2026-09-22.json",
        }

    @pytest.mark.parametrize("path", LINEUPS, ids=lambda p: p.name)
    def test_every_recipe_is_valid(self, path):
        lineup = apply_lineup.load_lineup(path)
        assert list(lineup.slots) == list(range(1, 8))
        for data in lineup.slots.values():
            validation.validate_recipe_data(normalization.normalize_recipe_data(data))


class TestLoadLineup:
    def test_rejects_badly_named_slot(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text(json.dumps({"camera": "X-T30 II", "slots": {"slot1": {}}}))
        with pytest.raises(ValueError):
            apply_lineup.load_lineup(path)


@pytest.mark.django_db
class TestPushLineup:
    def test_push_then_read_back_matches_every_slot(self, camera, lineup_file):
        lineup = apply_lineup.load_lineup(lineup_file)

        checks = apply_lineup.push_lineup(lineup)

        assert [c.slot for c in checks] == list(range(1, 8))
        assert all(c.ok for c in checks), [c.mismatches for c in checks if not c.ok]
        assert checks[6].name == "KODAK TRI-X 400"

    def test_refuses_a_different_camera_before_writing(self, settings, lineup_file):
        device = SlottedFakePTPDevice(camera_name="X-S10")
        settings.PTP_DEVICE = lambda: device
        lineup = apply_lineup.load_lineup(lineup_file)

        with pytest.raises(apply_lineup.LineupCameraMismatchError):
            apply_lineup.push_lineup(lineup)

        assert device._slot_stores == {}

    def test_rejected_write_is_a_warning_when_read_back_is_correct(self, settings, lineup_file):
        # The X-T30 II answers the D-Range Priority write with 0x201C even when
        # the slot already holds the value; read-back decides, not the error.
        device = SlottedFakePTPDevice(
            camera_name="X-T30 II",
            set_rejection_codes={constants.CUSTOM_SLOT_CODES["DRangePriority"]: 0x201C},
        )
        settings.PTP_DEVICE = lambda: device
        lineup = apply_lineup.load_lineup(lineup_file)

        checks = apply_lineup.push_lineup(lineup, slots=[1])

        assert checks[0].ok
        assert "DRangePriority" in checks[0].write_warning

    def test_unknown_slot_is_rejected(self, camera, lineup_file):
        lineup = apply_lineup.load_lineup(lineup_file)
        with pytest.raises(ValueError):
            apply_lineup.push_lineup(lineup, slots=[9])


@pytest.mark.django_db
class TestVerifyLineup:
    def test_reports_a_slot_that_changed_on_the_camera(self, camera, lineup_file):
        lineup = apply_lineup.load_lineup(lineup_file)
        apply_lineup.push_lineup(lineup)
        camera._slot_stores[3][0][constants.CUSTOM_SLOT_CODES["FilmSimulation"]] = (
            constants.FILM_SIMULATION_TO_PTP["Provia"]
        )

        checks = apply_lineup.verify_lineup(lineup)

        bad = [c for c in checks if not c.ok]
        assert [c.slot for c in bad] == [3]
        assert bad[0].mismatches["film_simulation"] == ("Classic Chrome", "Provia")


@pytest.mark.django_db
class TestImportLineup:
    def test_import_is_idempotent(self, lineup_file):
        lineup = apply_lineup.load_lineup(lineup_file)

        first = apply_lineup.import_lineup(lineup)
        second = apply_lineup.import_lineup(lineup)

        assert all(created for _, _, created in first)
        assert not any(created for _, _, created in second)
        assert [r.id for _, r, _ in first] == [r.id for _, r, _ in second]
