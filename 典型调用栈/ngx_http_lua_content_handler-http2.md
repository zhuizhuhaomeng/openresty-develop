``` txt
(gdb) bt
#0  ngx_http_lua_content_handler (r=0x555847aafc70) at ../ngx_lua-0.10.19.8/src/ngx_http_lua_contentby.c:167
#1  ngx_http_core_content_phase (r=0x555847aafc70, ph=<optimized out>) at src/http/ngx_http_core_module.c:1257
#2  ngx_http_core_run_phases (r=r@entry=0x555847aafc70) at src/http/ngx_http_core_module.c:878
#3  ngx_http_handler (r=r@entry=0x555847aafc70) at src/http/ngx_http_core_module.c:861
#4  ngx_http_process_request (r=r@entry=0x555847aafc70) at src/http/ngx_http_request.c:2103
#5  ngx_http_v2_run_request (r=0x555847aafc70) at src/http/v2/ngx_http_v2.c:3931
#6  ngx_http_v2_state_header_complete (end=0x7f6d15b54083 "", pos=0x7f6d15b5407a "", h2c=0x555847a985a0) at src/http/v2/ngx_http_v2.c:1868
#7  ngx_http_v2_state_header_complete (h2c=0x555847a985a0, pos=0x7f6d15b5407a "", end=0x7f6d15b54083 "") at src/http/v2/ngx_http_v2.c:1845
#8  ngx_http_v2_state_field_len (h2c=h2c@entry=0x555847a985a0, pos=<optimized out>, end=end@entry=0x7f6d15b54083 "") at src/http/v2/ngx_http_v2.c:1531
#9  ngx_http_v2_state_header_block (h2c=0x555847a985a0, pos=<optimized out>, end=0x7f6d15b54083 "") at src/http/v2/ngx_http_v2.c:1444
#10 ngx_http_v2_read_handler (rev=0x555847a74310) at src/http/v2/ngx_http_v2.c:425
#11 ngx_epoll_process_events (cycle=<optimized out>, timer=<optimized out>, flags=1) at src/event/modules/ngx_epoll_module.c:968
#12 ngx_process_events_and_timers (cycle=cycle@entry=0x555847a65a40) at src/event/ngx_event.c:262
#13 ngx_single_process_cycle (cycle=cycle@entry=0x555847a65a40) at src/os/unix/ngx_process_cycle.c:335
#14 main (argc=<optimized out>, argv=<optimized out>) at src/core/nginx.c:425
```