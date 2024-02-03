FROM python:3

RUN mkdir -p /opt/src/manageShop
WORKDIR /opt/src/manageShop

COPY manageShop/migrate.py ./migrate.py
COPY manageShop/configuration.py ./configuration.py
COPY manageShop/model.py ./model.py
COPY manageShop/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt


ENTRYPOINT ["python","./migrate.py"]