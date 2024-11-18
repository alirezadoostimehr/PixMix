FROM hub.hamdocker.ir/python:3.12
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --trusted-host https://mirror-pypi.runflare.com -i https://mirror-pypi.runflare.com/simple/ --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install --trusted-host https://mirror-pypi.runflare.com -i https://mirror-pypi.runflare.com/simple/ pillow
COPY ./ /code/
CMD ["python", "app/main.py", "serve"]
