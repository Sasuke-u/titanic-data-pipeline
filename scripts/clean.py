import os

from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("titanic-clean").master("local[*]").getOrCreate()

df = spark.read.csv("data/titanic.csv", header=True, inferSchema=True, quote='"', escape='"')


def count_missing(d):
    d.select([F.sum(F.col(c).isNull().cast("int")).alias(c) for c in d.columns]).show()


print("Rows before:", df.count())
print("Missing values before:")
count_missing(df)

# Cleaning
df = df.dropDuplicates()
df = df.drop("Cabin")
median_age = df.approxQuantile("Age", [0.5], 0.01)[0]
df = df.fillna({"Age": median_age, "Embarked": "S"})
df = df.withColumn("Name", F.trim(F.col("Name")))
df = df.toDF(*[c.lower() for c in df.columns])

print("Rows after:", df.count())
print("Missing values after:")
count_missing(df)
df.show(5, truncate=False)

# Data quality checks: stop the pipeline if the data looks wrong
total = df.count()
checks = {
    "rows exist": total > 0,
    "no duplicate passenger ids": df.select("passengerid").distinct().count() == total,
    "survived is only 0 or 1": df.filter(~F.col("survived").isin(0, 1)).count() == 0,
    "pclass is 1, 2 or 3": df.filter(~F.col("pclass").isin(1, 2, 3)).count() == 0,
    "age is between 0 and 100": df.filter((F.col("age") < 0) | (F.col("age") > 100)).count() == 0,
    "fare is not negative": df.filter(F.col("fare") < 0).count() == 0,
    "no missing ages": df.filter(F.col("age").isNull()).count() == 0,
}
for name, ok in checks.items():
    print(("PASS: " if ok else "FAIL: ") + name)
if not all(checks.values()):
    spark.stop()
    raise SystemExit("Data quality checks failed, nothing was saved")

# Save as Parquet (Windows cannot use Spark's writer without winutils, so use pandas there)
if os.name == "nt":
    os.makedirs("output/clean", exist_ok=True)
    df.toPandas().to_parquet("output/clean/clean.parquet", index=False)
else:
    df.write.mode("overwrite").parquet("output/clean")

spark.stop()