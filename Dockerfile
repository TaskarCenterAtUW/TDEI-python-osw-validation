FROM python:3.10
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# RUN pip install git+https://github.com/TaskarCenterAtUW/TDEI-python-ms-core@8c5e11e5e5560ac6853416f47507ee4c94992de4
COPY ./src /code/src
EXPOSE 8080
CMD ["uvicorn", "src.main:app","--host", "0.0.0.0", "--port", "8080"]
