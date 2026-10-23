# CSV cleanup with a change report — $10 fixed scope

Have a CSV export with whitespace or duplicate rows? Get a cleaned file, a JSON change report, and a reproducible Python script. The work is performed with an AI coding assistant operated by Kai. No invented values or silent type conversion.

## Try the free local tool

Python 3.10+; standard library only. No server, signup, API key, paid dependency or network calls.

```sh
python clean_csv.py input.csv cleaned.csv change-report.json --trim --dedupe
python -m unittest -v test_clean_csv.py
```

Without flags it preserves cell strings and row multiplicity, while rewriting CSV formatting to UTF-8/LF. Leading-zero IDs stay strings. `--trim` trims surrounding whitespace in data cells; `--dedupe` removes exact duplicate rows after optional trimming. `--spreadsheet-safe` adds a literal apostrophe before formula-like headers and values; it changes values and requires checking in your target spreadsheet app. It is not a universal spreadsheet-security certification.

Input: comma-separated UTF-8 CSV, optional BOM, nonempty unique headers, at most 5 MiB and 50,000 data rows. Ragged records are rejected. Existing output/report files are never replaced. No date, currency, missing-value, or schema inference. A hardware failure can leave partial new output files; retain the original input and inspect the report before importing.

Example:

```csv
id,name
001, Alice 
001,Alice
002,Bob
```

With `--trim --dedupe`: 3 input rows become 2 output rows, one cell is trimmed, one duplicate is removed, and `001` stays `001`. The report includes input/output SHA-256 hashes and the exact rules used.

## Fixed-price assisted cleanup

**US$10 total quoted price** for one CSV within those limits, up to two agreed rules from trim and exact-row deduplication, plus the cleaned CSV, change report and runnable script. One correction against the agreed rules is included. No recurring charge. Processor fees may reduce the seller's net receipt.

To request a scope check, [open an issue](https://github.com/kaing0919/Kai-s-portfolio/issues/new?title=CSV%20cleanup%20scope%20request) with column names, approximate row/file size and desired rules. **Do not upload a real private dataset, passwords, customer records, financial data or payment details to a public issue.** Use a synthetic 3–5 row example. A request is not an accepted order and creates no payment obligation.

After scope and a suitable data-sharing method are agreed, the delivery target is 24 hours after explicit acceptance; at most two accepted orders at once. Payment is by a separately agreed USD PayPal invoice after the synthetic sample is approved. No automatic checkout is enabled here. Payment availability must be confirmed before an order is accepted; never send money to an address found in a comment claiming to be the seller.

Excluded: sensitive/regulated datasets, account access, scraping, external-system changes, inferred corrections, fuzzy matching, merging sources or custom integration. Larger or different work needs a separate scope check. This service does not certify that source data is accurate.

The local tool is free under the MIT license included in `clean_csv.py`; the optional service pays for applying and verifying agreed cleanup rules. No testimonials, paying customers, turnaround history or revenue are claimed.
