# Architecture

Hospital Admin → departments and staff credentials → department authentication → current doctor identity → patient queue.

Patient → multilingual intake → adaptive questions → previous documents → structured summary → red-flag screening → routing → token → doctor review.

Department routing in the demo uses deterministic rules so the prototype remains runnable without a model download. Production can replace the router with a validated classifier/LLM while retaining rules for safety-critical red flags.
