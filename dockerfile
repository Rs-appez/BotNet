FROM python:3.12-slim

ENV TZ="Europe/Brussels"

WORKDIR /botNet
COPY requirements.txt /botNet/
RUN pip install -r requirements.txt
COPY . /botNet/

CMD ["python3", "botNet.py"]
