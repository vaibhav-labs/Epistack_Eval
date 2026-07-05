# Calibration as Linkage Integrity

Submission to the FLF Epistemic Case Study Competition ("Epistack").

**Start here:** the full writeup and run results are in [`FLF-Submission-Combined.pdf`](FLF-Submission-Combined.pdf). The runnable instrument is [`epistack_eval.py`](epistack_eval.py).

**The claim:** the real test of a knowledge base is not whether it looks rigorous but whether its rigor survives contact with a reasoner. A reasoner leaning only on the base should end up as confident as the evidence warrants, no more and no less. Any gap is a failure of the base, not the reader. This repo holds the instrument that measures that gap.

## What is here

- `epistack_eval.py` : the runnable instrument (dependency-light, one command).
- `FLF-Final-Submission.pdf` : the written argument.
- `results/` : run outputs across three cases and two models.

## Run it

```bash
pip install anthropic
export ANTHROPIC_API_KEY=sk-...
python3 epistack_eval.py --case covid       --model claude-sonnet-4-6
python3 epistack_eval.py --case blackholes  --model claude-opus-4-8
python3 epistack_eval.py --case eggs        --model claude-sonnet-4-6
```

No key? See the shape first with `python3 epistack_eval.py --dry-run` (prints placeholders, not results).

## What it measures

The instrument runs LLM personas through a knowledge base under a knowledge mask and reports two things.

**Part A, linkage integrity**, measures all three constraints it applies: reasoning from the base only, updating on a held-out claim it never saw, and holding up under a counter-argument. It also reports the objective metric, calibration gained per claim read, where calibration means closeness to the case's warranted width and range (not a target answer).

**Part B, double-counting** (COVID), measures behaviorally whether confidence moves further when correlated clues are shown as separate strikes than when flagged as one shared cause.

## Three cases, one instrument (the compounding claim, shown)

The same instrument runs on three differently-shaped cases; only the knowledge base and the warranted shape change.

- **covid** (contested): wide uncertainty warranted; failure = missing the reference-class crux, and double-counting.
- **blackholes** (settled): confident-safe warranted; failure = false balance.
- **eggs** (ill-posed): failure = a confident universal answer instead of catching heterogeneity.

## Headline results (LLM personas, suggestive not proof; models named)

- Black holes (settled) gave the clearest positive result: on Opus, calibration gained per claim read about 0.11, mean calibration increase about 0.57, most skeptical persona gaining most (0.75); none fell for false balance.
- The metric is model-dependent: slightly negative on COVID/Sonnet (about minus 0.01), slightly positive on COVID/Opus (about 0.005), clearly positive on black holes.
- Crux localization is model-dependent: patchy on Sonnet (COVID 0.67), reliable on Opus (1.0). Held-out transfer and confidence survival were 1.0 across models.
- Double-counting effect small: about 0.05 on Sonnet, about 0.02 (not firing) on Opus.

## Honest bounds

LLM personas, not humans. Scored against the structure of each case, not ground truth. The black-holes and eggs knowledge bases are compact, defensible starters meant to show the instrument travels, not authoritative verdicts. Effort is proxied by claims read. A human cohort, more runs, and larger bases are the next steps.

## Reuse

Cooperative competition, so reuse is welcome. Released under the MIT License (see `LICENSE`). Questions: hi@vj9.org
