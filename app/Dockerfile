FROM python:3.10

RUN apt update -y
RUN apt upgrade -y

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./ ./

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]