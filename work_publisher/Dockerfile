FROM python:3.8-slim

WORKDIR /redis

COPY ../requirements.txt .
RUN pip install -r requirements.txt

COPY ../* .
CMD ["python", "./work_publisher.py"]