FROM python:slim as build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:slim as bot
COPY --from=build /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY bot.py .
COPY config.py .
CMD python bot.py

FROM python:slim as puller
COPY --from=build /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY puller.py .
COPY config.py .
CMD python puller.py