#!/bin/bash


#git clone --shallow-submodules --depth 1 --recurse-submodules -b v1.36.4 https://github.com/grpc/grpc && cd grpc

rm -fr cmake/build
mkdir -p cmake/build
cd cmake/build
cmake -DgRPC_INSTALL=ON -DgRPC_BUILD_TESTS=OFF -DCMAKE_INSTALL_PREFIX=/usr/local/openresty-grpc -DCMAKE_BUILD_TYPE=Release -DgRPC_BUILD_GRPC_NODE_PLUGIN=OFF -DgRPC_BUILD_GRPC_OBJECTIVE_C_PLUGIN=OFF -DgRPC_BUILD_GRPC_PHP_PLUGIN=OFF -DgRPC_BUILD_GRPC_PHP_PLUGIN=OFF     -DgRPC_BUILD_GRPC_PYTHON_PLUGIN=OFF -DgRPC_BUILD_GRPC_RUBY_PLUGIN=OFF -DCMAKE_PREFIX_PATH="/usr/local/openresty/zlib;/usr/local/openresty/openssl111" -DgRPC_SSL_PROVIDER=package -DgRPC_ZLIB_PROVIDER=package ../..

make -j4
sudo make install

