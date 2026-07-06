# NOTE: this repo lives under ~/Documents, where macOS keeps re-applying the
# UF_HIDDEN flag to files inside .venv; Python 3.13+ skips hidden .pth files,
# which silently breaks the editable install. We therefore run everything with
# PYTHONPATH=src instead of relying on the .pth-based editable hook.
RUN := PYTHONPATH=src uv run --no-sync python -m

.PHONY: setup ingest panel base-rates shortlist test all

setup:
	uv sync --extra dev

ingest:
	$(RUN) wizarb.cli ingest --from-year 2019 --to-year 2025

panel:
	$(RUN) wizarb.cli build-panel

base-rates:
	$(RUN) wizarb.cli base-rates

shortlist:
	$(RUN) wizarb.cli shortlist

test:
	PYTHONPATH=src uv run --no-sync python -m pytest -q

all: setup ingest panel base-rates shortlist
