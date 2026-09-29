"""Validate and report on CDC PLACES North Carolina county estimates."""
import argparse
import csv
import hashlib
import io
import re
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

SOURCE = "https://data.cdc.gov/resource/d3i6-k6z5.csv"
FIELDS = ["stateabbr", "countyfips", "countyname", "totalpopulation",
          "diabetes_crudeprev", "obesity_crudeprev"]


def get_data():
    query = urllib.parse.urlencode({"$select": ",".join(FIELDS),
                                    "$where": "stateabbr='NC'",
                                    "$order": "countyfips", "$limit": "5000"})
    request = urllib.request.Request(SOURCE + "?" + query,
                                     headers={"User-Agent": "CDC-portfolio-pipeline/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def validate(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    missing = set(FIELDS) - set(reader.fieldnames or [])
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    rows = list(reader)
    if not rows:
        raise ValueError("No records")
    counts = Counter((r["countyfips"] or "").strip() for r in rows)
    good, issues = [], []
    for line, row in enumerate(rows, 2):
        fips = (row["countyfips"] or "").strip()
        checks = []
        if row["stateabbr"] != "NC": checks.append("state outside NC")
        if not re.fullmatch(r"37[0-9]{3}", fips): checks.append("invalid NC county FIPS")
        if counts[fips] > 1: checks.append("duplicate county FIPS")
        if not (row["countyname"] or "").strip(): checks.append("missing county name")
        pop = (row["totalpopulation"] or "").strip()
        if not pop.isdigit() or int(pop) < 1: checks.append("invalid population")
        for field in ("diabetes_crudeprev", "obesity_crudeprev"):
            try:
                value = float(row[field])
                if not 0 <= value <= 100: raise ValueError()
            except (ValueError, TypeError):
                checks.append("invalid or missing " + field)
        if checks:
            issues.extend(dict(line=line, countyfips=fips, issue=issue) for issue in checks)
        else:
            good.append({field: row[field].strip() for field in FIELDS[1:]})
    return good, issues, len(rows)


def save_csv(path, fields, records):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def run(raw, out, origin):
    good, issues, count = validate(raw)
    out.mkdir(parents=True, exist_ok=True)
    (out / "source.csv").write_bytes(raw)
    save_csv(out / "counties.csv", FIELDS[1:], good)
    save_csv(out / "exceptions.csv", ["line", "countyfips", "issue"], issues)
    lines = ["# Data quality report", "",
             "Generated UTC: " + datetime.now(timezone.utc).isoformat(),
             "Source: " + origin,
             "SHA-256: " + hashlib.sha256(raw).hexdigest(),
             "Rows received: " + str(count),
             "Valid rows: " + str(len(good)),
             "Invalid rows: " + str(count - len(good)),
             "Issues logged: " + str(len(issues)), "",
             "## County summaries", ""]
    if good:
        for field in ("diabetes_crudeprev", "obesity_crudeprev"):
            values = [float(row[field]) for row in good]
            lines.append(field + ": unweighted mean %.2f%%; range %.2f–%.2f%%" %
                         (mean(values), min(values), max(values)))
    lines += ["", "## Interpretation", "",
              "PLACES provides model-based estimates, not observed case counts. "
              "Unweighted county means are not statewide prevalence. This brief "
              "report omits confidence intervals and does not support causal claims.", ""]
    (out / "quality_report.md").write_text("\n".join(lines), encoding="utf-8")
    return count, len(good), len(issues)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="Saved CDC-format CSV")
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    try:
        raw = args.input.read_bytes() if args.input else get_data()
        count, valid, issues = run(raw, args.out, str(args.input or SOURCE))
        print("Rows: %s; valid: %s; issues: %s" % (count, valid, issues))
        raise SystemExit(0 if valid and not issues else 1)
    except (OSError, ValueError, UnicodeError) as error:
        parser.exit(2, "Pipeline failed: %s\n" % error)
