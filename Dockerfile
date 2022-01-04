FROM python:3.8-buster

COPY ./ /pykg2tbl
WORKDIR /pykg2tbl

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    python setup.py install

ENTRYPOINT ["pykg2tbl"]
