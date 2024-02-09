FROM python:3

RUN mkdir -p /opt/src/shop
WORKDIR /opt/src/shop

COPY shop/migrate.py ./migrate.py
COPY shop/configuration.py ./configuration.py
COPY shop/model.py ./model.py
COPY shop/requirementsMigration.txt ./requirementsMigration.txt

RUN pip install -r ./requirementsMigration.txt


ENTRYPOINT ["python","./migrate.py"]