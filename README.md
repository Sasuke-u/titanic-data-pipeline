# Titanic Data Pipeline

A small end-to-end data engineering project, built with Python, PySpark and AWS.

## Pipeline

Raw CSV -> AWS S3 (raw/) -> PySpark cleaning -> Parquet in S3 (clean/) -> SQL queries in Amazon Athena

## Tech stack

Python, PySpark, AWS S3 (ap-south-1), Amazon Athena, AWS IAM, Git

## What the cleaning does

- Removes duplicate rows
- Drops the Cabin column (most values are missing)
- Fills missing Age with the median age
- Fills missing Embarked with the most common port (S)
- Trims extra spaces in names
- Reads quoted names correctly (quote and escape set to a double quote)
- Makes all column names lowercase for easier SQL
- Saves the result as Parquet

## Project structure

- scripts/explore.py - reads the CSV and shows its schema and first rows
- scripts/clean.py - cleaning script, runs on a laptop
- scripts/glue_clean.py - same cleaning, reading and writing S3 (for AWS Glue)

## How to run locally

1. Install Java 17 and run: pip install pyspark pandas pyarrow
2. Download the Titanic CSV from https://github.com/datasciencedojo/datasets and save it as data/titanic.csv
3. Run: python scripts/clean.py
4. The cleaned file is written to output/clean/clean.parquet

Note: on Windows, Spark cannot write files without winutils, so clean.py writes the Parquet file through pandas on Windows and uses the normal Spark write on Linux.

## Athena

The cleaned Parquet file is uploaded to s3://YOUR-BUCKET/clean/ and an external table is created over it, then queried with SQL (for example, survival rate by passenger class).

## Status

- Done: S3, PySpark cleaning, Parquet, Athena queries
- Done: Same cleaning script run on an Amazon EC2 server (Amazon Linux 2023, Java 17, PySpark 4.3) using an IAM role, output copied to S3
- Not done: AWS Glue job (script is in scripts/glue_clean.py, but AWS blocked Glue for the account)

## Security

No AWS keys are stored in this repo. Credentials live in a local AWS CLI profile, and data and output folders are ignored by Git.

## Dataset

Public Titanic dataset, used for learning only.


