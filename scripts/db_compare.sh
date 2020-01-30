#!/usr/bin/env bash
set -e
about="Compare the database schema for aristotle from 2 different git branches"
usage="Usage: $0 oldbranch newbranch"
helptext="${about}\n\n${usage}"

if [[ -z "$1" || -z "$2" || "$1" == "--help" ]]; then
    echo -e "$helptext"
    exit 0
fi

# Get top of repo
top="$(git rev-parse --show-toplevel)"

# Set variables
outputdir="$top"
branch_old="$1"
branch_new="$2"
# Get database names from branch names
# Add prefix since name must start with letter
# Replace various symbols with '_' since they are not allowed in db names
dbname_prefix="compare_"
translate_chars="/.,-"
dbname_old=${dbname_prefix}$(echo "$1" | tr "$translate_chars" '_')
dbname_new=${dbname_prefix}$(echo "$2" | tr "$translate_chars" '_')

# Get output filenames
fname_old="${outputdir}/${dbname_old}.sql"
fname_new="${outputdir}/${dbname_new}.sql"

# Start database
cd "${top}/docker"
if [[ "$(docker-compose ps -q)" ]]; then
    echo "Taking down"
    docker-compose down
fi
docker-compose up --detach --no-deps db

# Checkout to branch and create database from it
# Argument 1: Name of branch
# Argument 2: Name of database
backup_from_branch() {
    # Checkout to branch
    echo "Checking out to branch $1"
    git checkout $1
    # Clean database
    echo "Dropping database $2"
    docker-compose exec db psql \
        --user postgres \
        -c "DROP DATABASE IF EXISTS $2"
    echo "Creating database $2"
    docker-compose exec db psql \
        --user postgres \
        -c "CREATE DATABASE $2"
    # Migrate into database with name of branch
    echo "Migrating database $2"
    docker-compose run \
        --no-deps \
        -e DATABASE_URL="postgresql://postgres:@db:5432/$2" \
        web \
        sh -c "pip install pypandoc && django-admin migrate"
}

# Dump database schema to sql commands
# Output is passed through sql sort
# Argument 1: Name of database
# Argument 2: Path to file for output
dump_database() {
    echo "Dumping database $1 to file $2"
    docker-compose exec db pg_dump \
        --schema-only \
        --no-owner \
        --no-privileges \
        --user postgres \
        $1 | python3 "${top}/scripts/sqlsort.py" > $2
}

# Backup from each branch
backup_from_branch $branch_old $dbname_old
backup_from_branch $branch_new $dbname_new

# pg_dump from each database
dump_database $dbname_old $fname_old
dump_database $dbname_new $fname_new

# Diff 2 sql files
diff_fname="${top}/comparison.diff"
diff_args="--strip-trailing-cr --unified $fname_old $fname_new"

echo "Writing diff to $diff_fname"
diff $diff_args > $diff_fname


docker-compose down
echo "Done!"
