FROM python:3.6

COPY requirements.txt .
RUN pip3.6 install -r ./requirements.txt --use-feature=2020-resolver

