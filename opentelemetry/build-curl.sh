#!/bin/bash

./configure --without-librtmp --without-nghttp3 --without-ngtcp2 --without-libidn2 --without-brotli --prefix=/usr/local/openresty-curl/ --with-openssl=/usr/local/openresty/openssl111

make
sudo make install
