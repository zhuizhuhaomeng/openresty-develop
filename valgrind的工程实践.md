我们都知道valgrind用于检测内存泄露非常的好用，但是如何让valgrind结合到日志的自动化测试中，而不等到遇到问题才想到用该工具来检查问题的原因。来看看openresty的良好实践吧！



# valgrind 的使用

openresty其中一种测试模式是VALGRIND模式。运行方法如下：

``` shell
export TEST_NGINX_USE_VALGRIND=1
prove -I.  t/000-sanity.t

或者
TEST_NGINX_USE_VALGRIND=1 prove -I.  t/000-sanity.t
```



# 实际的执行命令

``` shell
valgrind -q --tool=memcheck --leak-check=full --show-possibly-lost=no --num-callers=100  --gen-suppressions=all --suppressions=$pwd/valgrind.suppress nginx -p t/servroot/
```

实际上是执行上述的命令，其中：  

| 选项              | 解释                                                         |
| ----------------- | ------------------------------------------------------------ |
| -q                | 安静模式，在批量执行测试用例时候减少不必要的信息非常有用处   |
| --tool=memcheck   | valgrind可以执行很多中类型的检查(memcheck, cachegrind, callgrind, helgrind, drd,            massif, dhat, lackey, none, exp-bbv)，其中内存检查只是其中的一个是最常用的工具。 |
| --leak-check=full | 设置为full，能够显示每一块泄露的内存的调用栈 |
|--show-possibly-lost=no| 因为possibly-lost会很多，不利于自动化的处理，因此关闭输出 |
|--num-callers=100|如果调用栈深度超过100，那么最多显示100|
|--gen-suppressions=all|生成抑制输出的方法，如果认为是误报或者代码没有问题将这个调用栈加入后面的suppressions|
|--suppressions=$pwd/valgrind.suppress|指定抑制输出的配置文件|



# suppressions文件

valgrind.suppress 这个配置文件其实是非常用用处的。

1. 比如某一个内存泄露非常难于解决，但是又不会造成影响（比如只申请一次，生命周期直到进程结束的内存申请），那么就可以加入改文件。
2. 比如下面的 sendmsg(msg.msg_control)，因为没有执行memset，所以会报告使用了未初始化的内存。但是这个用法又是完全正确的，这是由msg_control的赋值方式决定会有部分空洞没有完全填充导致的。



``` txt
{
   <insert_a_suppression_name_here>
   Memcheck:Addr1
   fun:ngx_init_cycle
   fun:ngx_master_process_cycle
   fun:main
}
{
   <insert_a_suppression_name_here>
   Memcheck:Param
   sendmsg(msg.msg_control)
   fun:sendmsg
   fun:ngx_stream_lua_udp_sendmsg
   fun:ngx_stream_lua_socket_udp_send
   fun:lj_BC_FUNCC
   fun:ngx_stream_lua_run_thread
   fun:ngx_stream_lua_content_by_chunk
   fun:ngx_stream_lua_content_handler_inline
   fun:ngx_stream_lua_content_handler
   fun:ngx_stream_core_content_phase
   fun:ngx_stream_core_run_phases
   fun:ngx_stream_session_handler
   fun:ngx_stream_init_connection
   fun:ngx_event_recvmsg
   fun:ngx_epoll_process_events
   fun:ngx_process_events_and_timers
   fun:ngx_single_process_cycle
   fun:main
}
```

# 为什么调用栈不完整

有时候会发现没有行号信息甚至没有函数名，这对于调试问题非常的不利。

这种情况一般是由于编译的时候没有加入-g选项造成的，可以修改编译脚本重新编译。

如果没有安装debuginfo包也会造成调用栈不完全，安装debuginfo包即可。

# valgrind 完整选项

``` shell
[ljl@localhost home/ljl]$valgrind --help
usage: valgrind [options] prog-and-args

  tool-selection option, with default in [ ]:
    --tool=<name>             use the Valgrind tool named <name> [memcheck]

  basic user options for all Valgrind tools, with defaults in [ ]:
    -h --help                 show this message
    --help-debug              show this message, plus debugging options
    --help-dyn-options        show the dynamically changeable options
    --version                 show version
    -q --quiet                run silently; only print error msgs
    -v --verbose              be more verbose -- show misc extra info
    --trace-children=no|yes   Valgrind-ise child processes (follow execve)? [no]
    --trace-children-skip=patt1,patt2,...    specifies a list of executables
                              that --trace-children=yes should not trace into
    --trace-children-skip-by-arg=patt1,patt2,...   same as --trace-children-skip=
                              but check the argv[] entries for children, rather
                              than the exe name, to make a follow/no-follow decision
    --child-silent-after-fork=no|yes omit child output between fork & exec? [no]
    --vgdb=no|yes|full        activate gdbserver? [yes]
                              full is slower but provides precise watchpoint/step
    --vgdb-error=<number>     invoke gdbserver after <number> errors [999999999]
                              to get started quickly, use --vgdb-error=0
                              and follow the on-screen directions
    --vgdb-stop-at=event1,event2,... invoke gdbserver for given events [none]
         where event is one of:
           startup exit valgrindabexit all none
    --track-fds=no|yes        track open file descriptors? [no]
    --time-stamp=no|yes       add timestamps to log messages? [no]
    --log-fd=<number>         log messages to file descriptor [2=stderr]
    --log-file=<file>         log messages to <file>
    --log-socket=ipaddr:port  log messages to socket ipaddr:port

  user options for Valgrind tools that report errors:
    --xml=yes                 emit error output in XML (some tools only)
    --xml-fd=<number>         XML output to file descriptor
    --xml-file=<file>         XML output to <file>
    --xml-socket=ipaddr:port  XML output to socket ipaddr:port
    --xml-user-comment=STR    copy STR verbatim into XML output
    --demangle=no|yes         automatically demangle C++ names? [yes]
    --num-callers=<number>    show <number> callers in stack traces [12]
    --error-limit=no|yes      stop showing new errors if too many? [yes]
    --exit-on-first-error=no|yes exit code on the first error found? [no]
    --error-exitcode=<number> exit code to return if errors found [0=disable]
    --error-markers=<begin>,<end> add lines with begin/end markers before/after
                              each error output in plain text mode [none]
    --show-error-list=no|yes  show detected errors list and
                              suppression counts at exit [no]
    -s                        same as --show-error-list=yes
    --keep-debuginfo=no|yes   Keep symbols etc for unloaded code [no]
                              This allows saved stack traces (e.g. memory leaks)
                              to include file/line info for code that has been
                              dlclose'd (or similar)
    --show-below-main=no|yes  continue stack traces below main() [no]
    --default-suppressions=yes|no
                              load default suppressions [yes]
    --suppressions=<filename> suppress errors described in <filename>
    --gen-suppressions=no|yes|all    print suppressions for errors? [no]
    --input-fd=<number>       file descriptor for input [0=stdin]
    --dsymutil=no|yes         run dsymutil on Mac OS X when helpful? [yes]
    --max-stackframe=<number> assume stack switch for SP changes larger
                              than <number> bytes [2000000]
    --main-stacksize=<number> set size of main thread's stack (in bytes)
                              [min(max(current 'ulimit' value,1MB),16MB)]

  user options for Valgrind tools that replace malloc:
    --alignment=<number>      set minimum alignment of heap allocations [16]
    --redzone-size=<number>   set minimum size of redzones added before/after
                              heap blocks (in bytes). [16]
    --xtree-memory=none|allocs|full   profile heap memory in an xtree [none]
                              and produces a report at the end of the execution
                              none: no profiling, allocs: current allocated
                              size/blocks, full: profile current and cumulative
                              allocated size/blocks and freed size/blocks.
    --xtree-memory-file=<file>   xtree memory report file [xtmemory.kcg.%p]

  uncommon user options for all Valgrind tools:
    --fullpath-after=         (with nothing after the '=')
                              show full source paths in call stacks
    --fullpath-after=string   like --fullpath-after=, but only show the
                              part of the path after 'string'.  Allows removal
                              of path prefixes.  Use this flag multiple times
                              to specify a set of prefixes to remove.
    --extra-debuginfo-path=path    absolute path to search for additional
                              debug symbols, in addition to existing default
                              well known search paths.
    --debuginfo-server=ipaddr:port    also query this server
                              (valgrind-di-server) for debug symbols
    --allow-mismatched-debuginfo=no|yes  [no]
                              for the above two flags only, accept debuginfo
                              objects that don't "match" the main object
    --smc-check=none|stack|all|all-non-file [all-non-file]
                              checks for self-modifying code: none, only for
                              code found in stacks, for all code, or for all
                              code except that from file-backed mappings
    --read-inline-info=yes|no read debug info about inlined function calls
                              and use it to do better stack traces.
                              [yes] on Linux/Android/Solaris for the tools
                              Memcheck/Massif/Helgrind/DRD only.
                              [no] for all other tools and platforms.
    --read-var-info=yes|no    read debug info on stack and global variables
                              and use it to print better error messages in
                              tools that make use of it (Memcheck, Helgrind,
                              DRD) [no]
    --vgdb-poll=<number>      gdbserver poll max every <number> basic blocks [5000] 
    --vgdb-shadow-registers=no|yes   let gdb see the shadow registers [no]
    --vgdb-prefix=<prefix>    prefix for vgdb FIFOs [/tmp/vgdb-pipe]
    --run-libc-freeres=no|yes free up glibc memory at exit on Linux? [yes]
    --run-cxx-freeres=no|yes  free up libstdc++ memory at exit on Linux
                              and Solaris? [yes]
    --sim-hints=hint1,hint2,...  activate unusual sim behaviours [none] 
         where hint is one of:
           lax-ioctls lax-doors fuse-compatible enable-outer
           no-inner-prefix no-nptl-pthread-stackcache fallback-llsc none
    --fair-sched=no|yes|try   schedule threads fairly on multicore systems [no]
    --kernel-variant=variant1,variant2,...
         handle non-standard kernel variants [none]
         where variant is one of:
           bproc android-no-hw-tls
           android-gpu-sgx5xx android-gpu-adreno3xx none
    --merge-recursive-frames=<number>  merge frames between identical
           program counters in max <number> frames) [0]
    --num-transtab-sectors=<number> size of translated code cache [32]
           more sectors may increase performance, but use more memory.
    --avg-transtab-entry-size=<number> avg size in bytes of a translated
           basic block [0, meaning use tool provided default]
    --aspace-minaddr=0xPP     avoid mapping memory below 0xPP [guessed]
    --valgrind-stacksize=<number> size of valgrind (host) thread's stack
                               (in bytes) [1048576]
    --show-emwarns=no|yes     show warnings about emulation limits? [no]
    --require-text-symbol=:sonamepattern:symbolpattern    abort run if the
                              stated shared object doesn't have the stated
                              text symbol.  Patterns can contain ? and *.
    --soname-synonyms=syn1=pattern1,syn2=pattern2,... synonym soname
              specify patterns for function wrapping or replacement.
              To use a non-libc malloc library that is
                  in the main exe:  --soname-synonyms=somalloc=NONE
                  in libxyzzy.so:   --soname-synonyms=somalloc=libxyzzy.so
    --sigill-diagnostics=yes|no  warn about illegal instructions? [yes]
    --unw-stack-scan-thresh=<number>   Enable stack-scan unwind if fewer
                  than <number> good frames found  [0, meaning "disabled"]
                  NOTE: stack scanning is only available on arm-linux.
    --unw-stack-scan-frames=<number>   Max number of frames that can be
                  recovered by stack scanning [5]
    --resync-filter=no|yes|verbose [yes on MacOS, no on other OSes]
              attempt to avoid expensive address-space-resync operations
    --max-threads=<number>    maximum number of threads that valgrind can
                              handle [500]

  user options for Memcheck:
    --leak-check=no|summary|full     search for memory leaks at exit?  [summary]
    --leak-resolution=low|med|high   differentiation of leak stack traces [high]
    --show-leak-kinds=kind1,kind2,.. which leak kinds to show?
                                            [definite,possible]
    --errors-for-leak-kinds=kind1,kind2,..  which leak kinds are errors?
                                            [definite,possible]
        where kind is one of:
          definite indirect possible reachable all none
    --leak-check-heuristics=heur1,heur2,... which heuristics to use for
        improving leak search false positive [all]
        where heur is one of:
          stdstring length64 newarray multipleinheritance all none
    --show-reachable=yes             same as --show-leak-kinds=all
    --show-reachable=no --show-possibly-lost=yes
                                     same as --show-leak-kinds=definite,possible
    --show-reachable=no --show-possibly-lost=no
                                     same as --show-leak-kinds=definite
    --xtree-leak=no|yes              output leak result in xtree format? [no]
    --xtree-leak-file=<file>         xtree leak report file [xtleak.kcg.%p]
    --undef-value-errors=no|yes      check for undefined value errors [yes]
    --track-origins=no|yes           show origins of undefined values? [no]
    --partial-loads-ok=no|yes        too hard to explain here; see manual [yes]
    --expensive-definedness-checks=no|auto|yes
                                     Use extra-precise definedness tracking [auto]
    --freelist-vol=<number>          volume of freed blocks queue     [20000000]
    --freelist-big-blocks=<number>   releases first blocks with size>= [1000000]
    --workaround-gcc296-bugs=no|yes  self explanatory [no].  Deprecated.
                                     Use --ignore-range-below-sp instead.
    --ignore-ranges=0xPP-0xQQ[,0xRR-0xSS]   assume given addresses are OK
    --ignore-range-below-sp=<number>-<number>  do not report errors for
                                     accesses at the given offsets below SP
    --malloc-fill=<hexnumber>        fill malloc'd areas with given value
    --free-fill=<hexnumber>          fill free'd areas with given value
    --keep-stacktraces=alloc|free|alloc-and-free|alloc-then-free|none
        stack trace(s) to keep for malloc'd/free'd areas       [alloc-and-free]
    --show-mismatched-frees=no|yes   show frees that don't match the allocator? [yes]

  Extra options read from ~/.valgrindrc, $VALGRIND_OPTS, ./.valgrindrc

  Memcheck is Copyright (C) 2002-2017, and GNU GPL'd, by Julian Seward et al.
  Valgrind is Copyright (C) 2000-2017, and GNU GPL'd, by Julian Seward et al.
  LibVEX is Copyright (C) 2004-2017, and GNU GPL'd, by OpenWorks LLP et al.

  Bug reports, feedback, admiration, abuse, etc, to: www.valgrind.org.

```

