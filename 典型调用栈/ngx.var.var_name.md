## 调用栈

在content_by_lua中调用ngx.var.varname访问变量,比如ngx.var.cookie_name1

```bash
     1	main
     2	ngx_master_process_cycle
     3	ngx_start_worker_processes
     4	ngx_spawn_process
     5	ngx_worker_process_cycle
     6	ngx_process_events_and_timers
     7	ngx_epoll_process_events
     8	ngx_http_process_request_line
     9	ngx_http_process_request_headers
    10	ngx_http_core_run_phases
    11	ngx_http_core_content_phase
    12	ngx_http_lua_content_handler
    13	ngx_http_lua_content_by_chunk
    14	ngx_http_lua_run_thread
    15	lj_BC_FUNCC
    16	lj_cf_ffi_meta___call
    17	lj_ccall_func
    18	lj_vm_ffi_call
    19	ngx_http_lua_ffi_var_get

```