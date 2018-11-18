#!/usr/bin/env bash

set -e

cd ..
git clone -b gh-pages "https://$GH_TOKEN@github.com/lhofmann/pvxmlgen.git" gh-pages
cd gh-pages

git config user.name "Travis Builder"
git config user.email "lhofmann@users.noreply.github.com"

cp -R ../pvxmlgen/docs/build/html/* ./

git add -A .
git commit -m "[ci skip] Autodoc commit for $TRAVIS_COMMIT."
git push -q origin gh-pages
