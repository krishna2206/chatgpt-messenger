FROM python:3.10.8-bullseye

# Upgrade system
RUN apt-get update && apt-get upgrade -y

# Install required packages
RUN apt-get install -y python3-pip git build-essential

WORKDIR /app/

COPY . /app/

RUN pip install -r ./requirements.txt

CMD uvicorn app:webserver --host 0.0.0.0 --port $PORT