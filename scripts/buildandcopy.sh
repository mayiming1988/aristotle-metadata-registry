#!/bin/bash
set -e

if ! [[ "$PWD" = *aristotle-metadata-registry ]]; then
    echo "Must be run from root of repo"
    exit 1
fi

if [[ -z "$STORAGE_BUCKET_NAME" ]]; then
    echo "STORAGE_BUCKET_NAME environment variable must be set"
    exit 1
fi

mkdir ./python/aristotle-metadata-registry/manifests

cd assets
echo "Running webpack build..."
# Remove stats if it exists
rm -f ./dist/webpack-stats.json
npm run build
echo "Webpack build complete!"
cd ..

echo "Installing dependancies..."
pipenv install --dev
export PYTHONPATH=./docker
export DATABASE_URL=sqlite://:memory:
export DJANGO_SETTINGS_MODULE=settings
echo "Collecting static..."
pipenv run django-admin collectstatic --no-input

cp ./assets/dist/webpack-stats.json ./python/aristotle-metadata-registry/manifests
echo "Done!"
