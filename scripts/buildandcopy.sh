#!/bin/bash
set -e

if ! [[ -z "$DISABLE_COLLECTSTATIC" ]]; then
    echo "Collectstatic disabled"
    exit 0
fi

if ! [[ "$PWD" = *aristotle-metadata-registry ]]; then
    echo "Must be run from root of repo"
    exit 1
fi

if [[ "$TRAVIS" == "true" ]] && [[ "$TRAVIS_BRANCH" != "master" || "$TRAVIS_PULL_REQUEST" != "false" ]]; then
    echo "Not on correct branch. skipping..."
    exit 0
fi

if [[ -z "$STORAGE_BUCKET_NAME" ]]; then
    echo "STORAGE_BUCKET_NAME environment variable must be set"
    exit 1
fi

mkdir -p ./python/aristotle-metadata-registry/manifests

cd assets
echo "Running webpack build..."
# Remove stats if it exists
rm -f ./dist/webpack-stats.json
npm install
npm run build
echo "Webpack build complete!"
cd ..

echo "Installing dependancies..."
pipenv install --dev
export PYTHONPATH=./docker
export DATABASE_URL=sqlite://:memory:
export DJANGO_SETTINGS_MODULE=settings
export NO_LOGGING=1
echo "Collecting static..."
pipenv run django-admin collectstatic --no-input

cp ./assets/dist/webpack-stats.json ./python/aristotle-metadata-registry/aristotle_mdr/manifests
echo "Done!"
