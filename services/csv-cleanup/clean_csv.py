"""Local CSV cleanup with explicit rules, a change report and exclusive outputs.

MIT License. Copyright (c) 2026 Kai.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 50_000
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n")


def transform(raw, *, trim=False, dedupe=False, spreadsheet_safe=False):
    if len(raw) > MAX_BYTES:
        raise ValueError("Input exceeds 5 MiB")
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    rows = list(reader)
    if not rows or not rows[0] or any(not h.strip() for h in rows[0]):
        raise ValueError("A nonempty, unique header is required")
    header = rows[0]
    if len(set(header)) != len(header):
        raise ValueError("Duplicate column names")
    if len(rows) - 1 > MAX_ROWS:
        raise ValueError("Input exceeds 50,000 data rows")
    output = [header]
    seen = set()
    trimmed_cells = duplicate_rows = escaped_cells = 0
    for number, row in enumerate(rows[1:], start=2):
        if len(row) != len(header):
            raise ValueError(f"Ragged CSV record {number}: column count mismatch")
        cleaned = []
        for cell in row:
            value = cell.strip() if trim else cell
            trimmed_cells += int(value != cell)
            cleaned.append(value)
        identity = tuple(cleaned)
        if dedupe and identity in seen:
            duplicate_rows += 1
            continue
        seen.add(identity)
        output.append(cleaned)
    # Include headers: spreadsheet apps can interpret header cells too.
    for row in output:
        for index, cell in enumerate(row):
            if spreadsheet_safe and cell.lstrip().startswith(FORMULA_PREFIXES):
                row[index] = "'" + cell
                escaped_cells += 1
    buffer = io.StringIO(newline="")
    csv.writer(buffer, lineterminator="\n").writerows(output)
    result = buffer.getvalue().encode("utf-8")
    report = {
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "output_sha256": hashlib.sha256(result).hexdigest(),
        "input_rows": len(rows) - 1,
        "output_rows": len(output) - 1,
        "columns": len(header),
        "trimmed_cells": trimmed_cells,
        "removed_duplicate_rows": duplicate_rows,
        "spreadsheet_prefixed_cells": escaped_cells,
        "rules": {"trim": trim, "dedupe": dedupe,
                  "spreadsheet_safe": spreadsheet_safe},
        "limitations": ["No type, date, currency or missing-value inference",
                        "Spreadsheet prefixing changes values; verify in your target app",
                        "No certification of safety in every spreadsheet importer"],
    }
    return result, report


def run(input_path, output_path, report_path, **rules):
    source, target, audit = map(Path, (input_path, output_path, report_path))
    resolved = [p.resolve() for p in (source, target, audit)]
    if len(set(resolved)) != 3:
        raise ValueError("Input, output and report paths must be distinct")
    if source.stat().st_size > MAX_BYTES:
        raise ValueError("Input exceeds 5 MiB")
    if target.exists() or audit.exists():
        raise FileExistsError("Output/report already exists; choose fresh paths")
    result, report = transform(source.read_bytes(), **rules)
    # Reserve both files before writing. Exclusive create never replaces a file.
    with target.open("xb") as output:
        try:
            report_stream = audit.open("x", encoding="utf-8", newline="\n")
        except Exception:
            output.close()
            target.unlink()
            raise
        with report_stream:
            output.write(result)
            json.dump(report, report_stream, indent=2, ensure_ascii=False)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("report")
    parser.add_argument("--trim", action="store_true")
    parser.add_argument("--dedupe", action="store_true")
    parser.add_argument("--spreadsheet-safe", action="store_true")
    args = parser.parse_args()
    try:
        report = run(args.input, args.output, args.report, trim=args.trim,
                     dedupe=args.dedupe, spreadsheet_safe=args.spreadsheet_safe)
    except (ValueError, OSError, UnicodeError, csv.Error):
        parser.exit(2, "Cleanup stopped: invalid input or inaccessible/existing output. No overwrite requested.\n")
    print(f"Wrote {report['output_rows']} rows and a JSON change report.")


if __name__ == "__main__":
    main()
