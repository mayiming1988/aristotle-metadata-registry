#!/usr/bin/env bash
set -ev
# Make a MariaDB database
# Fix weirdness with MariaDB on Travis - https://github.com/mozilla/kitsune/pull/2453/commits/229db28973f00dfc4fa7b386f266caf3417966a0
if [[ $DB == mariadb ]];
then
  ./prep_mysql.sh;
fi

if [[ $SEARCH == elastic ]];
then
  sudo service elasticsearch start && sleep 10;
fi

# Make a postgres database
if [[ $DB == postgres* ]];
then
  ./prep_psql.sh;
fi

cd ./assets
npm install
npm run devbuild
