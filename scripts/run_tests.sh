#!/bin/bash -x

export PYTHONUNBUFFERED=1
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR=$(dirname "$BASE_DIR")

./manage.py wait_for_resources --db

if [ "$CI" == "true" ]; then
    pip3 install coverage pytest-xdist

    set -e

    # To show migration logs
    ./manage.py test --keepdb -v 2 gaatha.tests
    pytest -ra --reuse-db -v --durations=10

    set +e
else
    py.test
fi
