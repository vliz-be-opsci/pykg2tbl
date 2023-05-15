FROM python:3.8-buster

COPY ./ /pykg2tbl
WORKDIR /pykg2tbl

RUN python -m pip install --upgrade pip && \
    pip install poetry && \
    poetry install

ENTRYPOINT ["pykg2tbl"]
