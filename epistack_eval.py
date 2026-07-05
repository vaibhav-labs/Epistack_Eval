#!/usr/bin/env python3
"""
epistack_eval.py  -  combined epistack evaluation (v5, three cases)

Confirm the version by the header it prints: "EPISTACK EVALUATION (combined, v5 ...)".

WHAT IT DOES
------------
Tests whether a knowledge base's rigor survives contact with a reasoner, and
demonstrates that the SAME instrument travels across three differently-shaped
cases (this is the compounding claim, shown rather than asserted):

  covid       contested   -> warranted shape is WIDE; failure = miss the
                             reference-class crux, and double-count correlated clues.
  blackholes  settled     -> warranted shape is CONFIDENT-SAFE (near 0, narrow);
                             failure = false balance (staying uncertain when the
                             evidence licenses confidence).
  eggs        ill-posed   -> the question is under-specified; failure = a confident
                             universal answer instead of catching heterogeneity.

Part A (all cases) measures three constraints and the objective metric:
  - base-only reasoning (applied via a knowledge mask),
  - a held-out claim it never saw (measured: correct direction, sensible size,
    grounded reasoning),
  - a counter-argument (measured: does the warranted stance survive),
  - OBJECTIVE METRIC: calibration increase per claim read (calibration = closeness
    to the case's warranted width/range).
Part B (covid only) is the behavioral double-counting probe.

HONEST BOUNDS: LLM personas, not humans (suggestive, not proof); scored against
the STRUCTURE of each case, not ground truth; effort proxied by claims_read. The
black-holes and eggs knowledge bases are compact, defensible starters built from
the public understanding of each case, meant to show the instrument travels, NOT
to be authoritative verdicts. Always name the model.

RUN
  python3 epistack_eval.py --dry-run
  python3 epistack_eval.py --case covid       --model claude-sonnet-4-6
  python3 epistack_eval.py --case blackholes  --model claude-opus-4-8
  python3 epistack_eval.py --case eggs        --model claude-sonnet-4-6
"""

from __future__ import annotations
from dataclasses import dataclass, field
import argparse, json, sys, statistics

VERSION = "combined, v5 (3 cases)"


def call(system, messages, model, temperature, dry, dry_text=""):
    if dry:
        return dry_text
    try:
        import anthropic
    except ImportError:
        sys.exit("Install the SDK first:  pip install anthropic")
    kw = dict(model=model, max_tokens=1024, system=system, messages=messages)
    if temperature is not None and "opus-4-8" not in model and "fable" not in model:
        kw["temperature"] = temperature
    msg = anthropic.Anthropic().messages.create(**kw)
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


def parse(text):
    try:
        return json.loads(text[text.find("{"): text.rfind("}") + 1])
    except Exception:
        return {}


@dataclass
class Claim:
    id: str
    text: str
    favors: str
    stated_confidence: float
    citations: list = field(default_factory=list)
    correlated_with: list = field(default_factory=list)
    load_bearing: bool = False


# ===================== THE THREE CASES =======================================
CASES = {
 "covid": {
   "shape": "contested",
   "top_q": "What is the probability that SARS-CoV-2 had a natural (zoonotic) origin?",
   "kb": [
     Claim("market_cluster", "The earliest known cases cluster around the Huanan seafood market.",
           "zoonosis", 0.80, ["Worobey et al. 2022"], ["animals_sold"], True),
     Claim("animals_sold", "Susceptible live animals were sold at that market and environmental "
           "samples near the animal stalls tested positive.", "zoonosis", 0.75, ["Pekar et al. 2022"],
           ["market_cluster"]),
     Claim("wiv_in_wuhan", "The Wuhan Institute of Virology, which researches bat coronaviruses, is "
           "located in Wuhan.", "lab_leak", 0.85, ["public record"], ["outbreak_near_wiv"], True),
     Claim("outbreak_near_wiv", "The outbreak began in the same city as that institute.",
           "lab_leak", 0.85, ["public record"], ["wiv_in_wuhan"]),
     Claim("furin_site", "SARS-CoV-2 has an unusual furin cleavage site.", "lab_leak", 0.70,
           ["Andersen et al. 2020"]),
     Claim("reference_class", "Base rate: across novel epidemics in general, how often does the "
           "origin turn out to be a laboratory versus nature?", "meta", 0.50,
           ["Kahneman & Lovallo 1993 (outside view)"], load_bearing=True),
   ],
   "warranted_range": (0.20, 0.90),
   "crux": "reference_class",
   "held_out": {"text": "Two distinct viral lineages (A and B) were present at the market early on, "
                        "which some read as evidence of more than one spillover.",
                "good_direction": "up",
                "keywords": ["lineage", "spillover", "multiple", "introduction", "distinct", "two ", "a and b"]},
   "adversarial": "But the lab is right there in the same city, doing exactly this kind of research. "
                  "Isn't that on its own decisive for a lab origin?",
   "notes": ("Contested. Public record (Rootclaim; Alexander 2024): six analysts spanned 23 orders of "
             "magnitude, neutral analysts ~50x, driven by the reference-class choice, not the facts. "
             "Superforecasters ~75/25 zoonosis; public ~66% lab leak. Warranted shape is WIDE."),
   "double_count": True,
 },

 "blackholes": {
   "shape": "settled",
   "top_q": "What is the probability that the LHC produces a micro black hole that destroys Earth?",
   "kb": [
     Claim("hawking_radiation", "Any micro black hole produced would evaporate almost immediately via "
           "Hawking radiation.", "safe", 0.80, ["Hawking 1975"], load_bearing=True),
     Claim("cosmic_ray_bound", "Cosmic rays of far higher energy have struck Earth, the Sun and other "
           "bodies for billions of years without producing catastrophic black holes, and those bodies "
           "still exist.", "safe", 0.90, ["Giddings & Mangano 2008; LSAG 2008"],
           ["lhc_below_cosmic"], True),
     Claim("lhc_below_cosmic", "LHC collision energies are below those of high-energy cosmic-ray "
           "collisions that occur naturally.", "safe", 0.85, ["LSAG 2008"], ["cosmic_ray_bound"]),
     Claim("stable_hypothetical", "If Hawking radiation did not exist, a stable micro black hole is "
           "conceivable in principle.", "risk", 0.40, ["theoretical"]),
     Claim("production_uncertain", "It is not certain the LHC can produce micro black holes at all.",
           "safe", 0.70, ["LSAG 2008"]),
   ],
   "warranted_range": (0.00, 0.05),
   "crux": "cosmic_ray_bound",
   "held_out": {"text": "White dwarf stars and neutron stars, which are extremely dense, have also "
                        "survived cosmic-ray bombardment over cosmic timescales.",
                "good_direction": "down",
                "keywords": ["white dwarf", "neutron", "dense", "survived", "cosmic", "star"]},
   "adversarial": "But we have never run this exact experiment before, so how can anyone be sure it is "
                  "safe rather than just assuming it?",
   "notes": ("Settled (Giddings & Mangano 2008; LSAG 2008): evaporation via Hawking radiation, plus the "
             "cosmic-ray natural experiment, licenses confidence that it is safe. Warranted shape is "
             "CONFIDENT-SAFE (near 0, narrow). Failure mode = false balance."),
   "double_count": False,
 },

 "eggs": {
   "shape": "ill-posed",
   "top_q": ("For a typical adult, what is the probability that moderate egg consumption meaningfully "
             "increases cardiovascular risk?"),
   "kb": [
     Claim("responder_variation", "Egg consumption raises LDL cholesterol substantially in a minority of "
           "'hyper-responders' but little in most people.", "depends", 0.80,
           ["nutrition reviews"], ["substitution"], True),
     Claim("marker_vs_outcome", "LDL is a risk marker, but dietary cholesterol's effect on actual "
           "cardiovascular events is smaller and debated.", "depends", 0.75, ["cohort reviews"],
           load_bearing=True),
     Claim("outcomes_mixed", "Large cohort studies show mixed, generally small associations between egg "
           "intake and cardiovascular events in the general population.", "not_bad", 0.70, ["cohort studies"]),
     Claim("substitution", "Health effects depend on what eggs replace or accompany (e.g. refined carbs "
           "vs processed meat).", "depends", 0.70, ["dietary trials"], ["responder_variation"]),
     Claim("dose", "Effects at one egg per day differ from very high intakes.", "depends", 0.65, ["reviews"]),
   ],
   "warranted_range": (0.25, 0.60),
   "crux": "responder_variation",
   "held_out": {"text": "In randomized trials where eggs replace refined-carbohydrate breakfasts, effects "
                        "on risk markers are often neutral or favorable.",
                "good_direction": "down",
                "keywords": ["replace", "refined", "carb", "substitution", "neutral", "favorable", "trial"]},
   "adversarial": "But eggs are high in cholesterol, so surely the simple answer is that they raise your "
                  "risk. Why overcomplicate it?",
   "notes": ("Ill-posed: 'are eggs bad?' is under-specified. Depends on hyper-responders vs general "
             "population, LDL marker vs cardiovascular outcomes, dose, and dietary substitution. For a "
             "typical adult the warranted view is a small, genuinely uncertain effect. Failure mode = a "
             "confident universal answer instead of catching heterogeneity."),
   "double_count": False,
 },
}

MASK = ("You are reasoning about a contested empirical question. Reason ONLY from what you are given in "
        "this conversation. Do not rely on anything you already know about this topic. Be honest about "
        "uncertainty; when evidence is weak or correlated, say so. Answer every turn in strict JSON only.")

PERSONAS = [("skeptic_low", 0.30), ("neutral", 0.50), ("skeptic_high", 0.70)]


def kb_text(cfg):
    out = [f"TOP QUESTION: {cfg['top_q']}", "", "CLAIMS:"]
    for c in cfg["kb"]:
        flag = f"  [shares a common cause with: {', '.join(c.correlated_with)}]" if c.correlated_with else ""
        out.append(f"- id={c.id} ({c.favors}, KB-confidence {c.stated_confidence:.2f}) {c.text} "
                   f"[cite: {', '.join(c.citations)}]{flag}")
    return "\n".join(out)


def cal_distance(point, low, high, wrange):
    hw = (high - low) / 2.0
    w_hw = (wrange[1] - wrange[0]) / 2.0
    return round(abs(hw - w_hw) + max(0.0, wrange[0] - point) + max(0.0, point - wrange[1]), 3)


def run_linkage(name, prior, cfg, model, dry):
    wrange = cfg["warranted_range"]
    before_user = (f"Your starting belief is P = {prior:.2f}. Question: {cfg['top_q']}\n"
                   "You have NOT been shown any evidence base yet. Give your current view. "
                   'Return JSON: {"posterior_point":0..1,"posterior_low":0..1,"posterior_high":0..1}.')
    before = parse(call(MASK, [{"role": "user", "content": before_user}], model, None, dry,
                        '{"posterior_point":%.2f,"posterior_low":%.2f,"posterior_high":%.2f}'
                        % (prior, max(0, prior - 0.1), min(1, prior + 0.1))))

    read_user = (f"Your starting belief is P = {prior:.2f}.\n\n{kb_text(cfg)}\n\n"
                 "Reason from the knowledge base. Return JSON: posterior_point (0..1), posterior_low, "
                 "posterior_high, identified_load_bearing (list of claim ids the answer most hinges on), "
                 "claims_used (list of claim ids you actually relied on).")
    read_txt = call(MASK, [{"role": "user", "content": read_user}], model, None, dry,
                    '{"posterior_point":%.2f,"posterior_low":%.2f,"posterior_high":%.2f,'
                    '"identified_load_bearing":["%s"],"claims_used":["%s"]}'
                    % ((wrange[0] + wrange[1]) / 2, wrange[0], wrange[1], cfg["crux"], cfg["crux"]))
    read = parse(read_txt)
    read_point = read.get("posterior_point", 0.5)
    hist = [{"role": "user", "content": read_user}, {"role": "assistant", "content": read_txt or "{}"}]

    ho = cfg["held_out"]
    ho_user = (f"Here is a claim that was NOT in the knowledge base: {ho['text']}\n"
               "Update your probability. Return JSON: {\"posterior_point\":0..1, \"why\": one short "
               "sentence naming what in this claim drove your update}.")
    ho_txt = call(MASK, hist + [{"role": "user", "content": ho_user}], model, None, dry,
                  '{"posterior_point":%.2f,"why":"%s"}'
                  % (read_point + (0.07 if ho["good_direction"] == "up" else -0.07), ho["keywords"][0]))
    ho_r = parse(ho_txt)
    hist += [{"role": "user", "content": ho_user}, {"role": "assistant", "content": ho_txt or "{}"}]

    adv_user = (f"A critic argues: {cfg['adversarial']}\nReconsider. Return JSON: "
                '{"posterior_point":0..1, "held": true if your view is basically unchanged}.')
    adv = parse(call(MASK, hist + [{"role": "user", "content": adv_user}], model, None, dry,
                     '{"posterior_point":%.2f,"held":true}' % read_point))

    # held-out scoring (direction depends on the case)
    ho_post = ho_r.get("posterior_point")
    delta = round(ho_post - read_point, 3) if isinstance(ho_post, (int, float)) else None
    why = str(ho_r.get("why", "")).lower()
    grounded = any(k in why for k in ho["keywords"])
    if delta is None:
        direction = None
    elif ho["good_direction"] == "up":
        direction = "correct" if delta > 0.01 else ("wrong" if delta < -0.01 else "none")
    else:
        direction = "correct" if delta < -0.01 else ("wrong" if delta > 0.01 else "none")
    held_out_ok = direction == "correct" and grounded and delta is not None and abs(delta) <= 0.25

    dist_before = cal_distance(before.get("posterior_point", prior), before.get("posterior_low", 0),
                               before.get("posterior_high", 1), wrange)
    dist_after = cal_distance(read_point, read.get("posterior_low", 0), read.get("posterior_high", 1), wrange)
    calibration_increase = round(dist_before - dist_after, 3)
    claims_read = max(1, len(read.get("claims_used", [])))

    lo, hi = read.get("posterior_low", 0), read.get("posterior_high", 1)
    return {"persona": name, "posterior_range": [lo, hi], "width": round(hi - lo, 3),
            "located_crux": cfg["crux"] in read.get("identified_load_bearing", []),
            "held_out_delta": delta, "held_out_direction": direction,
            "held_out_reasoning_grounded": grounded, "held_out_ok": held_out_ok,
            "warranted_stance_held": bool(adv.get("held", False)),
            "calibration_distance_before": dist_before, "calibration_distance_after": dist_after,
            "calibration_increase": calibration_increase, "claims_read": claims_read,
            "calibration_increase_per_claim": round(calibration_increase / claims_read, 4)}


def score_linkage(rows, cfg):
    n = max(1, len(rows))
    loc = sum(r["located_crux"] for r in rows)
    held = sum(r["warranted_stance_held"] for r in rows)
    ho_ok = sum(bool(r["held_out_ok"]) for r in rows)
    failures = []
    if loc < n:
        failures.append(f"{n-loc}/{n} personas did not identify the load-bearing crux "
                        f"('{cfg['crux']}') that governs this case.")
    if ho_ok < n:
        failures.append(f"{n-ho_ok}/{n} personas did not fully transfer reasoning to the held-out claim.")
    return {"case": None, "shape": cfg["shape"], "per_persona": rows,
            "crux_localization_rate": round(loc / n, 2),
            "held_out_transfer_rate": round(ho_ok / n, 2),
            "warranted_stance_survival_rate": round(held / n, 2),
            "mean_posterior_width": round(statistics.mean(r["width"] for r in rows), 3),
            "warranted_width": round(cfg["warranted_range"][1] - cfg["warranted_range"][0], 3),
            "OBJECTIVE_METRIC_calibration_increase_per_claim_read":
                round(statistics.mean(r["calibration_increase_per_claim"] for r in rows), 4),
            "mean_calibration_increase": round(statistics.mean(r["calibration_increase"] for r in rows), 3),
            "mean_claims_read": round(statistics.mean(r["claims_read"] for r in rows), 2),
            "linkage_failures": failures}


# ===================== PART B: double-counting (covid) =======================
DC_TOP = "the probability that SARS-CoV-2 came from a laboratory (as opposed to a natural origin)"
DC_BASE = ("You are weighing where SARS-CoV-2 came from. Known background: the earliest cases cluster "
           "around a large live-animal market; the virus has some unusual genomic features; comparable "
           "past epidemics have had a range of origins.")
DC_CLUES = ["A major virology institute in the city conducts research on bat coronaviruses.",
            "A second research laboratory in the same city also handled coronavirus samples.",
            "Biosafety concerns had previously been raised about coronavirus work in that city."]
DC_NOTE = ("Note: these three observations are not independent. All three follow from a single underlying "
           "fact, that this city is a major hub of coronavirus research. Treat them as one correlated "
           "line of evidence, not three separate ones.")
DC_SYS = ("Reason only from what you are told in this conversation. Do not use outside knowledge about "
          "this specific event. Answer every turn in strict JSON only.")
DC_ASK = '\nReturn JSON: {"p_lab": number 0..1, "why": one short sentence}.'


def p_lab(system, messages, model, temperature, dry, dry_p):
    if dry:
        return dry_p, '{"p_lab": %s}' % dry_p
    txt = call(system, messages, model, temperature, dry)
    j = parse(txt)
    try:
        return float(j["p_lab"]), txt
    except Exception:
        return None, txt


def run_doublecount(name, prior, model, temperature, dry):
    base_user = (f"Your starting belief is P(lab) = {prior:.2f}. {DC_BASE}\n\nGiven only this, what is "
                 f"your probability for {DC_TOP}?" + DC_ASK)
    base_p, base_reply = p_lab(DC_SYS, [{"role": "user", "content": base_user}], model, temperature, dry, prior)
    clues = "\n".join(f"- {c}" for c in DC_CLUES)
    sep = (f"Here are three additional observations:\n{clues}\n\nUpdate from your previous answer and give "
           f"your probability for {DC_TOP}." + DC_ASK)
    flag = (f"Here are three additional observations:\n{clues}\n\n{DC_NOTE}\n\nUpdate from your previous "
            f"answer and give your probability for {DC_TOP}." + DC_ASK)
    hist = [{"role": "user", "content": base_user}, {"role": "assistant", "content": base_reply or "{}"}]
    sep_p, _ = p_lab(DC_SYS, hist + [{"role": "user", "content": sep}], model, temperature, dry, round(prior + 0.16, 2))
    flag_p, _ = p_lab(DC_SYS, hist + [{"role": "user", "content": flag}], model, temperature, dry, round(prior + 0.08, 2))
    row = {"persona": name, "baseline": base_p, "separate": sep_p, "flagged": flag_p}
    if None not in (base_p, sep_p, flag_p):
        row["double_counting_effect"] = round((sep_p - base_p) - (flag_p - base_p), 3)
    else:
        row["note"] = "a call failed to parse; rerun"
    return row


def score_doublecount(rows):
    eff = [r["double_counting_effect"] for r in rows if "double_counting_effect" in r]
    mean = round(statistics.mean(eff), 3) if eff else None
    return {"per_persona": rows, "mean_double_counting_effect": mean,
            "fired": mean is not None and mean > 0.03,
            "reading": "Positive = correlated clues shown separately moved confidence further than flagging them as one."}


# ===================== main ==================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", choices=list(CASES), default="covid")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--model", default="claude-sonnet-4-6")
    ap.add_argument("--temperature", type=float, default=0.7)
    a = ap.parse_args()
    cfg = CASES[a.case]

    linkage = score_linkage([run_linkage(n, p, cfg, a.model, a.dry_run) for n, p in PERSONAS], cfg)
    linkage["case"] = a.case
    report = {"case": a.case, "shape": cfg["shape"], "question": cfg["top_q"], "model": a.model,
              "PART_A_linkage_integrity": linkage,
              "warranted_shape_notes": cfg["notes"],
              "caveat": "LLM personas, few runs. Suggestive, not proof. Starter KB for a demonstration."}
    if cfg["double_count"]:
        report["PART_B_double_counting"] = score_doublecount(
            [run_doublecount(n, p, a.model, a.temperature, a.dry_run) for n, p in PERSONAS])
    else:
        report["PART_B_double_counting"] = "not run: double-counting is the covid-characteristic probe"

    print("=" * 78)
    print(f"EPISTACK EVALUATION ({VERSION})   case={a.case} [{cfg['shape']}]   model={a.model}")
    print(f"Question: {cfg['top_q']}")
    if a.dry_run:
        print(">> DRY RUN: numbers are PLACEHOLDERS, not results.")
    print("=" * 78)
    print(json.dumps(report, indent=2))
    print("=" * 78)
    print("READING")
    print("  crux_localization_rate: did reasoners find the claim that governs THIS case?")
    print("  warranted_stance_survival_rate: for settled cases this catches false balance under pressure.")
    print("  OBJECTIVE_METRIC: calibration gained (toward the case's warranted width/range) per claim read.")
    print("  Run each case on both models; compounding = the same instrument travels across shapes.")


if __name__ == "__main__":
    main()
