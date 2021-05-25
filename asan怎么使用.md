# asan 怎么使用



## 编译

编译的时候加上 CC="ccache gcc -fsanitize=address"，同时CFLAGS加上 -g -O1 -fno-omit-frame-pointer -fno-inline的选项，这样才能得到更好的调用栈信息。

可以参考这里： https://github.com/openresty/openresty-packaging/blob/master/rpm/SPECS/openresty-asan.spec#L101



## 运行

### 屏蔽内存泄露

ASAN_OPTIONS=detect_leaks=0 ./sbin/nginx -t

因为像nginx -t就是有内存泄露，但是我们不希望他失败，可以加上不检查内存泄露的选项。



### 输出错误信息到指定文件

mkdir -p /var/asan; chmod a+w /var/asan
ASAN_OPTIONS=log_path=/var/asan/asan,log_exe_name=true ./sbin/nginx

