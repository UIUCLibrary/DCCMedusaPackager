# escape=`
ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION} as certsgen
RUN certutil -generateSSTFromWU roots.sst

FROM python:${PYTHON_VERSION} as wheel_builder

RUN python -m pip install pip --upgrade; `
    pip install setuptools --upgrade ; `
    pip install wheel ; `
    pip wheel --wheel-dir=c:/wheels cx_freeze
ADD requirements.txt requirements-dev.txt requirements-freeze.txt c:/temp/
ARG PYTHON_INDEX=https://devpi.library.illinois.edu/production/release
RUN pip wheel --wheel-dir=c:/wheels -r c:/temp/requirements.txt -r c:/temp/requirements-dev.txt -r c:/temp/requirements-freeze.txt -i ${ENV:PYTHON_INDEX} -v

FROM python:${PYTHON_VERSION}
COPY --from=certsgen c:/roots.sst roots.sst
RUN certutil -addstore -f root roots.sst ; `
    del roots.sst

RUN python -m pip install pip --upgrade ; `
    pip install setuptools --upgrade


ENV PIP_EXTRA_INDEX_URL="https://devpi.library.illinois.edu/production/release"
ENV PIP_TRUSTED_HOST="devpi.library.illinois.edu"

COPY --from=wheel_builder c:/wheels/ c:/wheels/
ADD requirements.txt requirements-dev.txt requirements-freeze.txt c:/temp/
RUN pip install --no-index --find-links=c:/wheels `
    -r c:\temp\requirements.txt
    -r c:\temp\requirements-dev.txt
    -r c:\temp\requirements-freeze.txt