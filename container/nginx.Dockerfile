FROM python:3.11-slim AS python-builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG APP_DIR="/app"

WORKDIR ${APP_DIR}

# install build requirements
RUN apt -y update
RUN apt -y install pkg-config
RUN apt -y install python3-dev
RUN apt -y install build-essential
RUN apt -y install default-libmysqlclient-dev

# install environment
COPY ../requirements.txt ${APP_DIR}
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ../ ${APP_DIR}

# TODO: run npm run build for all npm packages

# collect static files
RUN python manage.py collectstatic --no-input --clear

FROM node:20-slim as node-builder
ARG APP_DIR="/liveticker-app"
WORKDIR ${APP_DIR}

COPY ../liveticker ${APP_DIR}

RUN npm ci
RUN npm run build

FROM nginx:stable

COPY --from=python-builder /app/league_manager/league_manager/static /static
COPY --from=node-builder /liveticker-app/static /static
COPY ./container/nginx.conf /etc/nginx/conf.d/default.conf
