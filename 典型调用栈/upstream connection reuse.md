# 连接建立的过程

``` shell
(gdb) bt
#0  ngx_http_lua_balancer_get_peer (pc=0xacb8c0, data=0xacbfd8) at ../ngx_lua-0.10.19/src/ngx_http_lua_balancer.c:264
#1  ngx_http_upstream_get_keepalive_peer (pc=0xacb8c0, data=0xacbfa0) at src/http/modules/ngx_http_upstream_keepalive_module.c:241
#2  ngx_event_connect_peer (pc=pc@entry=0xacb8c0) at src/event/ngx_event_connect.c:34
#3  ngx_http_upstream_connect (r=0x9f3e50, u=0xacb8b0) at src/http/ngx_http_upstream.c:1532
#4  ngx_http_upstream_init_request (r=0x9f3e50) at src/http/ngx_http_upstream.c:810
#5  ngx_http_read_client_request_body (post_handler=0x476e60 <ngx_http_upstream_init>, r=0x9f3e50) at src/http/ngx_http_request_body.c:79
#6  ngx_http_read_client_request_body (r=r@entry=0x9f3e50, post_handler=0x476e60 <ngx_http_upstream_init>) at src/http/ngx_http_request_body.c:32
#7  ngx_http_proxy_handler (r=0x9f3e50) at src/http/modules/ngx_http_proxy_module.c:1009
#8  ngx_http_proxy_handler (r=0x9f3e50) at src/http/modules/ngx_http_proxy_module.c:921
#9  ngx_http_core_content_phase (r=0x9f3e50, ph=<optimized out>) at src/http/ngx_http_core_module.c:1257
#10 ngx_http_core_run_phases (r=r@entry=0x9f3e50) at src/http/ngx_http_core_module.c:878
#11 ngx_http_handler (r=r@entry=0x9f3e50) at src/http/ngx_http_core_module.c:861
#12 ngx_http_process_request (r=r@entry=0x9f3e50) at src/http/ngx_http_request.c:2081
#13 ngx_http_process_request_headers (rev=rev@entry=0x99a7e0) at src/http/ngx_http_request.c:1483
#14 ngx_http_process_request_line (rev=0x99a7e0) at src/http/ngx_http_request.c:1154
#15 ngx_epoll_process_events (cycle=<optimized out>, timer=<optimized out>, flags=1) at src/event/modules/ngx_epoll_module.c:901
#16 ngx_process_events_and_timers (cycle=cycle@entry=0x9b2650) at src/event/ngx_event.c:257
#17 ngx_worker_process_cycle (cycle=0x9b2650, data=<optimized out>) at src/os/unix/ngx_process_cycle.c:811
#18 ngx_spawn_process (cycle=cycle@entry=0x9b2650, proc=proc@entry=0x449e60 <ngx_worker_process_cycle>, data=data@entry=0x0, name=name@entry=0x54ca05 "worker process", respawn=respawn@entry=-4) at src/os/unix/ngx_process.c:199
#19 ngx_start_worker_processes (cycle=cycle@entry=0x9b2650, n=1, type=type@entry=-4) at src/os/unix/ngx_process_cycle.c:387
#20 ngx_master_process_cycle (cycle=0x9b2650) at src/os/unix/ngx_process_cycle.c:241
#21 main (argc=<optimized out>, argv=<optimized out>) at src/core/nginx.c:385

```



# SSL 初始化堆栈

```shell
#0  ngx_http_upstream_ssl_init_connection (r=0x9e1140, u=0x9e92d0, c=0x7f575cfe9498) at src/http/ngx_http_upstream.c:1671
#1  ngx_http_upstream_handler (ev=<optimized out>) at src/http/ngx_http_upstream.c:1287
#2  ngx_epoll_process_events (cycle=<optimized out>, timer=<optimized out>, flags=1) at src/event/modules/ngx_epoll_module.c:930
#3  ngx_process_events_and_timers (cycle=cycle@entry=0x8f60f0) at src/event/ngx_event.c:257
#4  ngx_worker_process_cycle (cycle=0x8f60f0, data=<optimized out>) at src/os/unix/ngx_process_cycle.c:811
#5  ngx_spawn_process (cycle=cycle@entry=0x8f60f0, proc=proc@entry=0x449e60 <ngx_worker_process_cycle>, data=data@entry=0x0, name=name@entry=0x54ca05 "worker process", respawn=respawn@entry=-3) at src/os/unix/ngx_process.c:199
#6  ngx_start_worker_processes (cycle=cycle@entry=0x8f60f0, n=1, type=type@entry=-3) at src/os/unix/ngx_process_cycle.c:387
#7  ngx_master_process_cycle (cycle=0x8f60f0) at src/os/unix/ngx_process_cycle.c:135
#8  main (argc=<optimized out>, argv=<optimized out>) at src/core/nginx.c:385
```



```shell
print *(ngx_http_upstream_keepalive_peer_data_t *)0x9f48d0
$4 = {
  conf = 0xa35718, 
  upstream = 0x9f41e0, 
  data = 0x9f4908, 
  original_get_peer = 0x514c70 <ngx_http_lua_balancer_get_peer>, 
  original_free_peer = 0x514c30 <ngx_http_lua_balancer_free_peer>, 
  original_set_session = 0x514ae0 <ngx_http_lua_balancer_set_session>, 
  original_save_session = 0x514ac0 <ngx_http_lua_balancer_save_session>
}
```

# 释放连接，存入连接池的过程

```shell
#0  ngx_http_upstream_free_keepalive_peer (pc=0xacb8c0, data=0xacbfa0, state=0) at src/http/modules/ngx_http_upstream_keepalive_module.c:312
#1  ngx_http_upstream_finalize_request (r=0xa908d0, u=0xacb8b0, rc=0) at src/http/ngx_http_upstream.c:4384
#2  ngx_http_upstream_process_request (r=0xa908d0, u=0xacb8b0) at src/http/ngx_http_upstream.c:4062
#3  ngx_http_upstream_handler (ev=<optimized out>) at src/http/ngx_http_upstream.c:1290
#4  ngx_epoll_process_events (cycle=<optimized out>, timer=<optimized out>, flags=1) at src/event/modules/ngx_epoll_module.c:901
#5  ngx_process_events_and_timers (cycle=cycle@entry=0x9b2650) at src/event/ngx_event.c:257
#6  ngx_worker_process_cycle (cycle=0x9b2650, data=<optimized out>) at src/os/unix/ngx_process_cycle.c:811
#7  ngx_spawn_process (cycle=cycle@entry=0x9b2650, proc=proc@entry=0x449e60 <ngx_worker_process_cycle>, data=data@entry=0x0, name=name@entry=0x54ca05 "worker process", respawn=respawn@entry=-4) at src/os/unix/ngx_process.c:199
#8  ngx_start_worker_processes (cycle=cycle@entry=0x9b2650, n=1, type=type@entry=-4) at src/os/unix/ngx_process_cycle.c:387
#9  ngx_master_process_cycle (cycle=0x9b2650) at src/os/unix/ngx_process_cycle.c:241
#10 main (argc=<optimized out>, argv=<optimized out>) at src/core/nginx.c:385
```



如下配置会有三次创建server conf

```yajl
worker_processes  1;
daemon on;
master_process off;
error_log /home/ljl/code/orinc/lua-nginx-module-plus/t/servroot/logs/error.log debug;
pid       /home/ljl/code/orinc/lua-nginx-module-plus/t/servroot/logs/nginx.pid;
env MOCKEAGAIN_VERBOSE;
env MOCKEAGAIN;
env MOCKEAGAIN_WRITE_TIMEOUT_PATTERN;
env LD_PRELOAD;
env LD_LIBRARY_PATH;
env DYLD_INSERT_LIBRARIES;
env DYLD_FORCE_FLAT_NAMESPACE;
#env LUA_PATH;
#env LUA_CPATH;



http {
    access_log /home/ljl/code/orinc/lua-nginx-module-plus/t/servroot/logs/access.log;
    #access_log off;

    default_type text/plain;
    keepalive_timeout  68;

    upstream backend {
        server 0.0.0.1;
        balancer_by_lua_block {
            print("I am in phase ", ngx.get_phase())
        }
    }


    server {
        listen          1984;
        server_name     'localhost';

        client_max_body_size 30M;
        #client_body_buffer_size 4k;

        # Begin preamble config...

        # End preamble config...

        # Begin test case config...
    location = /t {
        proxy_pass http://backend;
    }

        # End test case config.

        location / {
            root /home/ljl/code/orinc/lua-nginx-module-plus/t/servroot/html;
            index index.html index.htm;
        }
    }
}



events {
    accept_mutex off;

    worker_connections  64;
}
```



创建server conf

```shell
(gdb) bt
#0  ngx_http_lua_create_srv_conf (cf=0x7fffffffca40) at /home/ljl/code/orinc/lua-nginx-module-plus/src/ngx_http_lua_module.c:1078
#1  ngx_http_block (cf=0x7fffffffca40, cmd=<optimized out>, conf=<optimized out>) at src/http/ngx_http.c:202
#2  ngx_conf_handler (cf=0x7fffffffca40, last=<optimized out>) at src/core/ngx_conf_file.c:463
#3  ngx_conf_parse (cf=0x7fffffffca40, filename=<optimized out>) at src/core/ngx_conf_file.c:319
#4  ngx_init_cycle (old_cycle=0x7fffffffcce8) at src/core/ngx_cycle.c:290
#5  main (argc=<optimized out>, argv=<optimized out>) at src/core/nginx.c:330
(gdb) c
Continuing.
(gdb) bt
#0  ngx_http_lua_create_srv_conf (cf=0x7fffffffca40) at /home/ljl/code/orinc/lua-nginx-module-plus/src/ngx_http_lua_module.c:1078
#1  ngx_http_upstream (cf=0x7fffffffca40, cmd=<optimized out>, dummy=<optimized out>) at src/http/ngx_http_upstream.c:5976
#2  ngx_conf_handler (cf=0x7fffffffca40, last=<optimized out>) at src/core/ngx_conf_file.c:463
#3  ngx_conf_parse (cf=0x7fffffffca40, filename=<optimized out>) at src/core/ngx_conf_file.c:319
#4  ngx_http_block (cf=0x7fffffffca40, cmd=<optimized out>, conf=<optimized out>) at src/http/ngx_http.c:237
#5  ngx_conf_handler (cf=0x7fffffffca40, last=<optimized out>) at src/core/ngx_conf_file.c:463
#6  ngx_conf_parse (cf=0x7fffffffca40, filename=<optimized out>) at src/core/ngx_conf_file.c:319
#7  ngx_init_cycle (old_cycle=0x7fffffffcce8) at src/core/ngx_cycle.c:290
#8  main (argc=<optimized out>, argv=<optimized out>) at src/core/nginx.c:330
(gdb) bt
#0  ngx_http_lua_create_srv_conf (cf=0x7fffffffca40) at /home/ljl/code/orinc/lua-nginx-module-plus/src/ngx_http_lua_module.c:1078
#1  ngx_http_core_server (cf=0x7fffffffca40, cmd=<optimized out>, dummy=<optimized out>) at src/http/ngx_http_core_module.c:2844
#2  ngx_conf_handler (cf=0x7fffffffca40, last=<optimized out>) at src/core/ngx_conf_file.c:463
#3  ngx_conf_parse (cf=0x7fffffffca40, filename=<optimized out>) at src/core/ngx_conf_file.c:319
#4  ngx_http_block (cf=0x7fffffffca40, cmd=<optimized out>, conf=<optimized out>) at src/http/ngx_http.c:237
#5  ngx_conf_handler (cf=0x7fffffffca40, last=<optimized out>) at src/core/ngx_conf_file.c:463
#6  ngx_conf_parse (cf=0x7fffffffca40, filename=<optimized out>) at src/core/ngx_conf_file.c:319
#7  ngx_init_cycle (old_cycle=0x7fffffffcce8) at src/core/ngx_cycle.c:290
#8  main (argc=<optimized out>, argv=<optimized out>) at src/core/nginx.c:330
```

