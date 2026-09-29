# Public Health Data Quality and Reporting Pipeline

Uses the real CDC PLACES county GIS-friendly 2024 release to validate North Carolina county data and produce analyst-ready outputs.

Source: https://data.cdc.gov/d/d3i6-k6z5

## Run

Requires Python 3.10+; no packages to install.

    python pipeline.py --out outputs
    python -m unittest discover -s tests -v

To rerun with a saved CDC-format CSV:

    python pipeline.py --input outputs/source.csv --out outputs

Outputs include source.csv (the exact input), counties.csv (valid rows), exceptions.csv (flagged rows), and quality_report.md (provenance, counts, summary). A nonzero exit status means a source or quality issue needs review. Invalid rows are excluded rather than filled or silently corrected.

Checks cover required columns, North Carolina scope, county FIPS, duplicate FIPS, population, and diabetes/obesity crude prevalence between 0 and 100. The SHA-256 checksum identifies the input version.

For Tableau, connect to outputs/counties.csv and compare diabetes and obesity estimates by county. Display the data source and note that PLACES figures are modeled estimates. The reported unweighted mean of county values is not a statewide prevalence estimate. Review CDC methodology and confidence intervals before formal comparisons.

This is an independent portfolio demonstration of public health data extraction, quality checks, exception reporting, and reproducible reporting. It does not establish full-time work experience.
