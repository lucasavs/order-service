FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt
COPY ./app /app

RUN pip3 install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]