FROM python:3.9-bullseye
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get upgrade -y && apt-get install -y gdal-bin
EXPOSE 8000
WORKDIR /code 
COPY requirements.txt /code
RUN pip3 install -r requirements.txt --no-cache-dir
CMD ["/code/run.sh"]
