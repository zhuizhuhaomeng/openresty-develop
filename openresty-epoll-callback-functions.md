# epoll

## ngx_event_actions的epoll 函数

(gdb) print ngx_event_actions
$2 = {
  add = ngx_epoll_add_event,
  del =  ngx_epoll_del_event,
  enable =  ngx_epoll_add_event,
  disable =  ngx_epoll_del_event,
  add_conn =  ngx_epoll_add_connection,
  del_conn =ngx_epoll_del_connection,
  notify =  ngx_epoll_notify,
  process_events =  ngx_epoll_process_events,
  init =  ngx_epoll_init,
  done =  ngx_epoll_done
}