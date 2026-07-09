#!/usr/bin/env python3
"""
refinement_loop.py — AutoEvolve LaTeX Engine v1.0
Pipeline: SENSE -> DIAGNOSE -> FIX -> VERIFY -> EVOLVE -> LEARN

Refinement loop for academic LaTeX documents:
1. Compile document
2. Run TDD tests
3. Parse log for issues
4. Apply auto-fixes for known patterns
5. Re-compile and re-test
6. Report results and save metrics
"""

import sys
import os
import json
import re
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX_FILE = os.path.join(BASE_DIR, "artigo_150_questoes.tex")
LOG_FILE = os.path.join(BASE_DIR, "artigo_150_questoes.log")
TESTS_DIR = os.path.join(BASE_DIR, "tests")
REPORTS_DIR = os.path.join(TESTS_DIR, "reports")
EVOLVE_DIR = os.path.join(BASE_DIR, "orchestration", "evolutions")
BACKUP_DIR = os.path.join(BASE_DIR, "orchestration", "backups")

MAX_ITERATIONS = 5
FIX_HISTORY_FILE = os.path.join(BASE_DIR, "orchestration", "fix_history.json")


class RefinementLoop:
    """AutoEvolve refinement loop for LaTeX documents."""

    def __init__(self):
        self.iteration = 0
        self.history = self._load_history()
        self.issues_found = []
        self.fixes_applied = []

    def _load_history(self):
        if os.path.exists(FIX_HISTORY_FILE):
            with open(FIX_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"sessions": [], "fix_patterns": {}}

    def _save_history(self):
        os.makedirs(os.path.dirname(FIX_HISTORY_FILE), exist_ok=True)
        with open(FIX_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def _make_backup(self):
        """Backup current .tex before applying fixes."""
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"artigo_{timestamp}.tex")
        shutil.copy2(TEX_FILE, backup_path)
        print(f"  [BACKUP] Saved to {backup_path}")
        return backup_path

    # ----------------------------------------------------------------
    # SENSE: Compile and read log
    # ----------------------------------------------------------------
    def sense(self):
        """Compile document and read log."""
        print("\n  --- SENSE: Compiling document ---")
        for i in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", TEX_FILE],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=120
            )
            status = "OK" if result.returncode == 0 else f"EXIT={result.returncode}"
            print(f"    Pass {i+1}: {status}")

        if not os.path.exists(LOG_FILE):
            print("    ERROR: log file not found")
            return ""

        with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
            log = f.read()

        # Extract key metrics
        pages = re.search(r"Output written on .*?\((\d+) pages?", log)
        self.page_count = int(pages.group(1)) if pages else 0
        print(f"    Pages: {self.page_count}")
        return log

    # ----------------------------------------------------------------
    # DIAGNOSE: Parse log for issues
    # ----------------------------------------------------------------
    def diagnose(self, log):
        """Parse log for errors, overfull, underfull, warnings."""
        print("\n  --- DIAGNOSE: Parsing issues ---")
        issues = []

        # 1. LaTeX errors (lines starting with '!')
        errors = re.findall(r"^! .*", log, re.MULTILINE)
        for err in errors[:10]:
            issues.append({
                "type": "error",
                "severity": "critical",
                "message": err.strip(),
                "auto_fixable": False,
            })

        # 2. Overfull boxes
        overfulls = re.findall(
            r"Overfull \\hbox \(([0-9.]+)pt too wide\) in paragraph at lines (\d+)--(\d+)",
            log
        )
        for pts, start, end in overfulls:
            pt_val = float(pts)
            issues.append({
                "type": "overfull",
                "severity": "warning" if pt_val < 12 else "critical",
                "message": f"Overfull hbox {pts}pt at lines {start}-{end}",
                "lines": (int(start), int(end)),
                "value_pt": pt_val,
                "auto_fixable": pt_val < 3,  # small overfulls can be auto-fixed
            })

        # 3. Underfull boxes
        underfulls = re.findall(
            r"Underfull \\hbox \(badness (\d+)\) in paragraph at lines (\d+)--(\d+)",
            log
        )
        for badness, start, end in underfulls:
            bad_val = int(badness)
            if bad_val >= 10000:
                issues.append({
                    "type": "underfull",
                    "severity": "warning",
                    "message": f"Underfull hbox (badness {badness}) at lines {start}-{end}",
                    "lines": (int(start), int(end)),
                    "badness": bad_val,
                    "auto_fixable": False,
                })

        # 4. Undefined references
        undefined = re.findall(
            r"LaTeX Warning: (?:Citation|Reference) `(.*?)' undefined",
            log
        )
        for ref in undefined:
            issues.append({
                "type": "undefined_ref",
                "severity": "critical",
                "message": f"Undefined reference: {ref}",
                "auto_fixable": False,
            })

        # 5. Font warnings
        font_warns = re.findall(
            r"LaTeX Font Warning: (.*?)(?: on input line \d+)?\.",
            log
        )
        for fw in font_warns:
            issues.append({
                "type": "font_warning",
                "severity": "minor",
                "message": f"Font: {fw.strip()[:100]}",
                "auto_fixable": False,
            })

        self.issues_found = issues
        print(f"    Found {len(issues)} issue(s):")
        for iss in issues:
            icon = {"critical": "!!", "warning": "!", "minor": "i"}[iss["severity"]]
            print(f"      [{icon}] [{iss['type']}] {iss['message'][:100]}")

        return issues

    # ----------------------------------------------------------------
    # FIX: Apply auto-fixes for known patterns
    # ----------------------------------------------------------------
    def fix(self, issues):
        """Apply fixes to the .tex file based on detected issues."""
        print("\n  --- FIX: Applying auto-fixes ---")
        self.fixes_applied = []

        if not self.iteration == 0:
            # Only backup before first fix in a session
            pass

        with open(TEX_FILE, "r", encoding="utf-8") as f:
            tex_content = f.read()

        modified = False

        for issue in issues:
            if not issue.get("auto_fixable"):
                continue

            fix_applied = False

            if issue["type"] == "overfull" and issue["value_pt"] < 3:
                # Small overfull: insert \sloppy at paragraph start
                start_line = issue["lines"][0]
                lines = tex_content.split("\n")
                if start_line <= len(lines):
                    # Find the paragraph start (go back to last blank line or section)
                    para_start = start_line - 1
                    while para_start > 0 and lines[para_start].strip() != "":
                        para_start -= 1
                    # Insert \sloppy before the paragraph
                    insert_at = para_start + 1
                    if insert_at < len(lines):
                        indent = "  "
                        lines.insert(insert_at, f"{indent}% AutoEvolve: sloppy for overfull\n")
                        lines.insert(insert_at + 1, f"{indent}{{\\sloppy ")
                        # Find paragraph end and close brace
                        para_end = start_line
                        while para_end < len(lines) and lines[para_end].strip() != "":
                            para_end += 1
                        lines.insert(para_end + 1, f"{indent}}}% End sloppy")
                        tex_content = "\n".join(lines)
                        modified = True
                        fix_applied = True
                        self.fixes_applied.append({
                            "issue": issue["message"],
                            "fix": "sloppy wrapper",
                            "lines": issue["lines"],
                        })
                        print(f"    [FIX] Applied sloppy at lines {issue['lines']}")

            if fix_applied:
                break  # One fix per iteration

        if modified:
            self._make_backup()
            with open(TEX_FILE, "w", encoding="utf-8") as f:
                f.write(tex_content)
            print(f"    Changes written to {os.path.basename(TEX_FILE)}")
        else:
            print("    No auto-fixable issues found.")

        return modified

    # ----------------------------------------------------------------
    # VERIFY: Run TDD test suites
    # ----------------------------------------------------------------
    def verify(self):
        """Run TDD test suites."""
        print("\n  --- VERIFY: Running TDD tests ---")
        result = subprocess.run(
            [sys.executable, "run_all_tests.py"],
            cwd=TESTS_DIR,
            capture_output=True,
            text=True,
            timeout=180
        )
        print(result.stdout[-1500:] if len(result.stdout) > 1500 else result.stdout)
        return result.returncode == 0

    # ----------------------------------------------------------------
    # EVOLVE: Track patterns, save metrics
    # ----------------------------------------------------------------
    def evolve(self, passed):
        """Track fix patterns and save evolution metrics."""
        print("\n  --- EVOLVE: Recording metrics ---")
        session = {
            "timestamp": datetime.now().isoformat(),
            "iteration": self.iteration,
            "page_count": getattr(self, "page_count", 0),
            "issues_found": len(self.issues_found),
            "fixes_applied": len(self.fixes_applied),
            "tests_passed": passed,
        }
        self.history["sessions"].append(session)

        # Update fix pattern frequency
        for fix in self.fixes_applied:
            pattern = fix["fix"]
            if pattern not in self.history["fix_patterns"]:
                self.history["fix_patterns"][pattern] = 0
            self.history["fix_patterns"][pattern] += 1

        self._save_history()
        print(f"    Session saved (iteration {self.iteration})")
        print(f"    Total sessions: {len(self.history['sessions'])}")
        print(f"    Known fix patterns: {len(self.history['fix_patterns'])}")

    # ----------------------------------------------------------------
    # LEARN: Generate insights and update knowledge
    # ----------------------------------------------------------------
    def learn(self):
        """Generate insights from the session history."""
        print("\n  --- LEARN: Generating insights ---")
        if len(self.history["sessions"]) < 2:
            print("    Not enough data for insights (need >= 2 sessions)")
            return

        recent = self.history["sessions"][-5:]

        # Trend: issues decreasing?
        issue_counts = [s["issues_found"] for s in recent]
        if len(issue_counts) >= 2 and issue_counts[-1] < issue_counts[0]:
            print(f"    [TREND] Issues decreasing: {issue_counts[0]} -> {issue_counts[-1]}")
        elif len(issue_counts) >= 2 and issue_counts[-1] > issue_counts[0]:
            print(f"    [TREND] Issues increasing: {issue_counts[0]} -> {issue_counts[-1]}")

        # Most effective fix patterns
        if self.history["fix_patterns"]:
            best_pattern = max(self.history["fix_patterns"], key=self.history["fix_patterns"].get)
            print(f"    [PATTERN] Most used fix: '{best_pattern}' "
                  f"({self.history['fix_patterns'][best_pattern]} times)")

        # Page count stability
        page_counts = [s["page_count"] for s in recent if s["page_count"] > 0]
        if page_counts:
            print(f"    [STABILITY] Page count: {min(page_counts)}-{max(page_counts)}")

        print("    Learning complete.")

    # ----------------------------------------------------------------
    # RUN: Full pipeline
    # ----------------------------------------------------------------
    def run(self):
        """Execute the full refinement loop."""
        print(f"\n{'='*70}")
        print(f"  AutoEvolve LaTeX Refinement Loop")
        print(f"  Document: {os.path.basename(TEX_FILE)}")
        print(f"  Max iterations: {MAX_ITERATIONS}")
        print(f"{'='*70}")

        for iteration in range(1, MAX_ITERATIONS + 1):
            self.iteration = iteration
            print(f"\n{'~'*50}")
            print(f"  ITERATION {iteration}/{MAX_ITERATIONS}")
            print(f"{'~'*50}")

            # SENSE
            log = self.sense()
            if not log:
                print("  ERROR: Cannot read log. Aborting.")
                break

            # DIAGNOSE
            issues = self.diagnose(log)

            # Check if we're done
            critical_issues = [i for i in issues if i["severity"] == "critical"]
            fixable_issues = [i for i in issues if i.get("auto_fixable")]

            if len(critical_issues) == 0 and len(fixable_issues) == 0:
                print(f"\n  >>> No issues found. Document is clean! <<<")
                self.evolve(passed=True)
                break

            if len(critical_issues) > 0:
                print(f"\n  >>> {len(critical_issues)} critical issue(s) require manual intervention <<<")
                for ci in critical_issues[:5]:
                    print(f"      {ci['message']}")

            # FIX
            if len(fixable_issues) > 0:
                self.fix(fixable_issues)
            else:
                print("\n  No auto-fixable issues to apply.")

            # VERIFY
            passed = self.verify()

            # EVOLVE
            self.evolve(passed)

            if passed and len(critical_issues) == 0:
                print(f"\n  >>> All tests passed at iteration {iteration} <<<")
                break

        # LEARN (final)
        self.learn()

        print(f"\n{'='*70}")
        print(f"  Refinement loop complete.")
        print(f"  Iterations: {self.iteration}")
        print(f"  Issues found: {len(self.issues_found)}")
        print(f"  Fixes applied: {len(self.fixes_applied)}")
        print(f"{'='*70}\n")

        return 0 if len([i for i in self.issues_found if i["severity"] == "critical"]) == 0 else 1


def main():
    loop = RefinementLoop()
    return loop.run()


if __name__ == "__main__":
    sys.exit(main())
