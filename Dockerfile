FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /app/

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade --timeout=10000 -r /app/requirements.txt

COPY ./ .

ENV PYTHONPATH=/app

EXPOSE 80

ENTRYPOINT [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80" ]