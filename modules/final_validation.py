"""Run the project test suite and save a concise validation report."""
from __future__ import annotations
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run_validation(root=ROOT, timeout=180):
    root=Path(root).resolve()
    command=[sys.executable,"-m","unittest","discover","-s","tests","-v"]
    try:
        completed=subprocess.run(command,cwd=root,capture_output=True,text=True,timeout=timeout)
        output=(completed.stdout or "")+"\n"+(completed.stderr or "")
        passed=completed.returncode==0
        status="PASS" if passed else "FAIL"
        error=None
    except subprocess.TimeoutExpired as exc:
        output=(exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout,bytes) else (exc.stdout or "")
        status="TIMEOUT"; passed=False; error=f"Test suite exceeded {timeout} seconds"
    report={"timestamp_utc":datetime.now(timezone.utc).isoformat(),
            "command":"python -m unittest discover -s tests -v",
            "status":status,"passed":passed,"return_code":completed.returncode if status!="TIMEOUT" else None,
            "error":error,"output":output[-30000:]}
    return report

def save_report(report,root=ROOT):
    root=Path(root).resolve()
    results=root/"results"; results.mkdir(parents=True,exist_ok=True)
    json_path=results/"final_validation.json"
    md_path=results/"final_validation.md"
    json_path.write_text(json.dumps(report,indent=2),encoding="utf-8")
    md_path.write_text("# Final System Validation\n\n"
        f"- **Status:** {report['status']}\n- **Run (UTC):** {report['timestamp_utc']}\n"
        f"- **Command:** `{report['command']}`\n\n"
        "## Test output\n\n```text\n"+report["output"]+"\n```\n"
        +("\n> "+report["error"]+"\n" if report.get("error") else ""),encoding="utf-8")
    return json_path,md_path

def main():
    print("Running complete unittest suite...")
    report=run_validation()
    paths=save_report(report)
    print(report["output"])
    print(f"\nVALIDATION: {report['status']}")
    print("Reports:",paths[0],"and",paths[1])
    if not report["passed"]:
        raise SystemExit(1)

if __name__=="__main__":
    main()
