[Toc]

# ngx.ctx



lua-resty-core/lib/resty/core/ctx.lua

## lua get_ctx_table/set_ctx_table接口

lua接口部分写得相当的绕，如下代码有稍做修改

``` lua
     4	local ffi = require "ffi"
     5	local debug = require "debug"
     6	local base = require "resty.core.base"
     7	local misc = require "resty.core.misc"
     8	
     9	
    10	local C = ffi.C
    11	local register_getter = misc.register_ngx_magic_key_getter
    12	local register_setter = misc.register_ngx_magic_key_setter
    13	local registry = debug.getregistry()
    14	local new_tab = base.new_tab
    15	local ref_in_table = base.ref_in_table
    16	local get_request = base.get_request
    17	local FFI_NO_REQ_CTX = base.FFI_NO_REQ_CTX
    18	local FFI_OK = base.FFI_OK
    19	local error = error
    20	local setmetatable = setmetatable
    21	local type = type
    22	local subsystem = ngx.config.subsystem
    23	
    24	
    25	local ngx_lua_ffi_get_ctx_ref
    26	local ngx_lua_ffi_set_ctx_ref
    27	
    28	
    29	if subsystem == "http" then
    30	    ffi.cdef[[
    31	    int ngx_http_lua_ffi_get_ctx_ref(ngx_http_request_t *r, int *in_ssl_phase,
    32	        int *ssl_ctx_ref);
    33	    int ngx_http_lua_ffi_set_ctx_ref(ngx_http_request_t *r, int ref);
    34	    ]]
    35	
    36	    ngx_lua_ffi_get_ctx_ref = C.ngx_http_lua_ffi_get_ctx_ref
    37	    ngx_lua_ffi_set_ctx_ref = C.ngx_http_lua_ffi_set_ctx_ref
    38	
    39	elseif subsystem == "stream" then
    40	    ffi.cdef[[
    41	    int ngx_stream_lua_ffi_get_ctx_ref(ngx_stream_lua_request_t *r,
    42	        int *in_ssl_phase, int *ssl_ctx_ref);
    43	    int ngx_stream_lua_ffi_set_ctx_ref(ngx_stream_lua_request_t *r, int ref);
    44	    ]]
    45	
    46	    ngx_lua_ffi_get_ctx_ref = C.ngx_stream_lua_ffi_get_ctx_ref
    47	    ngx_lua_ffi_set_ctx_ref = C.ngx_stream_lua_ffi_set_ctx_ref
    48	end
    49	
    50	
    51	local _M = {
    52	    _VERSION = base.version
    53	}
    54	
    55	
    56	local get_ctx_table
    57	do
    58	    local in_ssl_phase = ffi.new("int[1]")
    59	    local ssl_ctx_ref = ffi.new("int[1]")
    60	
    61	    function get_ctx_table()
    62	        local r = get_request()
    63	
    64	        if not r then
    65	            error("no request found")
    66	        end
    67	
    68	        local ctx_ref = ngx_lua_ffi_get_ctx_ref(r, in_ssl_phase, ssl_ctx_ref)
    69	        if ctx_ref == FFI_NO_REQ_CTX then
    70	            error("no request ctx found")
    71	        end
    72	
    73	        local ctxs = registry.ngx_lua_ctx_tables
    74	        if ctx_ref < 0 then
    75	            local ctx
    76	
    77	            ctx_ref = ssl_ctx_ref[0]
    78	            if ctx_ref > 0 and ctxs[ctx_ref] then
    79	                return ctxs[ctx_ref] -- 这里直接return即可
    85	
    86	            else
    87	                if in_ssl_phase[0] ~= 0 then
    88	                    ctx = new_tab(1, 4)
    89	                    -- to avoid creating another table, we assume the users
    90	                    -- won't overwrite the `__index` key
    91	                    ctx.__index = ctx
    92	
    93	                else
    94	                    ctx = new_tab(0, 4)
    95	                end
    96	            end
    97	
    98	            ctx_ref = ref_in_table(ctxs, ctx)
    99	            if ngx_lua_ffi_set_ctx_ref(r, ctx_ref) ~= FFI_OK then
   100	                return nil
   101	            end
   102	            return ctx
   103	        end
   104	        return ctxs[ctx_ref]
   105	    end
   106	end
   107	register_getter("ctx", get_ctx_table)
   108	
   109	
   110	local function set_ctx_table(ctx)
   111	    local ctx_type = type(ctx)
   112	    if ctx_type ~= "table" then
   113	        error("ctx should be a table while getting a " .. ctx_type)
   114	    end
   115	
   116	    local r = get_request()
   117	
   118	    if not r then
   119	        error("no request found")
   120	    end
   121	
   122	    local ctx_ref = ngx_lua_ffi_get_ctx_ref(r, nil, nil)
   123	    if ctx_ref == FFI_NO_REQ_CTX then
   124	        error("no request ctx found")
   125	    end
   126	
   127	    local ctxs = registry.ngx_lua_ctx_tables
   128	    if ctx_ref < 0 then
   129	        ctx_ref = ref_in_table(ctxs, ctx)
   130	        ngx_lua_ffi_set_ctx_ref(r, ctx_ref)
   131	        return
   132	    end
   133	    ctxs[ctx_ref] = ctx
   134	end
   135	register_setter("ctx", set_ctx_table)
   136	
   137	
   138	return _M
```

### ref_in_table 

``` lua
local FREE_LIST_REF = 0

function _M.ref_in_table(tb, key)
    if key == nil then
        return -1
    end
    local ref = tb[FREE_LIST_REF]
    if ref and ref ~= 0 then
         tb[FREE_LIST_REF] = tb[ref]

    else
        ref = #tb + 1
    end
    tb[ref] = key

    -- print("ref key_id returned ", ref)
    return ref
end
```



## register_setter/register_getter接口

给ngx的全局变量设置了metatable，包含_ _index 和   _ _newindex。

``` lua
     4	local base = require "resty.core.base"
     5	local ffi = require "ffi"
     6	local os = require "os"
     7	
     8	
     9	local C = ffi.C
    10	local ffi_new = ffi.new
    11	local ffi_str = ffi.string
    12	local ngx = ngx
    13	local type = type
    14	local error = error
    15	local rawget = rawget
    16	local rawset = rawset
    17	local tonumber = tonumber
    18	local setmetatable = setmetatable
    19	local FFI_OK = base.FFI_OK
    20	local FFI_NO_REQ_CTX = base.FFI_NO_REQ_CTX
    21	local FFI_BAD_CONTEXT = base.FFI_BAD_CONTEXT
    22	local new_tab = base.new_tab
    23	local get_request = base.get_request
    24	local get_size_ptr = base.get_size_ptr
    25	local get_string_buf = base.get_string_buf
    26	local get_string_buf_size = base.get_string_buf_size
    27	local subsystem = ngx.config.subsystem
    28	
    29	
    30	local ngx_lua_ffi_get_resp_status
    31	local ngx_lua_ffi_get_conf_env
    32	local ngx_magic_key_getters
    33	local ngx_magic_key_setters
    34	
    35	
    36	local _M = new_tab(0, 3)
    37	local ngx_mt = new_tab(0, 2)
    38	
    39	
    40	if subsystem == "http" then
    41	    ngx_magic_key_getters = new_tab(0, 4)
    42	    ngx_magic_key_setters = new_tab(0, 2)
    43	
    44	elseif subsystem == "stream" then
    45	    ngx_magic_key_getters = new_tab(0, 2)
    46	    ngx_magic_key_setters = new_tab(0, 1)
    47	end
    48	
    49	
    50	local function register_getter(key, func)
    51	    ngx_magic_key_getters[key] = func
    52	end
    53	_M.register_ngx_magic_key_getter = register_getter
    54	
    55	
    56	local function register_setter(key, func)
    57	    ngx_magic_key_setters[key] = func
    58	end
    59	_M.register_ngx_magic_key_setter = register_setter
    60	
    61	
    62	ngx_mt.__index = function (tb, key)
    63	    local f = ngx_magic_key_getters[key]
    64	    if f then
    65	        return f()
    66	    end
    67	    return rawget(tb, key)
    68	end
    69	
    70	
    71	ngx_mt.__newindex = function (tb, key, ctx)
    72	    local f = ngx_magic_key_setters[key]
    73	    if f then
    74	        return f(ctx)
    75	    end
    76	    return rawset(tb, key, ctx)
    77	end
    78	
    79	
    80	setmetatable(ngx, ngx_mt)
```



## ngx_http_lua_ffi_get_ctx_ref/ngx_http_lua_ffi_set_ctx_ref C接口

``` C
int
ngx_http_lua_ngx_set_ctx_helper(lua_State *L, ngx_http_request_t *r,
    ngx_http_lua_ctx_t *ctx, int index)
{
    ngx_pool_t              *pool;

    if (index < 0) {
        index = lua_gettop(L) + index + 1;
    }

    if (ctx->ctx_ref == LUA_NOREF) {
        ngx_log_debug0(NGX_LOG_DEBUG_HTTP, r->connection->log, 0,
                       "lua create ngx.ctx table for the current request");

        lua_pushliteral(L, ngx_http_lua_ctx_tables_key);
        lua_rawget(L, LUA_REGISTRYINDEX);
        lua_pushvalue(L, index);
        ctx->ctx_ref = luaL_ref(L, -2);
        lua_pop(L, 1);

        pool = r->pool;
        if (ngx_http_lua_ngx_ctx_add_cleanup(r, pool, ctx->ctx_ref) != NGX_OK) {
            return luaL_error(L, "no memory");
        }

        return 0;
    }

    ngx_log_debug0(NGX_LOG_DEBUG_HTTP, r->connection->log, 0,
                   "lua fetching existing ngx.ctx table for the current "
                   "request");

    lua_pushliteral(L, ngx_http_lua_ctx_tables_key);
    lua_rawget(L, LUA_REGISTRYINDEX);
    luaL_unref(L, -1, ctx->ctx_ref);
    lua_pushvalue(L, index);
    ctx->ctx_ref = luaL_ref(L, -2);
    lua_pop(L, 1);

    return 0;
}


int
ngx_http_lua_ffi_get_ctx_ref(ngx_http_request_t *r, int *in_ssl_phase,
    int *ssl_ctx_ref)
{
    ngx_http_lua_ctx_t              *ctx;
#if (NGX_HTTP_SSL)
    ngx_http_lua_ssl_ctx_t          *ssl_ctx;
#endif

    ctx = ngx_http_get_module_ctx(r, ngx_http_lua_module);
    if (ctx == NULL) {
        return NGX_HTTP_LUA_FFI_NO_REQ_CTX;
    }

    if (ctx->ctx_ref >= 0 || in_ssl_phase == NULL) {
        return ctx->ctx_ref;
    }

    *in_ssl_phase = ctx->context & (NGX_HTTP_LUA_CONTEXT_SSL_CERT
                                    | NGX_HTTP_LUA_CONTEXT_SSL_SESS_FETCH
                                    | NGX_HTTP_LUA_CONTEXT_SSL_SESS_STORE);
    *ssl_ctx_ref = LUA_NOREF;

#if (NGX_HTTP_SSL)
    if (r->connection->ssl != NULL) {
        ssl_ctx = ngx_http_lua_ssl_get_ctx(r->connection->ssl->connection);

        if (ssl_ctx != NULL) {
            *ssl_ctx_ref = ssl_ctx->ctx_ref;
        }
    }
#endif

    return LUA_NOREF;
}


int
ngx_http_lua_ffi_set_ctx_ref(ngx_http_request_t *r, int ref)
{
    ngx_pool_t                      *pool;
    ngx_http_lua_ctx_t              *ctx;
#if (NGX_HTTP_SSL)
    ngx_connection_t                *c;
    ngx_http_lua_ssl_ctx_t          *ssl_ctx;
#endif

    ctx = ngx_http_get_module_ctx(r, ngx_http_lua_module);
    if (ctx == NULL) {
        return NGX_HTTP_LUA_FFI_NO_REQ_CTX;
    }

#if (NGX_HTTP_SSL)
    if (ctx->context & (NGX_HTTP_LUA_CONTEXT_SSL_CERT
                        | NGX_HTTP_LUA_CONTEXT_SSL_SESS_FETCH
                        | NGX_HTTP_LUA_CONTEXT_SSL_SESS_STORE))
    {
        ssl_ctx = ngx_http_lua_ssl_get_ctx(r->connection->ssl->connection);
        if (ssl_ctx == NULL) {
            return NGX_ERROR;
        }

        ssl_ctx->ctx_ref = ref;
        c = ngx_ssl_get_connection(r->connection->ssl->connection);
        pool = c->pool;

    } else {
        pool = r->pool;
    }

#else
    pool = r->pool;
#endif

    ctx->ctx_ref = ref;

    if (ngx_http_lua_ngx_ctx_add_cleanup(r, pool, ref) != NGX_OK) {
        return NGX_ERROR;
    }

    return NGX_OK;
}

static void
ngx_http_lua_ngx_ctx_cleanup(void *data)
{
    lua_State       *L;

    ngx_http_lua_ngx_ctx_cleanup_data_t    *clndata = data;

    ngx_log_debug1(NGX_LOG_DEBUG_HTTP, ngx_cycle->log, 0,
                   "lua release ngx.ctx at ref %d", clndata->ref);

    L = clndata->vm;

    lua_pushliteral(L, ngx_http_lua_ctx_tables_key);
    lua_rawget(L, LUA_REGISTRYINDEX);
    luaL_unref(L, -1, clndata->ref);
    lua_pop(L, 1);
}
```

