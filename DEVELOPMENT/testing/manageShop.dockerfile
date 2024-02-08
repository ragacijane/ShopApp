FROM python:3

RUN mkdir -p /opt/src/manageShop
WORKDIR /opt/src/manageShop

COPY manageShop/application.py ./application.py
COPY manageShop/configuration.py ./configuration.py
COPY manageShop/model.py ./model.py
COPY manageShop/roleDecorator.py ./roleDecorator.py
COPY manageShop/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/manageShop"

ENTRYPOINT ["python","./application.py"]