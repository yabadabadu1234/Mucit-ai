from typing import List

from arc import Example, Task
from arc_loader import convert_grid_to_string
from araclar import tool_tanimlari_json_metni

SISTEM_PROMPTU_SABLONU = """You are an ARC-AGI puzzle-solving agent. You are given a small number of
input/output grid pairs (train examples) that all share one hidden transformation rule, and a
new test input grid. Your job is to discover that rule and apply it.

Tools:
{tool_tanimlari}
Return only a JSON function call, exactly as shown in the examples below.

STRICT OPERATING PROCEDURE — follow every step, in order, every time:

1. STATE THE RULE AS A NATURAL-LANGUAGE ALGORITHM SENTENCE.
   Before calling any tool, you must reason step by step through the train examples and then
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

2. ALWAYS WORK BY CALLING TOOLS. NEVER "SOLVE" THE PUZZLE BY THINKING OUT LOUD ALONE.
   After stating the rule sentence, use the `execute_python` tool as many times as you need to
   write and test code that implements your rule against the train examples (you may call it
   multiple times to iterate). When you are confident, call `submit_answer` with the final grid
   for the current test input. `submit_answer` is the ONLY way to register your final answer —
   text output alone is never scored.

   You are never restricted from using either tool: `execute_python` and `submit_answer` are
   always both available to you, in every turn, for every puzzle.

3. GRID SHAPE DISCIPLINE.
   The grid you pass to `submit_answer` must be rectangular: every row must have the same number
   of columns as every other row IN THAT GRID. The overall shape (rows x columns) is free to be
   anything and may differ from every train example's shape — only internal consistency is
   required. If `submit_answer` returns an error about inconsistent row lengths, that error is
   telling you your own code or reasoning produced a malformed grid; go back, find the actual bug
   in your rule or code, and submit again — never patch the shape by truncating or padding rows
   to force them equal, since that discards information about what your rule actually computed.

Example function call format:

User: Translate "Will it rain tomorrow?" into Japanese.

Assistant: ```json
{{"name": "translate_text", "arguments": {{"text": "Will it rain tomorrow?", "target_language": "Japanese"}}}}
```
"""


def sistem_promptu_olustur() -> str:
    return SISTEM_PROMPTU_SABLONU.format(tool_tanimlari=tool_tanimlari_json_metni())


_ORNEK_1AE2FEB7_ID = "1ae2feb7"


def _grid_bloklarini_olustur(train_examples: List[Example]) -> str:
    parcalar = []
    for i, ornek in enumerate(train_examples, start=1):
        parcalar.append(
            f"Train example {i} — input:\n{convert_grid_to_string(ornek.input)}\n"
            f"Train example {i} — output:\n{convert_grid_to_string(ornek.output)}"
        )
    return "\n\n".join(parcalar)


def gorev_kullanici_promptu_olustur(task: Task) -> str:
    task_id = task.name.split("-")[0] if task.name else ""
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
        f"{_grid_bloklarini_olustur(task.train_examples)}\n\n"
        f"Test input:\n{convert_grid_to_string(task.test_example.input)}\n\n"
        f"State your Final Rule Sentence, then use the tools to verify and submit your answer."
    )


def ttt_egitim_metni_olustur(task_id: str, ornek: Example) -> str:
    return (
        f"Task ID: {task_id}\n\n"
        f"Input:\n{convert_grid_to_string(ornek.input)}\n\n"
        f"Output:\n{convert_grid_to_string(ornek.output)}"
    )
