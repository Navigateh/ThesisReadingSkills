import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "thesisreading_skills"
EXPECTED_SKILLS = {
    "thesis-reading",
    "paper-ingestion",
    "paper-decomposition",
    "math-formula-reading",
    "figure-table-reading",
    "experiment-analysis",
    "related-work-mapping",
    "synthesis-and-notes",
}


def read_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    metadata = {}
    for line in match.group(1).splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata


def parse_simple_yaml(path):
    result = {}
    stack = [(-1, result)]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"')
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value:
            parent[key] = value
        else:
            child = {}
            parent[key] = child
            stack.append((indent, child))
    return result


class SkillBundleTests(unittest.TestCase):
    def test_expected_skill_directories_exist(self):
        found = {path.name for path in SKILLS_ROOT.iterdir() if (path / "SKILL.md").is_file()}
        self.assertEqual(EXPECTED_SKILLS, found)

    def test_skill_frontmatter_is_valid(self):
        for skill_name in EXPECTED_SKILLS:
            with self.subTest(skill=skill_name):
                skill_md = SKILLS_ROOT / skill_name / "SKILL.md"
                frontmatter = read_frontmatter(skill_md)
                self.assertIsNotNone(frontmatter)
                self.assertEqual(skill_name, frontmatter.get("name"))
                description = frontmatter.get("description", "")
                self.assertTrue(description.startswith("Use when"))
                self.assertLessEqual(len(description), 500)

    def test_agents_openai_yaml_has_required_interface_fields(self):
        for skill_name in EXPECTED_SKILLS:
            with self.subTest(skill=skill_name):
                openai_yaml = SKILLS_ROOT / skill_name / "agents" / "openai.yaml"
                self.assertTrue(openai_yaml.is_file())
                data = parse_simple_yaml(openai_yaml)
                interface = data.get("interface", {})
                self.assertTrue(interface.get("display_name"))
                self.assertTrue(interface.get("short_description"))
                default_prompt = interface.get("default_prompt", "")
                self.assertIn(f"${skill_name}", default_prompt)

    def test_json_assets_are_valid(self):
        json_files = sorted(SKILLS_ROOT.glob("*/assets/*.json"))
        self.assertGreaterEqual(len(json_files), len(EXPECTED_SKILLS))
        for path in json_files:
            with self.subTest(path=str(path.relative_to(ROOT))):
                json.loads(path.read_text(encoding="utf-8"))

    def test_dispatcher_mentions_full_reading_parallel_route(self):
        routing = (SKILLS_ROOT / "thesis-reading" / "references" / "routing.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Full Reading", routing)
        self.assertIn("parallel [`math-formula-reading`, `figure-table-reading`, `experiment-analysis`]", routing)
        self.assertLess(routing.index("paper-decomposition"), routing.index("related-work-mapping"))

    def test_pdf_parser_compiles_and_has_help(self):
        script = SKILLS_ROOT / "paper-ingestion" / "scripts" / "parse_pdf.py"
        compile_result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, compile_result.returncode, compile_result.stderr)

        help_result = subprocess.run(
            [sys.executable, str(script), "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, help_result.returncode, help_result.stderr)
        self.assertIn("--ocr", help_result.stdout)
        self.assertIn("--extract-images", help_result.stdout)


if __name__ == "__main__":
    unittest.main()
