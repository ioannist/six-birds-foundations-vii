# Results

Each completed lab writes a `verdict.md` in its results directory. The verdict
is at most one page and records the hypothesis, outcome, pass/fail/surprise,
and implication for the law's statement.

Every `lab/results/<lab-id>/verdict.md` must end with a line naming the specific Lean theorem/definition (once it exists) the lab result corresponds to, e.g. "This result exercises `SixBirdsFoundationsVI.Laws.G8.odometer_invariance`, confirming the abelian-compatibility hypothesis holds for the sandpile instantiation." Before Lean lands for a given law, the line instead names the specific `THEOREMS.md` claim (e.g. "This result exercises G8's Theorem Part A").
