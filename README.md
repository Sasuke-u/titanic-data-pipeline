# Titanic Data Pipeline

![pipeline-test](https://github.com/Sasuke-u/titanic-data-pipeline/actions/workflows/pipeline-test.yml/badge.svg)

An automated, tested, end-to-end data pipeline on AWS: raw CSV to S3, PySpark cleaning with data quality checks, Parquet storage, and SQL analytics in Amazon Athena.

## Pipeline

Raw CSV -> AWS S3 (raw/) -> PySpark cleaning + quality checks -> Parquet in S3 (clean/) -> SQL queries in Amazon Athena

## Tech stack

Python, PySpark, SQL, AWS S3 (ap-south-1), Amazon Athena, Amazon EC2, AWS IAM, boto3, GitHub Actions, Windows Task Scheduler, Git

## What the cleaning does

- Removes duplicate rows
- Drops the Cabin column (687 of 891 values are missing)
- Fills 177 missing ages with the median age
- Fills 2 missing Embarked values with the most common port (S)
- Trims extra spaces in names
- Reads quoted names correctly (quote and escape set to a double quote)
- Makes all column names lowercase for easier SQL
- Saves the result as Parquet

## Data quality checks

The pipeline stops before saving anything if any check fails:

- rows exist
- no duplicate passenger ids
- survived is only 0 or 1
- pclass is 1, 2 or 3
- age is between 0 and 100
- fare is not negative
- no missing ages

## Automation

- scripts/run_pipeline.py runs the whole pipeline in one command: clean, upload to S3, then six Athena queries.
- run_daily.bat runs the pipeline and writes a log. It is scheduled daily with Windows Task Scheduler.
- GitHub Actions (.github/workflows/pipeline-test.yml) runs the cleaning and all quality checks on every push, using only the public CSV and no AWS credentials.

## Athena analysis

Six queries run over the clean data: survival by ticket class, sex, boarding port, age group and family size, plus average fare by class.

Example result, survival by ticket class:

| pclass | passengers | survivors | survival_pct |
|---|---|---|---|
| 1 | 216 | 136 | 63.0 |
| 2 | 184 | 87 | 47.3 |
| 3 | 491 | 119 | 24.2 |

## Project structure

- scripts/clean.py - PySpark cleaning and quality checks
- scripts/run_pipeline.py - automated runner (clean, upload, Athena queries)
- scripts/explore.py - reads the CSV and shows its schema and first rows
- scripts/glue_clean.py - same cleaning, reading and writing S3 (for AWS Glue)
- run_daily.bat - scheduled run with logging
- .github/workflows/pipeline-test.yml - automated tests

## How to run locally

1. Install Java 17 and run: pip install pyspark pandas pyarrow boto3
2. Download the Titanic CSV from https://github.com/datasciencedojo/datasets and save it as data/titanic.csv
3. Run the cleaning and checks: python scripts/clean.py
4. The cleaned file is written to output/clean/clean.parquet
5. For the full pipeline (needs an AWS profile, an S3 bucket and an Athena table): python scripts/run_pipeline.py

Note: on Windows, Spark cannot write files without winutils, so clean.py writes the Parquet file through pandas on Windows and uses the normal Spark write on Linux.

## Status

- Done: S3, PySpark cleaning, Parquet, Athena queries
- Done: Data quality checks
- Done: Same script run on an Amazon EC2 server (Amazon Linux 2023, Java 17, PySpark 4.3) using an IAM role, output copied to S3
- Done: One-command pipeline runner, daily schedule and GitHub Actions tests
- Not done: AWS Glue job (script is in scripts/glue_clean.py, but AWS blocked Glue for the account)

## Security

No AWS keys are stored in this repo. Credentials live in a local AWS CLI profile, the EC2 server used an IAM role, and data, output and log folders are ignored by Git.

## Dataset

Public Titanic dataset, used for practice.
