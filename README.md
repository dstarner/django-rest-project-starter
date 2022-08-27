# Project

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