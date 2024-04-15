FROM python:slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base as bot
COPY bot.py .
COPY config.py .
CMD python bot.py

FROM base as puller
COPY puller.py .
COPY config.py .
CMD python puller.py