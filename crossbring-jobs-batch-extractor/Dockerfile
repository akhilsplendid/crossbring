FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY extractor.py .
ENV MODE=direct TOPIC_OUT=jobmodel.stg_jobs BATCH_WINDOW_MINUTES=15
CMD ["python","/app/extractor.py"]

