FROM python:3.14-slim

WORKDIR /crypto-alert-engine

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

CMD ["python", "main.py"]
CMD ["python", "main.py"]