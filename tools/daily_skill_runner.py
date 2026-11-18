"""
Daily Agent Skill Generator & Publisher (100% Dynamic Gemini AI Edition)
========================================================================
Tự động sáng tạo, kiểm định thực thi và xuất bản Skill chuyên sâu mỗi ngày cho từng AI Agent:
- 0% fix cứng danh sách chủ đề: AI tự khám phá bài toán kỹ thuật thực chiến mới mỗi ngày dựa trên vai trò Agent và lịch sử `published_skills`.
- Kết nối Pool 9 Key Gemini (`C:\\gehihi\\gemini-keys.json`), sinh trọn bộ `SKILL.md`, `workflow.py` (thuật toán thật chỉ dùng Python Standard Library + self-test `assert`) và `README.md`.
- Cổng kiểm định thực thi (Execution Gate): Chạy thử `python workflow.py` đảm bảo `exit code == 0` trước khi `git commit & push`.
"""

import os
import re
import sys
import json
import time
import argparse
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

sys.path.insert(0, r"C:\gehihi\tools")
from headless_logger import setup_headless_log, redact_secrets
setup_headless_log(r"C:\gehihi\tools\logs", prefix="workforce_skill", keep_days=7)
from error_alert import report_failure, install_crash_hook

REPO_DIR = Path(r"C:\gehihi\projects\ai-agent-workforce")
ENV_PATH = Path(r"C:\gehihi\env\.env")
POOL_KEYS_PATH = Path(r"C:\gehihi\gemini-keys.json")
STATE_FILE = REPO_DIR / "tools" / "generator_state.json"

try:
    from rate_pacer import can_perform_action, record_action, apply_human_jitter
except ImportError:
    def can_perform_action(a, t=""): return True, "OK"
    def record_action(a, t=""): pass
    def apply_human_jitter(a=1, b=2, label=""): pass

# Chỉ định nghĩa Vai Trò & Miền Chuyên Môn của từng Agent — Chủ đề cụ thể do AI tự sáng tạo vô hạn mỗi ngày!
ROSTER = [
    {
        "id": "backend-architect",
        "name": "Backend Architect",
        "focus": "High-throughput distributed systems, resilient caching, outbox/saga consistency, database indexing & partitioning, rate limiting, concurrency control",
    },
    {
        "id": "root-cause-debugger",
        "name": "Root-Cause Debugger",
        "focus": "Production defect isolation, memory/handle leak analysis, thread/async deadlock detection, log anomaly correlation, latency tail diagnosis",
    },
    {
        "id": "clean-code-reviewer",
        "name": "Clean Code Reviewer",
        "focus": "AST static code quality, cyclomatic/cognitive complexity analysis, SOLID & architecture boundary checks, code smell detection, API naming consistency",
    },
    {
        "id": "devops-sre",
        "name": "DevOps & SRE",
        "focus": "Container/Dockerfile auditing, CI/CD pipeline validation, Kubernetes manifest & SLO error-budget calculators, graceful shutdown & health probe checks",
    },
    {
        "id": "qa-tdd-engineer",
        "name": "QA & TDD Engineer",
        "focus": "Property-based & boundary test generation, JSON schema/OpenAPI contract verification, flaky test detection, performance regression benchmarking",
    },
    {
        "id": "security-auditor",
        "name": "Security Auditor",
        "focus": "Static taint/injection scanning, secret & entropy detection, JWT/CORS/CSP policy verification, SSRF & path-traversal sanitization checks",
    },
]


def load_gemini_keys() -> list[str]:
    keys: list[str] = []
    if POOL_KEYS_PATH.exists():
        try:
            data = json.loads(POOL_KEYS_PATH.read_text(encoding="utf-8"))
            for item in data.get("keys", []):
                k = str(item.get("key", "")).strip()
                if k and k not in keys:
                    keys.append(k)
        except Exception:
            pass
    if ENV_PATH.exists():
        try:
            for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "GEMINI" in line and "=" in line:
                    _, v = line.split("=", 1)
                    v = v.strip()
                    if v and v not in keys:
                        keys.append(v)
        except Exception:
            pass
    return keys


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"rotation_index": 0, "published_skills": []}


def save_state(state: dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def _sanitize_slug(raw_slug: str, agent_id: str, count: int) -> str:
    s = re.sub(r"[^a-z0-9\-]+", "-", str(raw_slug or "").lower()).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    if len(s) < 6:
        s = f"{agent_id}-toolkit-{count + 1}"
    return s[:48].strip("-")


def _verify_workflow_script(py_code: str) -> tuple[bool, str]:
    """Chạy thử workflow.py trong file tạm để đảm bảo code thật, không lỗi cú pháp, pass toàn bộ assert."""
    import tempfile
    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"
    sub_env["PYTHONUTF8"] = "1"
    with tempfile.TemporaryDirectory() as tmp:
        script_path = Path(tmp) / "workflow.py"
        script_path.write_text(py_code, encoding="utf-8")
        try:
            res = subprocess.run(
                [sys.executable, str(script_path)],
                env=sub_env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            if res.returncode == 0:
                return True, (res.stdout or "").strip()
            return False, ((res.stderr or "") + "\n" + (res.stdout or "")).strip()[-400:]
        except Exception as e:
            return False, str(e)


def generate_skill_via_gemini(agent: dict, published_skills: list[str]) -> dict | None:
    keys = load_gemini_keys()
    if not keys:
        return None

    avoid_str = ", ".join(published_skills[-60:]) if published_skills else "None"

    base_prompt = (
        f"You are a Principal Software Engineer designing a brand-new autonomous engineering skill for the '{agent['name']}' (`{agent['id']}`) agent.\n"
        f"Agent Focus Domain: {agent['focus']}.\n\n"
        f"STRICT NON-REPETITION RULE:\n"
        f"Do NOT repeat or closely overlap with any of these already-published skill slugs:\n[{avoid_str}]\n\n"
        f"TASK:\n"
        f"1. Invent ONE specific, practical engineering analyzer/validator skill within `{agent['name']}`'s focus domain.\n"
        f"2. Write `workflow.py` (60–110 lines) using ONLY Python 3 Standard Library (`re`, `json`, `ast`, `hashlib`, `collections`, `statistics`, `dataclasses`, `datetime` — ZERO third-party packages).\n"
        f"   - Its `if __name__ == '__main__':` block MUST run 2–3 deterministic unit test cases with `assert` statements, print a JSON summary, and exit with code 0.\n"
        f"3. Write `SKILL.md` (with YAML frontmatter `name`, `description`, `agent: {agent['id']}`, `version: 1.0.0`) and `README.md`.\n\n"
        f"Return ONLY valid JSON with exact keys:\n"
        "{\n"
        '  "slug": "kebab-case-skill-name",\n'
        '  "title": "Human Readable Skill Title",\n'
        '  "skill_md": "Full markdown content of SKILL.md",\n'
        '  "workflow_py": "Full executable Python 3 source code of workflow.py",\n'
        '  "readme_md": "Full markdown content of README.md"\n'
        "}"
    )

    def _call_model(prompt_text: str, key_idx: int) -> dict | None:
        for offset in range(len(keys)):
            api_key = keys[(key_idx + offset) % len(keys)]
            model = "gemini-3.5-flash-lite" if api_key.startswith("AQ.") else "gemini-2.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            gen_cfg = {
                "responseMimeType": "application/json",
                "temperature": 0.45,
            }
            if model == "gemini-2.5-flash":
                gen_cfg["thinkingConfig"] = {"thinkingBudget": 2048}
            payload = {
                "contents": [{"parts": [{"text": prompt_text}]}],
                "generationConfig": gen_cfg,
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(req, timeout=45) as resp:
                    raw = json.loads(resp.read().decode("utf-8"))
                    for part in raw["candidates"][0]["content"]["parts"]:
                        if "text" in part and not part.get("thought"):
                            return json.loads(part["text"].strip())
            except Exception:
                continue
        return None

    parsed = _call_model(base_prompt, 0)
    for attempt in range(3):
        if not isinstance(parsed, dict) or not parsed.get("workflow_py") or not parsed.get("skill_md"):
            parsed = _call_model(base_prompt, attempt + 1)
            continue

        wf_code = str(parsed["workflow_py"]).strip()
        ok, out_or_err = _verify_workflow_script(wf_code)
        if ok:
            parsed["slug"] = _sanitize_slug(parsed.get("slug", ""), agent["id"], len(published_skills))
            if parsed["slug"] in published_skills:
                parsed["slug"] = f"{parsed['slug']}-v{len(published_skills) + 1}"
            print(f"✨ [Gemini Verified] Đã sáng tạo & chạy pass 100% skill '{parsed['slug']}'!")
            return parsed

        print(f"⚠️ [Verify Gate #{attempt + 1}] Đang tự sửa lỗi thực thi Python: {out_or_err[:140]}")
        repair_prompt = (
            f"Fix the Python bug in `workflow_py` below so `python workflow.py` runs cleanly with exit code 0.\n\n"
            f"--- ERROR TRACEBACK ---\n{out_or_err}\n\n"
            f"--- CURRENT workflow.py ---\n{wf_code}\n\n"
            'Return ONLY valid JSON: {"workflow_py": "Fixed full Python 3 code"}'
        )
        fix_res = _call_model(repair_prompt, attempt + 2)
        if isinstance(fix_res, dict) and fix_res.get("workflow_py"):
            parsed["workflow_py"] = fix_res["workflow_py"]
        else:
            parsed = None
    return None


def write_skill_package(agent: dict, pkg: dict) -> Path:
    topic_slug = pkg["slug"]
    target_dir = REPO_DIR / "agents" / agent["id"] / "skills" / topic_slug
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "SKILL.md").write_text(pkg["skill_md"].strip() + "\n", encoding="utf-8")
    (target_dir / "workflow.py").write_text(pkg["workflow_py"].strip() + "\n", encoding="utf-8")
    (target_dir / "README.md").write_text(pkg["readme_md"].strip() + "\n", encoding="utf-8")
    print(f"✅ Generated verified skill package: {target_dir}")
    return target_dir


def commit_and_push_skill(agent: dict, topic_slug: str, skill_dir: Path) -> bool:
    apply_human_jitter(min_seconds=5, max_seconds=15, label="SkillPublisher")
    commit_msg = f"feat({agent['id']}): add {topic_slug} autonomous workflow skill"
    git_env = os.environ.copy()
    git_env["GIT_TERMINAL_PROMPT"] = "0"
    cflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    # Đồng bộ nhánh main từ remote trước để tránh lỗi diverged branch
    subprocess.run(
        ["git", "pull", "--rebase", "--autostash", "origin", "main"],
        cwd=REPO_DIR,
        env=git_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=45,
        creationflags=cflags,
    )

    rel_skill = str(skill_dir.relative_to(REPO_DIR)).replace("\\", "/")
    subprocess.run(
        ["git", "add", "--", rel_skill, "tools/generator_state.json"],
        cwd=REPO_DIR,
        env=git_env,
        check=True,
        timeout=30,
        creationflags=cflags,
    )
    subprocess.run(
        ["git", "commit", "-m", commit_msg],
        cwd=REPO_DIR,
        env=git_env,
        check=True,
        timeout=30,
        creationflags=cflags,
    )

    p = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=REPO_DIR,
        env=git_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        creationflags=cflags,
    )
    if p.returncode == 0:
        print(f"🚀 Successfully pushed '{commit_msg}' to GitHub!")
        record_action("commit_burst", topic_slug)
        return True
    else:
        err_clean = redact_secrets((p.stderr or "").strip()[-500:])
        print(f"❌ Push failed: {err_clean}")
        report_failure("Daily Agent Skill", f"Push skill '{topic_slug}' lên GitHub thất bại: {err_clean}")
        return False


def run_daily_cycle(dry_run: bool = False):
    state = load_state()
    today_str = datetime.now().strftime("%Y-%m-%d")
    if not dry_run and str(state.get("last_run", "")).startswith(today_str):
        print(f"ℹ️ Hôm nay ({today_str}) đã xuất bản Skill rồi. Bỏ qua lượt chạy trùng.")
        return

    if not dry_run:
        ok, msg = can_perform_action("commit_burst")
        if not ok:
            print(f"⚠️ [RATE PACER] {msg}")
            return

    idx = state.get("rotation_index", 0) % len(ROSTER)
    agent = ROSTER[idx]
    published = list(state.get("published_skills", []))

    print(f"🎯 Selected Agent: {agent['name']} ({agent['id']})")
    pkg = generate_skill_via_gemini(agent, published)
    if not pkg:
        report_failure("Daily Agent Skill", f"Không sinh được skill mới qua Gemini cho agent {agent['id']}.")
        sys.exit(1)

    topic_slug = pkg["slug"]
    if dry_run:
        print(f"🧪 [DRY-RUN] Skill '{topic_slug}' ({pkg.get('title')}) đã vượt qua Execution Gate! Không ghi/push Git.")
        return

    prev_state_backup = json.loads(json.dumps(state))
    skill_dir = write_skill_package(agent, pkg)
    state["rotation_index"] = idx + 1
    published.append(topic_slug)
    state["published_skills"] = published
    state["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_state(state)

    success = commit_and_push_skill(agent, topic_slug, skill_dir)
    if success:
        print("🎉 Daily cycle completed successfully!")
    else:
        save_state(prev_state_backup)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Test AI generation & execution gate without git push")
    args = parser.parse_args()
    if not args.dry_run:
        install_crash_hook("Daily Agent Skill")
    run_daily_cycle(dry_run=args.dry_run)
