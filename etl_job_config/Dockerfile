FROM python:3.8-slim
WORKDIR /app2
ADD . /app2
RUN pip install --trusted-host pypi.python.org -r requirements.txt
CMD ["python", "scheduler.py"]
