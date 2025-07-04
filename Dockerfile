FROM python:3.13.1

WORKDIR /course-app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY course/main.py .
COPY course/models.py .
COPY course.db .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]