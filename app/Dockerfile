FROM python:latest

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip --version
RUN python --version

ENTRYPOINT [ "python3", "-m", "src.scripts.load" ]