FROM python:3.9 as base
ARG PIPENV_DEV

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmemcached-dev \
    libpq-dev

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN if [ -z "$PIPENV_DEV" ] ; then PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy ; else PIPENV_VENV_IN_PROJECT=1 pipenv install --dev ; fi

FROM base AS runtime
LABEL maintainer="dan@risenutrition.org"

COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

WORKDIR /src

COPY . .
COPY scripts/entrypoint.sh entrypoint.sh
COPY scripts/release.sh release.sh

EXPOSE 8000

ENTRYPOINT ["/src/entrypoint.sh"]
CMD ["gunicorn", "-c", "api/config/gunicorn.py", "api.config.wsgi:application"]
