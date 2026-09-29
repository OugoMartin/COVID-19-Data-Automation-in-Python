import csv
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import FIELDS, validate


def encoded(rows):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.row = dict(stateabbr="NC", countyfips="37001",
                        countyname="Alamance", totalpopulation="1000",
                        diabetes_crudeprev="12.0", obesity_crudeprev="30.0")

    def test_valid(self):
        good, issues, count = validate(encoded([self.row]))
        self.assertEqual((len(good), len(issues), count), (1, 0, 1))

    def test_duplicate_and_invalid_value(self):
        other = dict(self.row, diabetes_crudeprev="101")
        good, issues, count = validate(encoded([self.row, other]))
        self.assertEqual((len(good), count), (0, 2))
        self.assertEqual(len(issues), 3)

    def test_missing_column(self):
        with self.assertRaises(ValueError):
            validate(b"countyfips\n37001\n")


if __name__ == "__main__":
    unittest.main()
