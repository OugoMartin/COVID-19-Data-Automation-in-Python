# Public Health Data Automation in Python

This repository now includes a completed [CDC PLACES data quality and reporting pipeline](places-nc-data-quality/README.md). It retrieves a real CDC dataset, checks North Carolina county records, logs exceptions, and creates reproducible report outputs. The included source snapshot yielded 100 valid county rows and no flagged issues on the recorded run.

The separate COVID-19 automation workflow described earlier remains planned. This PLACES project analyzes modeled diabetes and obesity prevalence; it is not a COVID-19 dataset. For completed COVID-19 analysis, see [Covid-19-Analysis](https://github.com/OugoMartin/Covid-19-Analysis).

## Run the completed pipeline

    cd places-nc-data-quality
    python pipeline.py --out outputs
    python -m unittest discover -s tests -v

See the [project README](places-nc-data-quality/README.md) for source, quality rules, outputs, and interpretation limits.
