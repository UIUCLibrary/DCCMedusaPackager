#!/usr/bin/env bash

echo 'hello'

cd docs
make clean
make html
cd ..

git add docs/build/html
git commit -m "Building and publishing docs"
git push origin master

git checkout gh-pages
rm -rf .
touch .nojekyll
git checkout master docs/build/html
mv ./docs/build/html/* ./
rm -rf ./docs
git add -A
git commit -m "publishing updated docs..."
git push origin gh-pages
# switch back
git checkout master
