#!/bin/bash

#cd otel-nginx/build   && cmake -DCMAKE_BUILD_TYPE=Release     -DCMAKE_PREFIX_PATH=/install     -DCMAKE_INSTALL_PREFIX=/usr/share/nginx/modules     ..   && make -j2   && make install

rm -fr build
mkdir build
cd build

cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="/usr/local/openresty-curl;/usr/local/openresty-grpc;/usr/local/openresty-opentelemetry" -DCMAKE_INSTALL_PREFIX=/usr/local/openresty/nginx/modules ..
make -j2
sudo make install

