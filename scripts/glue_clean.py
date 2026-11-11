from pyspark.sql import SparkSession, functions as F

BUCKET = "santhosh-titanic-pipeline-4827"

spark = SparkSession.builder.appName("titanic-glue-clean").getOrCreate()

df = spark.read.csv(f"s3://{BUCKET}/raw/titanic.csv",
                    header=True, inferSchema=True, quote='"', escape='"')

df = df.dropDuplicates()
df = df.drop("Cabin")
median_age = df.approxQuantile("Age", [0.5], 0.01)[0]
df = df.fillna({"Age": median_age, "Embarked": "S"})
df = df.withColumn("Name", F.trim(F.col("Name")))
df = df.toDF(*[c.lower() for c in df.columns])

print("Rows after cleaning:", df.count())

df.write.mode("overwrite").parquet(f"s3://{BUCKET}/clean_glue/")

spark.stop()