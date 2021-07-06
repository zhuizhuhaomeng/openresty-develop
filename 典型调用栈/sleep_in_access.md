``` shell
(gdb) bt
#0  ngx_http_lua_ngx_sleep (L=0x7ff6c21f7500) at ../ngx_lua-0.10.20/src/ngx_http_lua_sleep.c:34
#1  lj_BC_FUNCC () from target:/usr/local/openresty/luajit/lib/libluajit-5.1.so.2
#2  ngx_http_lua_run_thread (L=L@entry=0x7ff6c2222380, r=r@entry=0x23ca460, ctx=ctx@entry=0x23cb800, nrets=<optimized out>, nrets@entry=0) at ../ngx_lua-0.10.20/src/ngx_http_lua_util.c:1167
#3  ngx_http_lua_access_by_chunk (L=0x7ff6c2222380, r=0x23ca460) at ../ngx_lua-0.10.20/src/ngx_http_lua_accessby.c:337
#4  ngx_http_lua_access_handler (r=0x23ca460) at ../ngx_lua-0.10.20/src/ngx_http_lua_accessby.c:158
#5  ngx_http_core_access_phase (r=0x23ca460, ph=0x23810f8) at src/http/ngx_http_core_module.c:1103
#6  ngx_http_core_run_phases (r=r@entry=0x23ca460) at src/http/ngx_http_core_module.c:878
#7  ngx_http_handler (r=r@entry=0x23ca460) at src/http/ngx_http_core_module.c:861
#8  ngx_http_process_request (r=r@entry=0x23ca460) at src/http/ngx_http_request.c:2106
#9  ngx_http_process_request_headers (rev=rev@entry=0x239a570) at src/http/ngx_http_request.c:1508
#10 ngx_http_process_request_line (rev=0x239a570) at src/http/ngx_http_request.c:1175
#11 ngx_epoll_process_events (cycle=<optimized out>, timer=<optimized out>, flags=1) at src/event/modules/ngx_epoll_module.c:901
#12 ngx_process_events_and_timers (cycle=cycle@entry=0x23340f0) at src/event/ngx_event.c:257
#13 ngx_worker_process_cycle (cycle=0x23340f0, data=<optimized out>) at src/os/unix/ngx_process_cycle.c:782
#14 ngx_spawn_process (cycle=cycle@entry=0x23340f0, proc=proc@entry=0x44b6f0 <ngx_worker_process_cycle>, data=data@entry=0x0, name=name@entry=0x550728 "worker process", respawn=respawn@entry=-3) at src/os/unix/ngx_process.c:207
#15 ngx_start_worker_processes (cycle=cycle@entry=0x23340f0, n=1, type=type@entry=-3) at src/os/unix/ngx_process_cycle.c:382
#16 ngx_master_process_cycle (cycle=0x23340f0) at src/os/unix/ngx_process_cycle.c:135
#17 main (argc=<optimized out>, argv=<optimized out>) at src/core/nginx.c:386
```





``` shell
(gdb) bt
#0  ngx_http_lua_sleep_handler (ev=0x23c9fa0) at ../ngx_lua-0.10.20/src/ngx_http_lua_sleep.c:106
#1  ngx_event_expire_timers () at src/event/ngx_event_timer.c:94
#2  ngx_process_events_and_timers (cycle=cycle@entry=0x2338100) at src/event/ngx_event.c:270
#3  ngx_worker_process_cycle (cycle=0x2338100, data=<optimized out>) at src/os/unix/ngx_process_cycle.c:782
#4  ngx_spawn_process (cycle=cycle@entry=0x2338100, proc=proc@entry=0x44b6f0 <ngx_worker_process_cycle>, data=data@entry=0x0, name=name@entry=0x550728 "worker process", respawn=respawn@entry=-4) at src/os/unix/ngx_process.c:207
#5  ngx_start_worker_processes (cycle=cycle@entry=0x2338100, n=1, type=type@entry=-4) at src/os/unix/ngx_process_cycle.c:382
#6  ngx_master_process_cycle (cycle=0x2338100) at src/os/unix/ngx_process_cycle.c:241
#7  main (argc=<optimized out>, argv=<optimized out>) at src/core/nginx.c:386

```

