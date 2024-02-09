FROM python:3

RUN mkdir -p /opt/src/manageAccounts
WORKDIR /opt/src/manageAccounts

COPY accounts/application.py ./application.py
COPY accounts/configuration.py ./configuration.py
COPY accounts/model.py ./model.py
COPY accounts/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/manageAccounts"

ENTRYPOINT ["python","./application.py"]