from pyspark.sql import SparkSession
from pyspark.sql.functions import array, explode, struct, lit, col, split, size
from pyspark.sql.functions import sum as spark_sum

spark = SparkSession.builder.appName("TwitterStatistics").getOrCreate()

df = spark.read.text("s3://twitter-user-statistics-varnikaa/input/twitter_combined.txt")


df = df.withColumn("tokens", split(col("value"), r"\s+"))

edges = df.filter(size(col("tokens")) >= 2).select(
    col("tokens").getItem(0).alias("A"),
    col("tokens").getItem(1).alias("B")
).filter("A is not null and B is not null and A != '' and B != ''").dropDuplicates(["A", "B"])

contributions = edges.select(
    explode(
        array(
            struct(col("A").alias("UserID"), lit(0).alias("Followers"), lit(1).alias("Followees")),
            struct(col("B").alias("UserID"), lit(1).alias("Followers"), lit(0).alias("Followees"))
        )
    ).alias("record")
)

result = contributions.select("record.*")
user_stats = result.groupBy("UserID").agg(
    spark_sum("Followers").alias("Followers"),
    spark_sum("Followees").alias("Followees")
)

user_stats.coalesce(1).write.mode("overwrite").option("header", True).csv("s3://twitter-user-statistics-varnikaa/output/user_statistics/")

spark.stop()