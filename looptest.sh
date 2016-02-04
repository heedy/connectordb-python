#!/bin/bash
# This file is good to use when profiling connectordb CRUD. It runs the tests in a loop,
# so that good profiling data can be gained.
while [ 1 ]
do
    nosetests connectordb_test.py
done