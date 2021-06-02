# 编译openresty的rpm包

## 下载openresty的tar包

``` shell
wget -O openresty-1.19.3.1.tar.gz  https://openresty.org/download/openresty-1.19.3.1.tar.gz
mv openresty-1.19.3.1.tar.gz ~/rpmbuild/SOURCES
```

这个tar包是通过这个脚本生成的 https://github.com/openresty/openresty/blob/master/util/mirror-tarballs



## 下载打包脚本

``` shell
git clone  git@github.com:openresty/openresty-packaging.git
cd openresty-packaging
cp rpm/SOURCES/* ~/rpmbuild/SOURCES
rpmbuild -bb rpm/SPECS/openresty.spec
```



## 如何增加自己的模块

一个很简单的方法就是在修改mirror-tarballs，然后将模块加入openresty-1.19.3.1.tar.gz， 在openresty.spec的文件中增加--add-module指定要添加的模块。