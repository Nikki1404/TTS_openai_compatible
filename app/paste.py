I explored the Parakeet real-time ASR setup using NVIDIA NeMo Toolkit.
One blocker I’ve identified:

NeMo Toolkit (and its dependency pydantic-core) currently does not support Python 3.13.

This causes installation failures on both my local & the EC2 instance.

Python 3.10 / 3.11 is required to run Parakeet real-time ASR successfully.

This is a package compatibility limitation, not related to our application code.

Proposal:

Option A — We deploy the GPU ASR server on a machine that has Python 3.10 or 3.11 installed (recommended).
Option B — Switch to another ASR model that supports Python 3.13, with a trade-off in latency and real-time capabilities.

Please let me know which approach you would prefer so I can proceed accordingly.


  python -c "import torch; print(torch.cuda.is_available())"
