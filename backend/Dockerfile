FROM python:3.11-slim

WORKDIR /code

# Install required system packages for psycopg2 and GeoAlchemy
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app
COPY ./datasets /code/datasets
COPY ./scripts /code/scripts

# Command to run the Fastapi application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
