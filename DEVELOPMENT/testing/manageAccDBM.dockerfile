FROM python:3

RUN mkdir -p /opt/src/manageAccounts
WORKDIR /opt/src/manageShop

COPY manageAccounts/migrate.py ./migrate.py
COPY manageAccounts/configuration.py ./configuration.py
COPY manageAccounts/model.py ./model.py
COPY manageAccounts/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt


ENTRYPOINT ["python","./migrate.py"]