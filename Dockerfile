FROM python:slim

COPY requirements.txt .
COPY bot.py .
COPY config.py .
COPY puller.py .

RUN pip install -r ./requirements.txt

CMD python puller.py && python bot.py;
