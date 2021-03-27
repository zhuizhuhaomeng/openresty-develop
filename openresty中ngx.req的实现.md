# openresty中ngx.req的实现

[Toc]

# openresty中ngx的常见的使用方式

下面是从lua-nginx-module的测试用例中摘抄出来的一个代码片段。

我们看到ngx.req.set_header("Connection", "CLOSE") 这个语句，起作用就是将当前请求的Connecton请求头设置为CLOSE，告诉客户的要关闭连接。

这里有几个疑问：

1. 这种设置应该是请求相关的，但是没有看到请求的变量？
2. ngx是哪里来的，类型是啥？

从lua的语法出发, ngx没有被定义为local，肯定是个全局变量。

那么就会引出另一个问题，这个全局变量是在哪里定义的？

```lua
  55     location /req-header {
  56         rewrite_by_lua '
  57             ngx.req.set_header("Connection", "CLOSE");
  58         ';
  59 
  60         echo "connection: $http_connection";
  61     }

```

# ngx变量探索

## ngx的类型

只需要使用如下几个简单的命令就可以分析ngx、ngx.req、ngx.req.set_header的类型。实验结果跟预期的一致，ngx就是一张表，req也是一张表，而set_header是一个函数。

```shell
[ljl@localhost t]$ resty -e "ngx.say(type(ngx))"
table
[ljl@localhost t]$ resty -e "ngx.say(type(ngx.req))"
table
[ljl@localhost t]$ resty -e "ngx.say(type(ngx.req.set_header))"
function
[ljl@localhost t]$ 
```



## ngx内容探索

我们想探寻一下ngx这张表里面有什么，req里面又有什么，可以这样分析：

```shell
[ljl@localhost t]$ resty -e "for key, _ in pairs(ngx) do ngx.say(key) end" | sort
AGAIN
ALERT
arg
config
cookie_time
crc32_long
crc32_short
CRIT
DEBUG
DECLINED
decode_args
decode_base64
DONE
EMERG
encode_args
encode_base64
eof
ERR
ERROR
escape_uri
exec
exit
flush
get_phase
header
hmac_sha1
HTTP_ACCEPTED
HTTP_BAD_GATEWAY
HTTP_BAD_REQUEST
HTTP_CLOSE
HTTP_CONFLICT
HTTP_CONTINUE
HTTP_COPY
HTTP_CREATED
HTTP_DELETE
HTTP_FORBIDDEN
HTTP_GATEWAY_TIMEOUT
HTTP_GET
HTTP_GONE
HTTP_HEAD
HTTP_ILLEGAL
HTTP_INSUFFICIENT_STORAGE
HTTP_INTERNAL_SERVER_ERROR
HTTP_LOCK
HTTP_METHOD_NOT_IMPLEMENTED
HTTP_MKCOL
HTTP_MOVE
HTTP_MOVED_PERMANENTLY
HTTP_MOVED_TEMPORARILY
HTTP_NO_CONTENT
HTTP_NOT_ACCEPTABLE
HTTP_NOT_ALLOWED
HTTP_NOT_FOUND
HTTP_NOT_MODIFIED
HTTP_OK
HTTP_OPTIONS
HTTP_PARTIAL_CONTENT
HTTP_PATCH
HTTP_PAYMENT_REQUIRED
HTTP_PERMANENT_REDIRECT
HTTP_POST
HTTP_PROPFIND
HTTP_PROPPATCH
HTTP_PUT
HTTP_REQUEST_TIMEOUT
HTTP_SEE_OTHER
HTTP_SERVICE_UNAVAILABLE
HTTP_SPECIAL_RESPONSE
HTTP_SWITCHING_PROTOCOLS
HTTP_TEMPORARY_REDIRECT
http_time
HTTP_TOO_MANY_REQUESTS
HTTP_TRACE
HTTP_UNAUTHORIZED
HTTP_UNLOCK
HTTP_UPGRADE_REQUIRED
HTTP_VERSION_NOT_SUPPORTED
INFO
localtime
location
log
md5
md5_bin
NOTICE
now
null
OK
on_abort
orig_print
orig_say
parse_http_time
_phase_ctx
print
quote_sql_str
re
redirect
req
resp
say
send_headers
sha1_bin
shared
sleep
socket
STDERR
thread
time
timer
today
unescape_uri
update_time
utctime
var
WARN
worker
```

## ngx.req内容探索 

同样的，我们想了解一下 ngx.req都有哪些成员，使用如下的命令

``` shell
[ljl@localhost t]$ resty -e "for key, _ in pairs(ngx.req) do ngx.say(key) end" | sort
append_body
clear_header
discard_body
finish_body
get_body_data
get_body_file
get_headers
get_method
get_post_args
get_uri_args
http_version
init_body
is_internal
raw_header
read_body
set_body_data
set_body_file
set_header
set_method
set_uri
set_uri_args
socket
start_time
```



# ngx 全局变量定义分析

`ngx`这个全局变量在哪里定义的呢？应该要在一个非常早的阶段，也就是lua vm初始化的阶段来定义，否则在init_lua_block d等阶段就不能使用了。具体是在ngx_http_lua_inject_ngx_api这个函数定义的。参照函数第一行的lua_createtable(L, 0 /* narr */, 113 /* nrec */);    /* ngx.* */和函数末尾的lua_setglobal(L, "ngx")。

```c
static void
ngx_http_lua_inject_ngx_api(lua_State *L, ngx_http_lua_main_conf_t *lmcf,
    ngx_log_t *log)
{
    lua_createtable(L, 0 /* narr */, 113 /* nrec */);    /* ngx.* */

    lua_pushcfunction(L, ngx_http_lua_get_raw_phase_context);
    lua_setfield(L, -2, "_phase_ctx");

    ngx_http_lua_inject_arg_api(L);

    ngx_http_lua_inject_http_consts(L);
    ngx_http_lua_inject_core_consts(L);

    ngx_http_lua_inject_log_api(L);
    ngx_http_lua_inject_output_api(L);
    ngx_http_lua_inject_string_api(L);
    ngx_http_lua_inject_control_api(log, L);
    ngx_http_lua_inject_subrequest_api(L);
    ngx_http_lua_inject_sleep_api(L);

    ngx_http_lua_inject_req_api(log, L);
    ngx_http_lua_inject_resp_header_api(L);
    ngx_http_lua_create_headers_metatable(log, L);
    ngx_http_lua_inject_shdict_api(lmcf, L);
    ngx_http_lua_inject_socket_tcp_api(log, L);
    ngx_http_lua_inject_socket_udp_api(log, L);
    ngx_http_lua_inject_uthread_api(log, L);
    ngx_http_lua_inject_timer_api(L);
    ngx_http_lua_inject_config_api(L);

    lua_getglobal(L, "package"); /* ngx package */
    lua_getfield(L, -1, "loaded"); /* ngx package loaded */
    lua_pushvalue(L, -3); /* ngx package loaded ngx */
    lua_setfield(L, -2, "ngx"); /* ngx package loaded */
    lua_pop(L, 2);

    lua_setglobal(L, "ngx");

    ngx_http_lua_inject_coroutine_api(log, L);
}
```

从上面的代码可以看到，这里把ngx设置为全局变量，但是为什么还要加入package.load去呢？

是不是阻止ngx被垃圾回收呢？但是全局变量应该是不会被回收的



## package 表内容

这个package.loaded里面都有什么东西呢？

``` shell
[ljl@localhost stream-lua-nginx-module]$ resty -e "for key, _ in pairs(package.loaded) do ngx.say(key) end" | sort
bit
coroutine
debug
ffi
_G
io
jit
jit.opt
math
ndk
ngx
ngx.process
os
package
resty.core
resty.core.base
resty.core.base64
resty.core.ctx
resty.core.exit
resty.core.hash
resty.core.misc
resty.core.ndk
resty.core.phase
resty.core.regex
resty.core.request
resty.core.response
resty.core.shdict
resty.core.socket
resty.core.time
resty.core.uri
resty.core.utils
resty.core.var
resty.core.worker
resty.lrucache
string
table
table.clear
table.new
thread.exdata
```





带着这个疑问我们也来加个全局变量来试试看。