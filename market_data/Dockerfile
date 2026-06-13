FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY market_data ./market_data
COPY common ./common

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "market_data.main:app", "--host", "0.0.0.0", "--port", "8000"]
