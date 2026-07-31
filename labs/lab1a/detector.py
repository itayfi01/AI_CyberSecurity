from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

LOG_PATH = Path("/data/security.log")
OUTPUT_PATH = Path("/output/findings.json")
FAILED_PASSWORD_THRESHOLD = 3


def extract_source_ip(line: str) -> str:
    if " from " not in line:
        return "unknown"
    return line.split(" from ", 1)[1].split()[0]


def analyze_log(log_path: Path) -> list[dict[str, object]]:
    if not log_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_path}")

    lines = log_path.read_text(encoding="utf-8").splitlines()
    findings: list[dict[str, object]] = []
    failed_password_sources: Counter[str] = Counter()

    for line_number, line in enumerate(lines, start=1):
        normalized = line.lower()

        if "failed password" in normalized:
            source_ip = extract_source_ip(line)
            failed_password_sources[source_ip] += 1

        if "network scan detected" in normalized:
            source_ip = extract_source_ip(line)
            findings.append(
                {
                    "finding": "Possible network service discovery",
                    "source_ip": source_ip,
                    "mitre_technique": "T1046",
                    "mitre_name": "Network Service Discovery",
                    "tactic": "Discovery",
                    "severity": "Medium",
                    "evidence": line,
                    "line_number": line_number,
                }
            )

    for source_ip, count in failed_password_sources.items():
        if count >= FAILED_PASSWORD_THRESHOLD:
            findings.append(
                {
                    "finding": "Possible brute-force login attempt",
                    "source_ip": source_ip,
                    "failed_attempts": count,
                    "mitre_technique": "T1110",
                    "mitre_name": "Brute Force",
                    "tactic": "Credential Access",
                    "severity": "High",
                    "evidence": (
                        f"{count} failed password events were detected "
                        f"from {source_ip}."
                    ),
                }
            )

    return findings


def print_findings(findings: list[dict[str, object]]) -> None:
    print("=" * 60)
    print("LAB 1A — SECURITY DETECTION REPORT")
    print("=" * 60)

    if not findings:
        print("No supported suspicious activity was detected.")
        return

    for number, finding in enumerate(findings, start=1):
        print(f"\nFinding {number}")
        print(f"Activity: {finding['finding']}")
        print(f"Source IP: {finding['source_ip']}")
        print(
            f"MITRE ATT&CK: {finding['mitre_technique']} - "
            f"{finding['mitre_name']}"
        )
        print(f"Tactic: {finding['tactic']}")
        print(f"Severity: {finding['severity']}")
        print(f"Evidence: {finding['evidence']}")


def save_findings(
    findings: list[dict[str, object]],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(findings, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    try:
        findings = analyze_log(LOG_PATH)
        print_findings(findings)
        save_findings(findings, OUTPUT_PATH)
        print(f"\nResults saved to: {OUTPUT_PATH}")
    except (FileNotFoundError, PermissionError) as exc:
        print(f"Error: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()