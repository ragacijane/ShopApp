
from pyspark.sql import SparkSession
import os


PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_URL = os.environ["DATABASE_URL"] if ("DATABASE_URL" in os.environ) else "localhost"
DATABASE_NAME = "shopDB"
builder = SparkSession.builder.appName("PySpark Database example")

if (not PRODUCTION):
    builder = builder.master("local[*]") \
        .config(
        "spark.driver.extraClassPath",
        "mysql-connector-j-8.0.33.jar"
    )

spark = builder.getOrCreate()

orders_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_URL}:3306/shop") \
    .option("dbtable", "(SELECT * FROM shop.orders WHERE shop.orders.status = 'COMPLETE') as allOrders") \
    .option("user", "root") \
    .option("password", "root") \
    .load()
products_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_URL}:3306/shop") \
    .option("dbtable", "(SELECT * FROM shop.products) as allProducts") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

sold = []
statistics = []

for row in products_data_frame.collect():
    listOfCategories = row[2].split("|")
    for category in listOfCategories:
        if category not in statistics:
            statistics.append(category)
            sold.append(0)
for row in orders_data_frame.collect():
    listOfProducts = [int(x) for x in row[1].split("|")]
    listofQuantities = [int(x) for x in row[2].split("|")]
    for (product, quantity) in zip(listOfProducts, listofQuantities):
        filteredCategproes = products_data_frame[products_data_frame["id"] == product].collect()[0]
        categories = filteredCategproes[2].split("|")
        for category in categories:
            sold[statistics.index(category)]+=quantity
stats=dict(zip(statistics,sold))
sortedStats=dict(sorted(stats.items(),key=lambda item: (-item[1], item[0])))
statistics=list(sortedStats.keys())

output={"statistics": statistics}
print(output)
spark.stop()