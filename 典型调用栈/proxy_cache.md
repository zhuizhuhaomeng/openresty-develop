``` shell
#0  __libc_open64 (file=0x55b7245f5a38 "proxy/cache/1/e7/06d5fc7f1a135385512343aaa6a6be71", oflag=oflag@entry=2048) at ../sysdeps/unix/sysv/linux/open64.c:37
#1  open64 (__oflag=2048, __path=<optimized out>) at /usr/include/bits/fcntl2.h:59
#2  ngx_open_file_wrapper (name=<optimized out>, of=0x7ffe493a6190, mode=2048, create=0, access=0, log=0x55b724552cc0) at src/core/ngx_open_file_cache.c:638
#3  ngx_open_and_stat_file (name=name@entry=0x55b7245f5758, of=of@entry=0x7ffe493a6190, log=0x55b724552cc0) at src/core/ngx_open_file_cache.c:876
#4  ngx_open_cached_file (cache=0x0, name=name@entry=0x55b7245f5758, of=of@entry=0x7ffe493a6190, pool=0x55b7245f3ec0) at src/core/ngx_open_file_cache.c:186
#5  ngx_http_file_cache_open (r=r@entry=0x55b7245f3f10) at src/http/ngx_http_file_cache.c:363
#6  ngx_http_upstream_cache (u=0x55b7245f52b0, r=0x55b7245f3f10) at src/http/ngx_http_upstream.c:930
#7  ngx_http_upstream_init_request (r=0x55b7245f3f10) at src/http/ngx_http_upstream.c:587
#8  ngx_http_read_client_request_body (post_handler=0x55b722bfc2d0 <ngx_http_upstream_init>, r=0x55b7245f3f10) at src/http/ngx_http_request_body.c:82
#9  ngx_http_read_client_request_body (r=r@entry=0x55b7245f3f10, post_handler=0x55b722bfc2d0 <ngx_http_upstream_init>) at src/http/ngx_http_request_body.c:35
#10 ngx_http_proxy_handler (r=0x55b7245f3f10) at src/http/modules/ngx_http_proxy_module.c:1026
#11 ngx_http_core_content_phase (r=0x55b7245f3f10, ph=<optimized out>) at src/http/ngx_http_core_module.c:1257
#12 ngx_http_core_run_phases (r=r@entry=0x55b7245f3f10) at src/http/ngx_http_core_module.c:878
#13 ngx_http_handler (r=r@entry=0x55b7245f3f10) at src/http/ngx_http_core_module.c:861
#14 ngx_http_process_request (r=r@entry=0x55b7245f3f10) at src/http/ngx_http_request.c:2103
#15 ngx_http_process_request_headers (rev=rev@entry=0x55b7245a5fc8) at src/http/ngx_http_request.c:1505
#16 ngx_http_process_request_line (rev=0x55b7245a5fc8) at src/http/ngx_http_request.c:1176
#17 ngx_epoll_process_events (cycle=<optimized out>, timer=<optimized out>, flags=1) at src/event/modules/ngx_epoll_module.c:968
#18 ngx_process_events_and_timers (cycle=cycle@entry=0x55b72456b620) at src/event/ngx_event.c:262
#19 ngx_worker_process_cycle (cycle=cycle@entry=0x55b72456b620, data=data@entry=0x0) at src/os/unix/ngx_process_cycle.c:856
#20 ngx_spawn_process (cycle=cycle@entry=0x55b72456b620, proc=proc@entry=0x55b722bcb770 <ngx_worker_process_cycle>, data=data@entry=0x0, name=name@entry=0x55b722cbd675 "worker process", respawn=respawn@entry=-3) at src/os/unix/ngx_process.c:207
#21 ngx_start_worker_processes (cycle=cycle@entry=0x55b72456b620, n=1, type=type@entry=-3) at src/os/unix/ngx_process_cycle.c:412
#22 ngx_master_process_cycle (cycle=0x55b72456b620) at src/os/unix/ngx_process_cycle.c:143
#23 main (argc=<optimized out>, argv=<optimized out>) at src/core/nginx.c:428
```

