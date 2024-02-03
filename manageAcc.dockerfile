FROM python:3

RUN mkdir -p /opt/src/manageAccounts
WORKDIR /opt/src/manageAccounts

COPY manageAccounts/application.py ./application.py
COPY manageAccounts/configuration.py ./configuration.py
COPY manageAccounts/model.py ./model.py
COPY manageAccounts/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/manageAccounts"

ENTRYPOINT ["python","./application.py"]