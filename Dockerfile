FROM python:3.8.5

ARG USER_ID
ARG GROUP_ID

# Avoid file permission issues for container user files that are written to host volume.
RUN addgroup --gid $GROUP_ID user
RUN adduser --disabled-password --gecos '' --uid $USER_ID --gid $GROUP_ID user
USER user

EXPOSE 8000

RUN mkdir -p /home/user/.pytest/cache

ENV VIRTUAL_ENV=/home/user/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV PYTEST_ADDOPTS="--color=yes"
# Creds for aws 
ENV AWS_CONFIG_FILE=/home/user/.aws/config
# This is so we wipe the file on every container run.
ENV TESTMON_DATAFILE=/home/user/.testmondata

WORKDIR /home/user/app

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["chalice", "local", "--host", "0.0.0.0", "--port", "80"]
