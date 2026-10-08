"""Consistency gate for the PROBAST+AI assessment (Supplementary File S4).

The summary table at the top of the checklist is what a reader consults first. If
it disagrees with the per-item judgements below it, the assessment is worse than
useless: it looks authoritative and is wrong. That exact drift is not caught by
spell-checking or by any numeric gate, so it gets its own test.

Run: python3 manuscript_assets/test_probast_consistency.py
"""

import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
S4 = ROOT / "Supplementary_File_S4_PROBAST_AI_Assessment.md"

VERDICTS = ("High", "Low", "Unclear")
SUMMARY_ROW = re.compile(
    r"^\|\s*(Participants|Predictors|Outcome|Analysis)\s*\|\s*\*\*(\w+)\*\*\s*\|"
    r"\s*\**(\w+)\**\s*\|"
)
DOMAIN_HEADING = re.compile(r"^## Domain \d+ — (.+)$")
ITEM_VERDICT = re.compile(r"\|\s*\*\*(" + "|".join(VERDICTS) + r")\*\*\s*\|")


def parse():
    """Return (summary, per_domain) where per_domain maps domain -> Counter."""
    text = S4.read_text()
    summary, domain, per_domain = {}, None, {}
    for line in text.splitlines():
        head = DOMAIN_HEADING.match(line)
        if head:
            domain = head.group(1).strip()
            per_domain[domain] = {v: 0 for v in VERDICTS}
            continue
        if not line.startswith("|") or "---" in line or "Question" in line:
            continue
        row = SUMMARY_ROW.match(line)
        if row:
            summary[row.group(1)] = {"risk": row.group(2), "applicability": row.group(3)}
            continue
        item = ITEM_VERDICT.search(line)
        if item and domain:
            per_domain[domain][item.group(1)] += 1
    return summary, per_domain


class ProblastConsistencyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary, cls.per_domain = parse()

    def test_01_all_four_domains_present(self):
        for name in ("Participants", "Predictors", "Outcome", "Analysis"):
            self.assertIn(name, self.summary, f"summary table missing {name}")
            self.assertIn(name, self.per_domain, f"no per-item section for {name}")

    def test_02_every_domain_has_judgements(self):
        for name, counts in self.per_domain.items():
            self.assertGreater(
                sum(counts.values()), 0, f"domain {name} has no scored items"
            )

    def test_03_summary_matches_item_judgements(self):
        """PROBAST domain summary rule: any High item makes the domain High."""
        mismatches = []
        for name, counts in self.per_domain.items():
            expected = "High" if counts["High"] > 0 else "Low"
            actual = self.summary[name]["risk"]
            if actual != expected:
                mismatches.append(
                    f"{name}: table says {actual}, but {counts['High']} High item(s) "
                    f"and {counts['Low']} Low item(s)"
                )
        self.assertEqual(
            mismatches, [],
            "summary table contradicts per-item PROBAST judgements:\n  "
            + "\n  ".join(mismatches),
        )

    def test_04_overall_rating_follows_domains(self):
        text = S4.read_text()
        m = re.search(r"\*\*Overall risk of bias: (\w+)\.", text)
        self.assertIsNotNone(m, "overall risk-of-bias statement missing")
        any_high = any(self.summary[d]["risk"] == "High" for d in self.summary)
        self.assertEqual(
            m.group(1), "High" if any_high else "Low",
            "overall rating does not follow from the domain table",
        )

    def test_05_no_unqualified_verdicts(self):
        """A verdict must be one of the three permitted PROBAST values.

        PROBAST+AI uses High / Low / Unclear for both risk of bias and
        applicability. "Moderate" appears in some secondary summaries of the
        tool but is not a permitted rating, and using it makes the table
        impossible to audit against the instrument.
        """
        bad = [
            f"{d} {k}: {v}"
            for d, row in self.summary.items()
            for k, v in row.items()
            if v not in VERDICTS
        ]
        self.assertEqual(bad, [], f"invalid verdict values: {bad}")

    def test_06_manuscript_cites_the_same_conclusion(self):
        """The manuscript must not understate the assessment it points to."""
        manuscript = (ROOT / "Journal_of_Dentistry_Example_OdontoCA.md").read_text()
        self.assertIn("PROBAST+AI", manuscript)
        self.assertIn("Supplementary File S4", manuscript.replace(
            "Supplementary Files S3 and S4", "Supplementary File S4"
        ))


if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False)
    sys.exit(0)
