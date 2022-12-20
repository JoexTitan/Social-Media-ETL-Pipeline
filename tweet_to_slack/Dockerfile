FROM python:3.8-slim
WORKDIR /app3
ADD . /app3
RUN pip install --trusted-host pypi.python.org -r requirements.txt
CMD ["python", "tweet_to_slack.py"]
