# openresty 是如何获取请求变量r的

# lua 里面的变量获取

很多的ffi相关的接口需要 ngx_http_request_t *r这个指针变量， 那么在lua里面是如何获取的呢？

按图索骥，很容易找到 是在lib/resty/core/base.lua这个文件中获取的。

然而这里的thread.exdata是什么意思呢？为什么又有两种获取 ngx_http_request_t *r的方法呢？

之所以要有两种不同的方法，是因为追求性能。

getfenv(0)返回的是全局变量的表，然后再表中查找__ngx_req这个变量。而thread.exdata()是openresty对luajit的扩展，相当于直接获取结构体的成员变量，显然后者更加高效。

```lua
 237 do
 238     local exdata
 239 
 240     ok, exdata = pcall(require, "thread.exdata")
 241     if ok and exdata then
 242         function _M.get_request()
 243             local r = exdata()
 244             if r ~= nil then
 245                 return r
 246             end
 247         end
 248 
 249     else
 250         local getfenv = getfenv
 251 
 252         function _M.get_request()
 253             return getfenv(0).__ngx_req
 254         end
 255     end
 256 end

```



# nginx中设置ngx_http_request_t *r

那么既然是从全局表或者是结构体成员获取，这些值是什么时候赋值的呢？我们查找一下代码可以发现是在openresty执行阶段的入口设置的，比如static ngx_int_t ngx_http_lua_access_by_chunk(lua_State *L, ngx_http_request_t *r)。

``` C
#ifndef OPENRESTY_LUAJIT
#define ngx_http_lua_req_key  "__ngx_req"
#endif

static ngx_inline ngx_http_request_t *
ngx_http_lua_get_req(lua_State *L)
{
#ifdef OPENRESTY_LUAJIT
    return lua_getexdata(L);
#else
    ngx_http_request_t    *r;

    lua_getglobal(L, ngx_http_lua_req_key);
    r = lua_touserdata(L, -1);
    lua_pop(L, 1);

    return r;
#endif
}


static ngx_inline void
ngx_http_lua_set_req(lua_State *L, ngx_http_request_t *r)
{
#ifdef OPENRESTY_LUAJIT
    lua_setexdata(L, (void *) r);
#else
    lua_pushlightuserdata(L, r);
    lua_setglobal(L, ngx_http_lua_req_key);
#endif
}

```



# access 执行阶段的入口函数

```C
static ngx_int_t
ngx_http_lua_access_by_chunk(lua_State *L, ngx_http_request_t *r)
{
    int                  co_ref;
    ngx_int_t            rc;
    ngx_uint_t           nreqs;
    lua_State           *co;
    ngx_event_t         *rev;
    ngx_connection_t    *c;
    ngx_http_lua_ctx_t  *ctx;
    ngx_http_cleanup_t  *cln;

    ngx_http_lua_loc_conf_t     *llcf;

    /*  {{{ new coroutine to handle request */
    co = ngx_http_lua_new_thread(r, L, &co_ref);

    if (co == NULL) {
        ngx_log_error(NGX_LOG_ERR, r->connection->log, 0,
                      "lua: failed to create new coroutine "
                      "to handle request");

        return NGX_HTTP_INTERNAL_SERVER_ERROR;
    }

    /*  move code closure to new coroutine */
    lua_xmove(L, co, 1);

#ifndef OPENRESTY_LUAJIT
    /*  set closure's env table to new coroutine's globals table */
    ngx_http_lua_get_globals_table(co);
    lua_setfenv(co, -2);
#endif

    /*  save nginx request in coroutine globals table */
    ngx_http_lua_set_req(co, r);

    ...
}
```



# luajit中的扩展分析

luajit扩展分成lua接口和C接口两个部分。

```
https://github.com/openresty/luajit2/blob/v2.1-agentzh/README.md#threadexdata
https://github.com/openresty/luajit2/blob/v2.1-agentzh/README.md#new-c-api
```

## C接口的实现 

``` C
// C接口的实现，非常简单
LUA_API void lua_setexdata(lua_State *L, void *exdata)
{
  L->exdata = exdata;
}

LUA_API void *lua_getexdata(lua_State *L)
{
  return L->exdata;
}
```

## lua 接口的实现

``` C
LJLIB_NOREG LJLIB_CF(thread_exdata) LJLIB_REC(.)
{
  ptrdiff_t nargs = L->top - L->base;
  GCcdata *cd;

  if (nargs == 0) {
    CTState *cts = ctype_ctsG(G(L));
    if (cts == NULL)
      lj_err_caller(L, LJ_ERR_FFI_NOTLOAD);
    cts->L = L;  /* Save L for errors and allocations. */

    cd = lj_cdata_new(cts, CTID_P_VOID, CTSIZE_PTR);
    cdata_setptr(cdataptr(cd), CTSIZE_PTR, L->exdata);
    setcdataV(L, L->top++, cd);
    return 1;
  }

  cd = lj_lib_checkcdata(L, 1);
  L->exdata = cdata_getptr(cdataptr(cd), CTSIZE_PTR);
  return 0;
}

//这里的lj_cf_thread_exdata就是上面的函数 LJLIB_CF(thread_exdata) 
static int luaopen_thread_exdata(lua_State *L)
{
  return lj_lib_postreg(L, lj_cf_thread_exdata, FF_thread_exdata, "exdata");
}

LUALIB_API int luaopen_base(lua_State *L)
{
  /* NOBARRIER: Table and value are the same. */
  GCtab *env = tabref(L->env);
  settabV(L, lj_tab_setstr(L, env, lj_str_newlit(L, "_G")), env);
  lua_pushliteral(L, LUA_VERSION);  /* top-3. */
  newproxy_weaktable(L);  /* top-2. */
  LJ_LIB_REG(L, "_G", base);
  LJ_LIB_REG(L, LUA_COLIBNAME, coroutine);

#if LJ_HASFFI
  lj_lib_prereg(L, LUA_THRLIBNAME ".exdata", luaopen_thread_exdata, env);
  lj_lib_prereg(L, LUA_THRLIBNAME ".exdata2", luaopen_thread_exdata2, env);
#endif

  return 2;
}

```



从文档中我们看到，这个接口是可以被jit编译的，“As of this version, retrieving the `exdata` (i.e. `th_exdata()` without any argument) can be JIT compiled.” 怎么做才能够被jit编译呢？是下面这个函数实现的，具体原理需要后续分析。

可以参考去官方网站学习 http://wiki.luajit.org/Home#luajit-internals。

``` C

#if LJ_HASFFI
void LJ_FASTCALL recff_thread_exdata(jit_State *J, RecordFFData *rd)
{
  TRef tr = J->base[0];
  if (!tr) {
    TRef trl = emitir(IRT(IR_LREF, IRT_THREAD), 0, 0);
    TRef trp = emitir(IRT(IR_FLOAD, IRT_PTR), trl, IRFL_THREAD_EXDATA);
    TRef trid = lj_ir_kint(J, CTID_P_VOID);
    J->base[0] = emitir(IRTG(IR_CNEWI, IRT_CDATA), trid, trp);
    return;
  }
  recff_nyiu(J, rd);  /* this case is too rare to be interesting */
}

```

