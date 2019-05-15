#!/bin/bash
set -e
PYTHON_CMD="python3"
USAGE="Usage: buildandcopy [--manual] [--dry] [--skip-wp] [--help]"

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
        "--help")
        echo "$USAGE"
        exit 0
        ;;
    esac
done

# Check environment is set correctly
if ! [[ -z "$DISABLE_COLLECTSTATIC" ]]; then
    echo "Collectstatic disabled"
    exit 0
fi

if [[ -z $ASSET_PATH ]]; then
    echo "ASSET_PATH must be set"
    exit 1
fi

if [[ -z $STORAGE_BUCKET_NAME ]]; then
    echo "STORAGE_BUCKET_NAME must be set"
    exit 1
fi

if ! [[ "$PWD" =~ .*aristotle-metadata-registry$ ]]; then
    echo "Must be run from root of repo"
    exit 1
fi

# If running on travis check if this needs to be run
if [[ "$TRAVIS" == "true" ]] && [[ "$TRAVIS_BRANCH" != "master" || "$TRAVIS_PULL_REQUEST" != "false" ]]; then
    echo "Not on correct branch. skipping..."
    exit 0
fi

# Message if not custom static bucket
if [[ -z "$CUSTOM_STATIC_BUCKET_NAME" ]]; then
    echo "No custom static buckets, building without"
fi

mkdir -p ./python/aristotle-metadata-registry/aristotle_mdr/manifests

cd assets
if [[ $SKIP_WEBPACK_BUILD -ne 1 ]]; then
    echo "Running webpack build..."
    # Remove stats if it exists
    rm -f ./dist/webpack-stats.json
    # Fetch custom static
    if [[ ! -z "$CUSTOM_STATIC_BUCKET_NAME" ]]; then
        aws s3 cp s3://$CUSTOM_STATIC_BUCKET_NAME/static ./src/custom --recursive
    fi
    npm install
    # Export asset path to be used by build
    export ASSET_PATH="$ASSET_PATH"
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
    # Check manual bucket set
    if [[ -z $MANUAL_BUCKET ]]; then
        echo "MANUAL_BUCKET not set"
        exit 1
    fi
    # Clean dist if exists
    if [[ -e ./dist ]];then
        rm -r ./dist
    fi
    # Run setup
    $PYTHON_CMD setup.py bdist_wheel
    # Push to s3
    if [[ $DRY -eq 1 ]]; then
        aws s3 cp ./dist $MANUAL_BUCKET --recursive --acl public-read --dry
    else
        aws s3 cp ./dist $MANUAL_BUCKET --recursive --acl public-read
    fi
fi

echo "Done!"
exit 0
