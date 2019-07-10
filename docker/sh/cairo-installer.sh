#!/usr/bin/env bash
set -e

apt-get update

apt-get install gettext -y

git clone https://gitlab.freedesktop.org/cairo/cairo.git --depth 1 --branch 1.15.10
cd cairo
./autogen.sh
./configure --prefix=/usr/local

make
make install

# This command updates all the symbolic links (apt libraries links)
ldconfig