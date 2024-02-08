
from pyspark.sql import SparkSession
import os


PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_URL = os.environ["DATABASE_URL"] if ("DATABASE_URL" in os.environ) else "localhost"

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
    .option("dbtable", "(SELECT * FROM shop.orders) as allOrders") \
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

products=[]
statistics=[]

products = [row['id'] for row in products_data_frame.select('id').collect()]
sold=[0 for _ in range(len(products))]
waiting=[0 for _ in range(len(products))]

# for row in products_data_frame.collect():
#     products.append(row[0])
#     sold.append(0)
#     waiting.append(0)

for row in orders_data_frame.collect():
    listOfProducts=[int(x) for x in row[1].split("|")]
    listofQuantities=[int (x) for x in row[2].split("|")]
    for (product, quantity) in zip(listOfProducts, listofQuantities):
        if (row[6] == "COMPLETE"):
            sold[products.index(product)]+=quantity
        else:
            waiting[products.index(product)]+=quantity
for productId in products:
    i=products.index(productId)
    filteredProduct=products_data_frame[products_data_frame["id"] == productId].collect()[0]
    productName=filteredProduct[1]
    statistics.append({"name": productName,"sold":sold[i],"waiting":waiting[i]})

output={"statistics":statistics}
print(output)

spark.stop()