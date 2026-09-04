# Clean-room reproducibility

## Goal
Prove the local MVP does not depend on hidden workspace state.

## Reproduction commands
From the repository root with Python 3.11+:

```bash
python -m pip install pytest
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m ripple.evaluation.matrix
PYTHONPATH=src python -m ripple.evaluation.release_gate
PYTHONPATH=src python -m ripple.webapp
```

Then open `http://127.0.0.1:8765`.

## CI
`.github/workflows/quality-gate.yml` runs the tests, regenerates executable evidence, and fails if the committed evidence reports drift from runtime behavior.
