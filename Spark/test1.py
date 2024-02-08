from pyspark.sql import SparkSession

import os

PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_IP = os.environ["DATABASE_IP"] if ("DATABASE_IP" in os.environ) else "localhost"

builder = SparkSession.builder.appName("PySpark Database example")

if (not PRODUCTION):
    builder = builder.master("local[*]") \
        .config(
        "spark.driver.extraClassPath",
        "mysql-connector-j-8.0.33.jar"
    )

spark = builder.getOrCreate()

products_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://shopDB:3307/shop") \
    .option("dbtable", "shop.products") \
    .option("user", "root") \
    .option("password", "root") \
    .load()
#?enabledTLSProtocols=TLSv1.2


# people_data_frame.show ( )
# result = people_data_frame.filter ( people_data_frame["gender"] == "Male" ).collect ( )
# print ( result )
print("**************")
print(products_data_frame)
print("**************")
spark.stop()