FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi==0.110.0 \
    uvicorn==0.29.0 \
    pydantic==2.6.4 \
    pandas==2.2.1 \
    numpy==1.26.4 \
    scikit-learn>=1.4.0 \
    xgboost==2.0.3 \
    --timeout 300 \
    --retries 5

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]