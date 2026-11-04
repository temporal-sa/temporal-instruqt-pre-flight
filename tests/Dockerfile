FROM python:3.12.12-slim
WORKDIR /test
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
COPY tests/ tests/
CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
