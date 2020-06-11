ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION} as wheel_builder

ADD requirements.txt requirements-dev.txt  /tmp/
ARG PYTHON_INDEX=https://devpi.library.illinois.edu/production/release
RUN python -m pip install --upgrade pip &&  \
    pip install setuptools && \
    pip install wheel
RUN pip wheel --wheel-dir=/wheels -r /tmp/requirements.txt -r /tmp/requirements-dev.txt -i ${PYTHON_INDEX} -v

FROM python:${PYTHON_VERSION}
ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user -g user user

COPY --from=wheel_builder /wheels /wheels/
ADD requirements.txt requirements-dev.txt  /tmp/
ENV PIP_EXTRA_INDEX_URL="${PYTHON_INDEX}"
ENV PIP_TRUSTED_HOST="devpi.library.illinois.edu"
ENV PIP_FIND_LINKS=/wheels

RUN pip install --no-index --find-links=/wheels \
    -r /tmp/requirements.txt \
    -r /tmp/requirements-dev.txt

USER user
WORKDIR /home/user