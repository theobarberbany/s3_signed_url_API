FROM python:3.6.5-jessie

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt 
RUN apt-get update && apt-get install -y jq \
    curl

COPY . .
EXPOSE 8000
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
