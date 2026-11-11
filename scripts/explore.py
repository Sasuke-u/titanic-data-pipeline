from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("titanic-explore").master("local[*]").getOrCreate()

df = spark.read.csv("data/titanic.csv", header=True, inferSchema=True)

print("Rows:", df.count())
df.printSchema()
df.show(5, truncate=False)

spark.stop()