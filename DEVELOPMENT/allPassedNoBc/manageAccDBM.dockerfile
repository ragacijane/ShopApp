FROM python:3

RUN mkdir -p /opt/src/manageAccounts
WORKDIR /opt/src/manageShop

COPY accounts/migrate.py ./migrate.py
COPY accounts/configuration.py ./configuration.py
COPY accounts/model.py ./model.py
COPY accounts/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt


ENTRYPOINT ["python","./migrate.py"]