#TODO
- SqlAlchemy - sql queries
- Redis
- Blockchain
# ShopApp
> System is not finished!
> 
> ShopApp is a system of web applications made in Python, designed to manage accounts and shops for a web store.
# Technologies and Libraries
> More details about versions you can find in requirements.txt.
> To install them use ``` pip install requirements.txt```
- Flask
- SQLAlchemy
- Docker
- Spark
- Etherium Blockchain
# Flask
- Framework is used for accounts, owner, customer and courier applications.
# SQLAlchemy
- Used for creating, managing and retrieving data from MySQL database.
# Docker
> More details you can find in deployment.yaml
- Created system with Docker compose.
- System have 2 parts, one for managing accounts and one for managing shop.
- Each system is comprised of three Docker images:
  - MySQL for database
  - Image for database migrations
  - Image for applications
- The systems are separeted into different networks, making it impossible to access the databases from the outsidee.
- Docker volumes are used for data backup.
# Spark
- Statistics are generated using a Docker Image template found on [Big Data Europe GitHub](https://github.com/big-data-europe/docker-spark).
- The spark cluster reads data from the database and generates the required statistics. A Spark Master server is also available.
- Containers of Spark clusters are integrated into the system for managing the shop.
# System Variables
For Spark image:
```
HADOOP HOME : C:\hadoop\bin\winutils.exe
JAVA_HOME: C:\Program Files\jdk...
```
For python applications that are using pyspark:
```
PYSPARK_DRIVER_PYTHON=jupyter;
PYSPARK_DRIVER_PYTHON_ARGS=notebook;
PYSPARK_PYTHON=python;
PYTHONUNBUFFERED=1
```
# Flask Migrate
>For local tests
```
python applications/manage.py db init
python applications/manage.py db migrate -m "Text Message"
python applications/manage.py db upgrade
```
