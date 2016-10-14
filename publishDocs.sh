#!/usr/bin/env bash

echo 'hello'

cd docs
make clean
make html
cd ..

git add -A
git commit -m "Building and publishing docs"
git push origin master