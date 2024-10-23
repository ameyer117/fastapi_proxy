# Google Cloud Run doesn't support ARM64 so be careful if you deploy via a M1/M2/M3 etc. Mac
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8080

CMD ["python", "main.py"]