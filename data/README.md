# Word lists and provenance

The current MVP ships with curated word lists for English and Hungarian. These are intentionally modest and deterministic, suitable for local development and tests.

The project keeps answer words and valid guesses separate. `daily_answers` are a smaller curated set used for the daily schedule, while `valid_guesses` are broader candidate words valid for gameplay.

This repository intentionally stores the lists directly rather than relying on an external download during tests or runtime.
