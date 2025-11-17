I checked whether we can move from Python 3.10 to Python 3.11 or 3.12.
After reviewing NVIDIA and NeMo documentation, here is the conclusion:
Specifically:

nvidia-riva-client has no Python 3.11-compatible version.
NVIDIA Riva SDK officially supports only Python 3.8–3.10
(reference: NVIDIA Riva user guide).

nemo-text-processing cannot install on Python 3.11
because its dependencies (Pynini, OpenFST) have no wheels for Python 3.11.

pyannote.audio 3.x does not work on Python 3.11
due to dependencies like numba/llvmlite and pydantic v1, which break beyond Python 3.10.
