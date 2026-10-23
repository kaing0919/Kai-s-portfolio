import csv
import io
import tempfile
import unittest
from pathlib import Path

from clean_csv import MAX_BYTES, run, transform


class CleanupTests(unittest.TestCase):
    def test_preserves_ids_unicode_and_quoted_fields(self):
        raw = 'id,note\n001,"你好,world"\n002,"two\nlines"\n'.encode()
        result, report = transform(raw)
        self.assertEqual(list(csv.reader(io.StringIO(result.decode()))),
                         list(csv.reader(io.StringIO(raw.decode()))))
        self.assertEqual(report["output_rows"], 2)

    def test_explicit_trim_then_dedupe(self):
        result, report = transform(b'id,name\n001, A \n001,A\n', trim=True, dedupe=True)
        self.assertEqual(result, b'id,name\n001,A\n')
        self.assertEqual(report["trimmed_cells"], 1)
        self.assertEqual(report["removed_duplicate_rows"], 1)

    def test_no_silent_deduplication_or_type_conversion(self):
        result, report = transform(b'id,value\n001,-3.00\n001,-3.00\n')
        self.assertEqual(report["output_rows"], 2)
        self.assertIn(b'001,-3.00', result)

    def test_opt_in_spreadsheet_prefixes_headers_and_values(self):
        result, report = transform(b'=header,val\n001, =SUM(A1)\n', spreadsheet_safe=True)
        self.assertEqual(result, b"'=header,val\n001,' =SUM(A1)\n")
        self.assertEqual(report["spreadsheet_prefixed_cells"], 2)

    def test_invalid_csv(self):
        for raw in (b'a,a\n1,2\n', b'a,b\n1\n', b'a,b\n"unterminated', b',b\n1,2\n', b''):
            with self.subTest(raw=raw), self.assertRaises((ValueError, csv.Error)):
                transform(raw)

    def test_bom_and_size_limit(self):
        result, _ = transform(b'\xef\xbb\xbfa,b\n1,2\n')
        self.assertEqual(result, b'a,b\n1,2\n')
        with self.assertRaises(ValueError):
            transform(b'x' * (MAX_BYTES + 1))

    def test_files_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            source, target, audit = [Path(folder) / x for x in ('in.csv', 'out.csv', 'report.json')]
            source.write_bytes(b'a\n001\n')
            run(source, target, audit)
            with self.assertRaises(FileExistsError):
                run(source, target, audit)
            self.assertEqual(source.read_bytes(), b'a\n001\n')
            with self.assertRaises(ValueError):
                run(source, source, audit)


if __name__ == '__main__':
    unittest.main()
