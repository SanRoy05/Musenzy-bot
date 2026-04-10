FROM nikolaik/python-nodejs:python3.11-nodejs20

USER root

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /tmp/musenzy /app/data

CMD ["python", "-u", "bot.py"]
