
# EPOLLET mode
## epoll-all-read
If receive buffer is smaller than the data of the client sent,
should read multiple times.

## epoll-part-read
If receive buffer is smaller than the data of the client sent,
read part of the data and epoll_wait again, the process will be blocked.

## epoll-part-read-retrigger
If receive buffer is smaller than the data of the client sent,
read part of the data and epoll_wait again, the process will be blocked.
After another client packet sent from client, epoll_wait return. Now kernel buffer
contains both the old data and the new received data.

## epoll-part-read-oneshot
With EPOLLONESHORT, when part of data was not read by the first trigger, the latter
data arrival will not tirgger the epoll_wait return.

# EPOLL LT module
## epoll-part-read-lt
If receive buffer is smaller than the data of the client sent,
read part of the data and epoll_wait again, epoll_wait will return immediately.