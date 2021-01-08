FROM python:3-alpine

LABEL maintainer="w.fantom@lancaster.ac.uk"

RUN pip install flask pyxs

WORKDIR /app
COPY ./ .
RUN python setup.py install

ENTRYPOINT [ "unimon-ctl" ]