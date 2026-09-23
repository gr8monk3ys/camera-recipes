# Lineups

A lineup is one recipe per custom slot (C1–Cn), kept as a JSON file so a camera's
whole setup lives in version control rather than only in the local database.

| Camera | Guide |
|---|---|
| X-T30 II | [x-t30-ii/](x-t30-ii/README.md) |

## Commands

```bash
.venv/bin/python manage.py camera_lineup verify <file>                 # read every slot back and compare
.venv/bin/python manage.py camera_lineup push   <file> [--slots 2 4]   # write, then verify every slot
.venv/bin/python manage.py camera_lineup import <file>                 # add the recipes to the database only
```

`push` refuses to run if the connected camera is not the lineup's model. Both
`push` and `verify` exit non-zero when any slot differs from the file.

## Format

```json
{
  "camera": "X-T30 II",
  "note": "free text",
  "slots": {
    "C1": {
      "name": "REGGIES PORTRA",
      "description": "shown in the web app",
      "sensors": ["X-Trans IV"],
      "film_simulation": "Classic Chrome",
      "...": "every other FujifilmRecipeData field"
    }
  }
}
```

`camera` must match the model name the camera reports (`manage.py camera_info`).
Names follow the camera's slot rules: at most 25 ASCII characters. The field values
are the same strings the web app's Create Recipe form stores; the easiest way to
make a new lineup is to build the recipes in the app and copy an existing file.
