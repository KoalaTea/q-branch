FROM python:3.7-alpine

RUN mkdir /q-branch
WORKDIR /q-branch
COPY . /q-branch
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "-u", "/q-branch/qbot.py" ]
