#!/bin/bash

#git clone --shallow-submodules --depth 1 --recurse-submodules -b v1.3.0 https://github.com/open-telemetry/opentelemetry-cpp.git && cd opentelemetry-cpp
rm -fr build
mkdir build
cd build

cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local/openresty-opentelemetry -DCMAKE_PREFIX_PATH="/usr/local/openresty-grpc;/usr/local/openresty-curl" -DWITH_OTLP=ON -DWITH_OTLP_GRPC=ON -DWITH_OTLP_HTTP=OFF -DBUILD_TESTING=OFF -DWITH_EXAMPLES=OFF -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DBUILD_SHARED_LIBS=OFF  -DWITH_ABSEIL=ON ..

#cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local/openresty-opentelemetry -DCMAKE_PREFIX_PATH=/usr/local/openresty-grpc -DWITH_OTLP=ON -DWITH_OTLP_GRPC=ON -DWITH_OTLP_HTTP=OFF -DBUILD_TESTING=OFF -DWITH_EXAMPLES=OFF -DCMAKE_POSITION_INDEPENDENT_CODE=ON -DWITH_ABSEIL=ON ..

make -j4
sudo make install
