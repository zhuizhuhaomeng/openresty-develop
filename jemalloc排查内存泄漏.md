经常有客户发现nginx reload导致消耗了很多的内存。如何定位这样的问题呢？

如果使用xray的内存泄漏火焰图，那么hash表的大小会受到限制。虽然可以调整hash表的大小，但是哈希表的大小也不可能调整得太大。



可以使用jemalloc的内存分析工具来实现，注意编译jemalloc的时候需要 加上--enable-prof 

比如

```
./configure --enable-prof --enable-prof-libunwind。
```



nginx中我们可以通过在init_by_lua 中直接调用prof.dump来实现每次reload就dump一次内存。

nginx.conf 添加如下配置

```c
    init_by_lua_block {
        local ffi = require "ffi"
        local C = ffi.C

        ffi.cdef[[
          int mallctl(	const char *name,
           	void *oldp,
           	size_t *oldlenp,
           	void *newp,
           	size_t newlen);
        ]]

        C.mallctl("prof.dump", NULL, NULL, NULL, 0)
    }
```



启动nginx命令如下：

export MALLOC_CONF=prof:true

LD_PRELOAD=/usr/local/lib/libjemalloc.so.2 ./sbin/nginx -s reload



分析内存的时候可以通过比较前后两次reload的内存情况以了解自上次reload以来的变化。

jeprof --pdf /usr/local/openresty/nginx/sbin/nginx --base=jeprof.4759.7.m7.heap  jeprof.4759.8.m8.heap > a.pdf



关机jeprof比较详细的介绍可以参考文章http://tinylab.org/the-builtin-heap-profiling-of-jemalloc/

