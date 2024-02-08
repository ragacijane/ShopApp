FROM python:3

RUN mkdir -p /opt/src/shop
WORKDIR /opt/src/shop

COPY DEVELOPMENT/allPassedNoBc/shop/migrate.py ./migrate.py
COPY DEVELOPMENT/allPassedNoBc/shop/configuration.py ./configuration.py
COPY DEVELOPMENT/allPassedNoBc/shop/model.py ./model.py
COPY DEVELOPMENT/allPassedNoBc/shop/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt


ENTRYPOINT ["python","./migrate.py"]