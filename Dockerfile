FROM python:3.11
WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN apt-get update && apt-get install -y sqlite3
RUN pip3 install --no-cache-dir gunicorn && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 4242
CMD ["gunicorn", "--bind", "0.0.0.0:4242", "app.server:app"]
