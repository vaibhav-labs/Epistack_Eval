# Calibration as Linkage Integrity

Submission to the FLF Epistemic Case Study Competition ("Epistack").

**Start here:** the full writeup and run results are in [`FLF-Submission-Combined.pdf`](FLF-Submission-Combined.pdf). The runnable instrument is [`epistack_eval.py`](epistack_eval.py).

## The core submission

The real test of the rigor of a knowledge base is how well it survives contact with a reasoner. Ideally the reasoner leaning only on the base should be as confident as the evidence in the base warrants. Any more or less confidence is a failure of the base and not a failure of the reader. This instrument measures that deviation, on real contested cases.

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

The evaluation runs as one script with two parts: a linkage-integrity test and a behavioral double-counting test. They measure different failures.

The linkage test measures all three constraints it applies: reasoning from the base only, updating on a held-out claim it never saw, and holding up under a counter-argument. The first is enforced by instruction; the next two are measured directly. It also reports the objective metric, calibration gained per claim read.

## Three cases, one instrument

The same instrument runs on three differently-shaped cases; only the knowledge base and the warranted shape change.

- **covid** (contested): wide uncertainty is warranted.
- **blackholes** (settled): confident-safe is warranted, and the failure to catch is false balance.
- **eggs** (ill-posed): the failure is a confident universal answer instead of catching that the effect depends on who you are.

## What the results say

Following are the results from running the instrument on the three cases using two models (Sonnet and Opus). It was done using LLM personas, so the results are pointing and not proving.

| Case | Shape | Model | Found the crux | Held-out transfer | Confidence survived | Metric (calibration / claim read) |
|---|---|---|---|---|---|---|
| COVID | contested | Sonnet | 0.67 | 1.0 | 1.0 | about -0.01 |
| COVID | contested | Opus | 1.0 | 1.0 | 1.0 | about +0.005 |
| Black holes | settled | Sonnet | 1.0 | 0.0 (see note) | 1.0 | about +0.09 |
| Black holes | settled | Opus | 1.0 | 0.0 (see note) | 1.0 | about +0.11 |
| Eggs | ill-posed | Sonnet | 0.0 | 1.0 | 1.0 | about +0.009 |
| Eggs | ill-posed | Opus | 1.0 | 1.0 | 1.0 | about +0.004 |

Note on the black-holes held-out score: the held-out claim reinforced an answer that was already at zero, so there was no room left to move, and the instrument recorded no update as no transfer. It is a scoring edge, not a reasoning failure.

For the settled case of black holes, it gave the clearest positive result (rightfully so). On Opus the mean calibration increase was 0.57, and the most skeptical persona gained the most (0.75). None of the personas fell for false balance when the counter-argument pushed them to doubt a settled answer.

The metric pointed to being model-dependent. It came out cleaner and more positive on the stronger model, and weaker and slightly negative on the lighter one. Which again proved the point that a better reasoner pulls more warranted calibration out of the same base.

Even the crux localization is model-dependent. It was more reliable on Opus and patchy on Sonnet, and it kept moving between different runs.

For the eggs case, it showed its characteristic failure. On the Sonnet model the reasoners missed that the effect is heterogeneous across people, while on Opus they caught it.

The honest bounds are in `FLF-Submission-Combined.pdf`.

## Limitations

1. It used LLM personas and not a human cohort, though it had multiple runs.
2. It scored against the structure of each case.
3. The effort metric is proxied by the claims it read.
4. The black-holes and eggs knowledge bases are compact, defensible starters, which are meant to show the instrument travels, and not necessarily authoritative verdicts.

## Reuse

Cooperative competition, so reuse is welcome. Released under the MIT License (see `LICENSE`). Questions: hi@vj9.org
