# Django Project Template

I've written dozens of Django applications through the years, and I always find myself starting from
square zero again, which can get annoying and tedious. This provides a nice project structure that
can be used to bootstrap a production-ready application.

It is written using [Python Django][django] and [Django REST Framework][drf] for web request handling,
and [Celery][celery] for asynchronous task management. The components are wrapped in
[Docker containers][docker-overview] to ensure that they can be deployed across multiple environments
in a scalable fashion and for easy local development testing.

## Local Development

### Running Commands

You should be able to start using `manage.py` commands to control your local environment. The
two most useful features to ensure things are setup are `lint` and `test`.

```console
./manage.py lint --fix
```

```console
# Add `-- -k SomeTestCaseToRun` for filtering a test class
./manage.py test
```

### Using Docker Compose

The first time running the project in `docker-compose`, you will need to create a image
reference for `api` that will be referenced throughout the rest of the project.

```console
docker-compose build
```

You can start a full local environment using [`docker-compose`][docker-overview]. This will make the
application available at [`127.0.0.1:8000`](http://127.0.0.1:8000), as well as spin up the following
containers similar to how they would work in a real deployment environment:

- Web application (already mentioned)
- Celery task worker
- Celery task scheduler
- PostgreSQL Database
- Redis Cache for Celery queues
- A superuser to log into the admin dashboard

```console
docker-compose up --build --remove-orphans
```

[celery]: https://docs.celeryproject.org/en/stable/
[django]: https://www.djangoproject.com/
[drf]: https://www.django-rest-framework.org/
[docker-overview]: https://docs.docker.com/get-started/overview/