# curl为什么连接成功了却没有响应

在写测试用例的时候，需要指定源IP地址发起连接，这时候想到用curl的--interface 来指定源IP地址。

以下是openresty中的lua通过os.execute代码执行curl

``` lua
         content_by_lua_block {
             os.execute("curl --interface 127.0.0.100 http://127.0.0.1:1985")
         }
```

但是测试用例失败了，通过抓包发现连接正常建立，发出去的数据也是符合预期，就是服务端不响应。



使用netstat 查看发现连接是正常建立，就是不结束。第三行的78表示socket里面有78个字节，但是并没有被应用层接收处理。

``` shell
[ljl@localhost lua-conf-nginx-module]$ sudo netstat -tplna | grep 1985
tcp        1      0 0.0.0.0:1985            0.0.0.0:*               LISTEN      4167/nginx          
tcp       78      0 127.0.0.1:1985          127.0.0.100:50969       ESTABLISHED -                   
tcp        0      0 127.0.0.100:50969       127.0.0.1:1985          ESTABLISHED 4168/curl   
```



使用ss查看，那么发现1985端口是curl在监听，跟上面的属于nginx在监听是不一样的。

``` shell
[ljl@localhost lua-conf-nginx-module]$ ss -tplna | grep 1985
LISTEN   1   128   0.0.0.0:1985       0.0.0.0:*   users:(("curl",pid=4168,fd=7),("nginx",pid=4167,fd=7))   
ESTAB    78   0    127.0.0.1:1985     127.0.0.100:50969                                                
ESTAB    0    0    127.0.0.100:50969  127.0.0.1:1985    users:(("curl",pid=4168,fd=6)) 
```



使用lsof查看 curl进程

``` shell
[ljl@localhost lua-conf-nginx-module]$ lsof -P -n -p 4168 | grep TCP
lsof: WARNING: can't stat() tracefs file system /sys/kernel/debug/tracing
      Output information may be incomplete.
curl    4168  ljl    6u     IPv4  88560      0t0        TCP 127.0.0.100:50969->127.0.0.1:1985 (ESTABLISHED)
curl    4168  ljl    7u     IPv4  85961      0t0        TCP *:1985 (LISTEN)
curl    4168  ljl    8u     IPv4  85962      0t0        TCP 127.0.0.1:64321 (LISTEN)
curl    4168  ljl    9u     IPv4  85963      0t0        TCP *:1984 (LISTEN)
```



使用curl查看nginx进程

``` shell
[ljl@localhost lua-conf-nginx-module]$ lsof -P -n -p 4167 | grep TCP
lsof: WARNING: can't stat() tracefs file system /sys/kernel/debug/tracing
      Output information may be incomplete.
nginx   4167  ljl    7u     IPv4  85961      0t0        TCP *:1985 (LISTEN)
nginx   4167  ljl    8u     IPv4  85962      0t0        TCP 127.0.0.1:64321 (LISTEN)
nginx   4167  ljl    9u     IPv4  85963      0t0        TCP *:1984 (LISTEN)
nginx   4167  ljl   12u     IPv4  84930      0t0        TCP 127.0.0.1:1984->127.0.0.1:33950 (CLOSE_WAIT)
```



问题1：为什么curl会监听原本属于nginx的端口呢？ 

这个还是比较好解释的，因为curl是在nginx进程调用os.execute起来的进程。也就是说curl是nginx进程fork的子进程，会继承属于nginx的监听端口。



问题2：为什么连接建立成功了，但是却没有被应用层处理？

内核应该是会通知nginx和cul，而curl显然不会去accept，因此就是nginx不处理导致的。为什么nginx不去accept呢？那就看看nginx在干嘛吧！

通过gdb回溯堆栈问题就一目了然。因为nginx以同步阻塞的方式等待os.execute执行curl命令的结束；而curl正在等待nginx给应答。这就造成了死循环。

```
(gdb) bt
#0  0x00007fe6a9102cdb in __GI___waitpid (pid=5389, stat_loc=stat_loc@entry=0x7fffd73fde98, options=options@entry=0) at ../sysdeps/unix/sysv/linux/waitpid.c:30
#1  0x00007fe6a907e92f in do_system (line=<optimized out>) at ../sysdeps/posix/system.c:149
#2  0x00007fe6a907ed2e in __libc_system (line=<optimized out>) at ../sysdeps/posix/system.c:185
#3  0x00007fe6aa873aca in lj_cf_os_execute (L=0x7fe6ab016780) at lib_os.c:52
#4  0x00007fe6aa804a7d in lj_BC_FUNCC () from /usr/local/lib/libluajit-5.1.so.2
#5  0x0000562a32e7aafd in ngx_http_lua_run_thread (L=L@entry=0x7fe6ab048380, r=r@entry=0x562a344abb40, ctx=ctx@entry=0x562a344ac530, nrets=nrets@entry=0) at /home/ljl/code/orinc/lua-nginx-module-plus/src/ngx_http_lua_util.c:1167
#6  0x0000562a32e7ef54 in ngx_http_lua_content_by_chunk (L=L@entry=0x7fe6ab048380, r=r@entry=0x562a344abb40) at /home/ljl/code/orinc/lua-nginx-module-plus/src/ngx_http_lua_contentby.c:124
#7  0x0000562a32e7f112 in ngx_http_lua_content_handler_inline (r=0x562a344abb40) at /home/ljl/code/orinc/lua-nginx-module-plus/src/ngx_http_lua_contentby.c:312
#8  0x0000562a32e7e87e in ngx_http_lua_content_handler (r=0x562a344abb40) at /home/ljl/code/orinc/lua-nginx-module-plus/src/ngx_http_lua_contentby.c:222
#9  0x0000562a32da75b6 in ngx_http_core_content_phase (r=0x562a344abb40, ph=<optimized out>) at src/http/ngx_http_core_module.c:1257
#10 0x0000562a32da18b1 in ngx_http_core_run_phases (r=r@entry=0x562a344abb40) at src/http/ngx_http_core_module.c:878
#11 0x0000562a32da1956 in ngx_http_handler (r=r@entry=0x562a344abb40) at src/http/ngx_http_core_module.c:861
#12 0x0000562a32dadc4f in ngx_http_process_request (r=r@entry=0x562a344abb40) at src/http/ngx_http_request.c:2103
#13 0x0000562a32dae2a8 in ngx_http_process_request_headers (rev=rev@entry=0x562a344aa2d0) at src/http/ngx_http_request.c:1505
#14 0x0000562a32dae666 in ngx_http_process_request_line (rev=rev@entry=0x562a344aa2d0) at src/http/ngx_http_request.c:1176
#15 0x0000562a32dae81f in ngx_http_wait_request_handler (rev=0x562a344aa2d0) at src/http/ngx_http_request.c:522
#16 0x0000562a32d906eb in ngx_epoll_process_events (cycle=<optimized out>, timer=<optimized out>, flags=<optimized out>) at src/event/modules/ngx_epoll_module.c:968
#17 0x0000562a32d839e5 in ngx_process_events_and_timers (cycle=cycle@entry=0x562a3448cde0) at src/event/ngx_event.c:262
#18 0x0000562a32d8f3e3 in ngx_single_process_cycle (cycle=0x562a3448cde0) at src/os/unix/ngx_process_cycle.c:335
#19 0x0000562a32d6177e in main (argc=<optimized out>, argv=<optimized out>) at src/core/nginx.c:425
(gdb) quit
```

