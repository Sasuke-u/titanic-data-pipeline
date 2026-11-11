from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("titanic-clean").master("local[*]").getOrCreate()

df = spark.read.csv("data/titanic.csv", header=True, inferSchema=True, quote='"', escape='"')

def count_missing(d):
    d.select([F.sum(F.col(c).isNull().cast("int")).alias(c) for c in d.columns]).show()

print("Rows before:", df.count())
print("Missing values before:")
count_missing(df)

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
import os
if os.name == "nt":
    os.makedirs("output/clean", exist_ok=True)
    df.toPandas().to_parquet("output/clean/clean.parquet", index=False)
else:
    df.write.mode("overwrite").parquet("output/clean")
spark.stop()