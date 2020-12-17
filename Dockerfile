# base image: Debian Buster slim with Python 3.9.1
FROM python:3.9.1-slim-buster

# disable pip's cache to reduce image size
ENV PIP_NO_CACHE_DIR=1

# update pip
RUN pip install -U \
    pip \
    setuptools \
    wheel

# change workdir
WORKDIR /usr/src/FritzBoxInflux

# create new non-root user
RUN useradd -m -r user

# install python dependencies
# copy requirements first to not invalidate the cache when updating the python app
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy application data
COPY FritzBoxInflux.py .

# run as `user` instead of root
USER user

# run application
CMD ["python3", "FritzBoxInflux.py"]
