import os
import subprocess
import sys
import time

import boto3

BUCKET = "santhosh-titanic-pipeline-4827"
REGION = "ap-south-1"
PROFILE = "santhosh-dev"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

session = boto3.Session(profile_name=PROFILE, region_name=REGION)
s3 = session.client("s3")
athena = session.client("athena")

# STEP 1: clean the data (clean.py also runs the data quality checks)
print("STEP 1: cleaning data with PySpark (includes quality checks)")
subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "clean.py")], cwd=ROOT, check=True)

# STEP 2: upload the clean Parquet file to S3
print("STEP 2: uploading clean Parquet to S3")
local_file = os.path.join(ROOT, "output", "clean", "clean.parquet")
s3.upload_file(local_file, BUCKET, "clean/clean.parquet")
print("Uploaded to s3://" + BUCKET + "/clean/clean.parquet")

# STEP 3: run SQL queries in Athena
print("STEP 3: running Athena SQL queries")


def run_query(title, sql):
    query_id = athena.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={"Database": "titanic_db"},
        ResultConfiguration={"OutputLocation": "s3://" + BUCKET + "/athena-results/"},
    )["QueryExecutionId"]
    while True:
        state = athena.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]["Status"]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(1)
    if state != "SUCCEEDED":
        sys.exit("Query '" + title + "' ended with state: " + state)
    rows = athena.get_query_results(QueryExecutionId=query_id)["ResultSet"]["Rows"]
    print("\n--- " + title + " ---")
    for row in rows:
        print(" | ".join(cell.get("VarCharValue", "") for cell in row["Data"]))


queries = [
    ("1. Survival by ticket class",
     "SELECT pclass, COUNT(*) AS passengers, SUM(survived) AS survivors, "
     "ROUND(100.0 * SUM(survived) / COUNT(*), 1) AS survival_pct "
     "FROM titanic_db.titanic_clean GROUP BY pclass ORDER BY pclass"),
    ("2. Survival by sex",
     "SELECT sex, COUNT(*) AS passengers, SUM(survived) AS survivors, "
     "ROUND(100.0 * SUM(survived) / COUNT(*), 1) AS survival_pct "
     "FROM titanic_db.titanic_clean GROUP BY sex ORDER BY sex"),
    ("3. Survival by boarding port",
     "SELECT embarked, COUNT(*) AS passengers, SUM(survived) AS survivors, "
     "ROUND(100.0 * SUM(survived) / COUNT(*), 1) AS survival_pct "
     "FROM titanic_db.titanic_clean GROUP BY embarked ORDER BY embarked"),
    ("4. Survival by age group",
     "SELECT CASE WHEN age < 13 THEN '1 child (under 13)' "
     "WHEN age < 20 THEN '2 teen (13-19)' "
     "WHEN age < 60 THEN '3 adult (20-59)' "
     "ELSE '4 senior (60+)' END AS age_group, "
     "COUNT(*) AS passengers, SUM(survived) AS survivors, "
     "ROUND(100.0 * SUM(survived) / COUNT(*), 1) AS survival_pct "
     "FROM titanic_db.titanic_clean GROUP BY 1 ORDER BY 1"),
    ("5. Survival by family size",
     "SELECT CASE WHEN sibsp + parch = 0 THEN '1 travelling alone' "
     "WHEN sibsp + parch <= 3 THEN '2 small family (2-4)' "
     "ELSE '3 large family (5+)' END AS family_size, "
     "COUNT(*) AS passengers, SUM(survived) AS survivors, "
     "ROUND(100.0 * SUM(survived) / COUNT(*), 1) AS survival_pct "
     "FROM titanic_db.titanic_clean GROUP BY 1 ORDER BY 1"),
    ("6. Average fare by ticket class",
     "SELECT pclass, COUNT(*) AS passengers, ROUND(AVG(fare), 2) AS avg_fare, "
     "ROUND(MAX(fare), 2) AS max_fare "
     "FROM titanic_db.titanic_clean GROUP BY pclass ORDER BY pclass"),
]

for title, sql in queries:
    run_query(title, sql)

print("\nPIPELINE FINISHED OK")