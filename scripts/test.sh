#!/bin/bash
set -e

./manage.py lint
./manage.py test