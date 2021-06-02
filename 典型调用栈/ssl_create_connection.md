

# stap分析脚本

```
[root@lijunlong systemtap-plus]# cat ssl.stp 

probe process("/usr/local/openresty/nginx/sbin/nginx").function("ngx_process*") {
    printf("%s\n", probefunc());
}

#probe process("/usr/local/openresty/openssl/lib/libssl.so.1.1").function("ssl*") {
#    printf("%s\n", probefunc());
#}

probe process("/usr/local/openresty/openssl/lib/libssl.so.1.1").function("SSL_do_handshake") {
    print_ustack(ubacktrace());
}

[root@lijunlong systemtap-plus]# stap -d /usr/local/openresty/openssl/lib/libssl.so.1.1  ssl.stp 
ngx_process_events_and_timers
ngx_process_events_and_timers
ngx_process_events_and_timers
WARNING: Missing unwind data for a module, rerun with 'stap -d /usr/lib64/libc-2.17.so'
 0x7fa5c4485090 : SSL_do_handshake+0x0/0xb0 [/usr/local/openresty/openssl/lib/libssl.so.1.1]
 0x44dae3 : ngx_ssl_handshake+0x23/0x1f0 [/usr/local/openresty/nginx/sbin/nginx]
 0x460586 : ngx_http_ssl_handshake+0x196/0x340 [/usr/local/openresty/nginx/sbin/nginx]
 0x449eae : ngx_epoll_process_events+0x20e/0x270 [/usr/local/openresty/nginx/sbin/nginx]
 0x44100b : ngx_process_events_and_timers+0x6b/0x1b0 [/usr/local/openresty/nginx/sbin/nginx]
 0x44811a : ngx_worker_process_cycle+0x7a/0x170 [/usr/local/openresty/nginx/sbin/nginx]
 0x446b24 : ngx_spawn_process+0x164/0x4b0 [/usr/local/openresty/nginx/sbin/nginx]
 0x44856c : ngx_start_worker_processes+0x6c/0xd0 [/usr/local/openresty/nginx/sbin/nginx]
 0x448e33 : ngx_master_process_cycle+0x1c3/0xa10 [/usr/local/openresty/nginx/sbin/nginx]
 0x421512 : main+0xbf2/0xc28 [/usr/local/openresty/nginx/sbin/nginx]
 0x7fa5c3a02555 : 0x7fa5c3a02555 [/usr/lib64/libc-2.17.so+0x22555/0x3c9000]
ngx_process_events_and_timers
 0x7fa5c4485090 : SSL_do_handshake+0x0/0xb0 [/usr/local/openresty/openssl/lib/libssl.so.1.1]
 0x44dae3 : ngx_ssl_handshake+0x23/0x1f0 [/usr/local/openresty/nginx/sbin/nginx]
 0x44dcd8 : ngx_ssl_handshake_handler+0x28/0x30 [/usr/local/openresty/nginx/sbin/nginx]
 0x449eae : ngx_epoll_process_events+0x20e/0x270 [/usr/local/openresty/nginx/sbin/nginx]
 0x44100b : ngx_process_events_and_timers+0x6b/0x1b0 [/usr/local/openresty/nginx/sbin/nginx]
 0x44811a : ngx_worker_process_cycle+0x7a/0x170 [/usr/local/openresty/nginx/sbin/nginx]
 0x446b24 : ngx_spawn_process+0x164/0x4b0 [/usr/local/openresty/nginx/sbin/nginx]
 0x44856c : ngx_start_worker_processes+0x6c/0xd0 [/usr/local/openresty/nginx/sbin/nginx]
 0x448e33 : ngx_master_process_cycle+0x1c3/0xa10 [/usr/local/openresty/nginx/sbin/nginx]
 0x421512 : main+0xbf2/0xc28 [/usr/local/openresty/nginx/sbin/nginx]
 0x7fa5c3a02555 : 0x7fa5c3a02555 [/usr/lib64/libc-2.17.so+0x22555/0x3c9000]
ngx_process_events_and_timers
ngx_process_events_and_timers

```





```
stap 的-d选项
-d MODULE
              Add symbol/unwind information for the given module into the kernel object module.  This may enable symbolic  trace‐
              backs from those modules/programs, even if they do not have an explicit probe placed into them.
              
--ldd  Add  symbol/unwind  information for all user-space shared libraries suspected by ldd to be necessary for user-space
              binaries being probed or listed with the -d option.  Caution: this can make the probe modules considerably  larger.
              Note that this option does not deal with kernel-space modules: see instead --all-modules below.
```

