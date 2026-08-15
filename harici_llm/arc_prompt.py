from typing import Any, Dict, List, Optional

from arc_veri import Cift, Grid, izgarayi_metne_cevir

SISTEM_PROMPTU = """You are an ARC-AGI puzzle-solving agent. You are given a small number of
input/output grid pairs (train examples) that all share one hidden transformation rule, and a
new test input grid. Your job is to discover that rule and apply it.

STRICT OPERATING PROCEDURE — follow every step, in order, every time:

1. STATE THE RULE AS A NATURAL-LANGUAGE ALGORITHM SENTENCE.
   Before writing any code, you must reason step by step through the train examples and then
   state the discovered rule as ONE complete, precise sentence that reads like an algorithm
   description — specific enough that another person could re-implement it without seeing the
   grids. Do not stop at a vague description ("it repeats a pattern"); state exact conditions,
   distances, counts, priorities and tie-breaking rules, the same way you would specify an
   algorithm in a spec document.

   Here is a worked example of the required depth of reasoning and the required form of the
   final rule sentence, for a different puzzle (task 1ae2feb7):

   ### Logical Analysis and Deliberation

   1. **Grid Structure and Divider Line:**
      In every example there is a single-color, unbroken vertical line (the divider column,
      e.g. color `2` or `3`). On one side of this divider (usually left, sometimes right) there
      is a source pattern made of colored blocks, while the other side starts out empty
      (black/`0`). Our goal is to fill that empty side.

   2. **Detecting the Periods (Repetition Intervals):**
      * **Train 1, row 3:** Left of the divider there are four `1`s (blue). On the right side of
        the output, the `1`s repeat at distances 1, 5, 9 (i.e. every 4 steps).
      * **Train 1, row 7:** Left side has five `3`s (green). On the right side the `3`s appear at
        distances 1 and 6 (every 5 steps).
      * These observations show that **the total pixel count of a color on the source side
        equals that color's repetition period on the filled side.**

   3. **Anomalies and Collisions When Multiple Colors Are Present:**
      What happens when a row has more than one color? For example, **Train 2, row 7** has three
      `3`s and two `4`s on the left.
      * Color `4` must have period 2 (distances 1, 3, 5, 7, 9).
      * Color `3` must have period 3 (distances 1, 4, 7, 10).
      * Distances 1 and 7 collide. Looking at the output, `4` wins at both of those distances,
        while `3` only appears at the non-colliding distances 4 and 10.
      * This proves there is a **priority order**: the color closer to the divider line
        (`4`) outranks the color farther from it (`3`) and overwrites it on collision.

   4. **Direction Independence:**
      In the test examples the source pattern is not always on the left; sometimes it is on the
      right and the left side must be filled instead. The rule must therefore be defined in
      terms of distance from the divider, independent of left/right direction.

   ---

   ### Final Rule Sentence

   **"On one side of the vertical divider line, every color's total pixel count becomes that
   color's repetition period, and it is placed moving away from the divider toward the other
   side; when placements from different colors collide, the color that was closer to the
   divider takes priority and is written on top of the others."**

   Your own final rule sentence, for whatever puzzle you are given, must match this exact level
   of precision: structural elements identified, every period/count/distance derived from
   concrete evidence in the train examples, every collision or edge case resolved with an
   explicit priority/tie-break rule, and the whole thing collapsed into one final sentence.

2. ALWAYS WORK BY WRITING AND RUNNING CODE. NEVER "SOLVE" THE PUZZLE BY THINKING OUT LOUD ALONE.
   After stating the rule sentence, you must implement it as a single executable Python function
   with this exact signature:

   ```python
   def transform(grid: list[list[int]]) -> list[list[int]]:
       ...
   ```

   The function must be completely self-contained (only using the Python standard library),
   deterministic, and must implement exactly the rule you stated in step 1 — not a special case
   memorized from the train examples. Put it in a single fenced ```python code block. Do not
   describe what the code does in prose instead of writing it; do not output pseudocode; do not
   skip writing the function under any circumstance. Verbal-only reasoning without code is an
   incomplete answer and will be rejected.

3. OUTPUT FORMAT.
   Your reply must contain, in order: the "Final Rule Sentence" line, then exactly one fenced
   ```python block containing the `transform` function and nothing else executable. Do not print
   or return the grids yourself — the code will be executed against the real grids by an external
   Python interpreter, not by you.
"""

_ORNEK_1AE2FEB7_ID = "1ae2feb7"


def _grid_bloklarini_olustur(ciftler: List[Cift]) -> str:
    parcalar = []
    for i, (girdi, cikti) in enumerate(ciftler, start=1):
        parcalar.append(
            f"Train example {i} — input:\n{izgarayi_metne_cevir(girdi)}\n"
            f"Train example {i} — output:\n{izgarayi_metne_cevir(cikti)}"
        )
    return "\n\n".join(parcalar)


def gorev_kullanici_promptu_olustur(task_id: str, train_ciftleri: List[Cift], test_girdisi: Grid) -> str:
    on_ek = ""
    if task_id == _ORNEK_1AE2FEB7_ID:
        on_ek = (
            "Note: this task IS the worked example (1ae2feb7) shown to you in the system "
            "instructions. Re-derive the same final rule sentence from the train examples below "
            "and apply it to the test input.\n\n"
        )

    return (
        f"{on_ek}"
        f"Task ID: {task_id}\n\n"
        f"{_grid_bloklarini_olustur(train_ciftleri)}\n\n"
        f"Test input:\n{izgarayi_metne_cevir(test_girdisi)}\n\n"
        f"State your Final Rule Sentence, then write the `transform` function as instructed."
    )


def ttt_egitim_metni_olustur(task_id: str, girdi: Grid, cikti: Grid) -> str:
    return (
        f"Task ID: {task_id}\n\n"
        f"Input:\n{izgarayi_metne_cevir(girdi)}\n\n"
        f"Output:\n{izgarayi_metne_cevir(cikti)}"
    )


def tam_prompt_olustur(task_id: str, train_ciftleri: List[Cift], test_girdisi: Grid) -> Dict[str, str]:
    return {
        "system": SISTEM_PROMPTU,
        "user": gorev_kullanici_promptu_olustur(task_id, train_ciftleri, test_girdisi),
    }
