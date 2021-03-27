openrestyz中调试除了添加错误日志外，还可以使用dd这个宏来增加更加详细的日志信息。

可以在文件的最开始定义 #define  DDEBUG 1

比如

``` C
#define DDEBUG 1
/*
 * Copyright (C) Xiaozhe Wang (chaoslawful)
 * Copyright (C) Yichun Zhang (agentzh)
 */


#ifndef DDEBUG
#define DDEBUG 0
#endif
#include "ddebug.h"


#include "ngx_http_lua_misc.h"
#include "ngx_http_lua_util.h"


static int ngx_http_lua_ngx_req_is_internal(lua_State *L);


void
ngx_http_lua_inject_req_misc_api(lua_State *L)
{
    lua_pushcfunction(L, ngx_http_lua_ngx_req_is_internal);
    lua_setfield(L, -2, "is_internal");
}


```

