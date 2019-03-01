#!/bin/bash
set -e
PYTHON_CMD="python3"

# Basic flag arg parsing
MANUAL=0
DRY=0
SKIP_WEBPACK_BUILD=0
for i in $@; do
    case $i in
        "--manual")
        MANUAL=1
        echo "Doing manual deploy"
        ;;
        "--dry")
        DRY=1
        echo "Doing dry run"
        ;;
        "--skip-wp")
        SKIP_WEBPACK_BUILD=1
        ;;
    esac
done


if ! [[ -z "$DISABLE_COLLECTSTATIC" ]]; then
    echo "Collectstatic disabled"
    exit 0
fi

if ! [[ "$PWD" =~ .*aristotle-metadata-registry$ ]]; then
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

if [[ -z "$ASSET_PATH" ]];then 
    echo "ASSET_PATH environment variable must be set"
    exit 1
fi

mkdir -p ./python/aristotle-metadata-registry/aristotle_mdr/manifests

cd assets
if [[ $SKIP_WEBPACK_BUILD -ne 1 ]]; then
    echo "Running webpack build..."
    # Remove stats if it exists
    rm -f ./dist/webpack-stats.json
    npm install
    npm run build
    echo "Webpack build complete!"
fi
cd ..

# If aws command not avaliable
if ! [[ $(command -v aws) ]]; then
    echo "Installing dependancies..."
    pip install awscli
fi

echo "Collecting bundle static..."

if [[ $DRY -eq 1 ]]; then
    aws s3 cp ./assets/dist/bundles s3://$STORAGE_BUCKET_NAME/bundles --recursive --dryrun
else
    aws s3 cp ./assets/dist/bundles s3://$STORAGE_BUCKET_NAME/bundles --recursive
fi

cp ./assets/dist/webpack-stats.json ./python/aristotle-metadata-registry/aristotle_mdr/manifests

if [[ $MANUAL -eq 1 ]]; then
    echo "Doing a manual deploy to s3..."
    rm -r ./dist
    $PYTHON_CMD setup.py bdist_wheel
    if [[ $DRY -eq 1 ]]; then
        aws s3 cp ./dist s3://aristotle-pypi-bucket-1kyswb3cn1pa1 --recursive --dry
    else
        aws s3 cp ./dist s3://aristotle-pypi-bucket-1kyswb3cn1pa1 --recursive 
    fi
fi

echo "Done!"
exit 0
