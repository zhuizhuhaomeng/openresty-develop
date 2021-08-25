开源软件一般都会为了兼容各种不同的操作系统、不同的依赖软件版本、调试等目的而定义很多的宏来达到目录。这给代码阅读带来了很多的障碍。

下面以lmdb/libraries/liblmdb为例分析如何确认系统具体使用哪个宏。

```C
#ifdef _WIN32
#define MDB_USE_HASH	1
#define MDB_PIDLOCK	0
#define THREAD_RET	DWORD
#define pthread_t	HANDLE
#define pthread_mutex_t	HANDLE
#define pthread_cond_t	HANDLE
typedef HANDLE mdb_mutex_t, mdb_mutexref_t;
#define pthread_key_t	DWORD
#define pthread_self()	GetCurrentThreadId()
#define pthread_key_create(x,y)	\
	((*(x) = TlsAlloc()) == TLS_OUT_OF_INDEXES ? ErrCode() : 0)
#define pthread_key_delete(x)	TlsFree(x)
#define pthread_getspecific(x)	TlsGetValue(x)
#define pthread_setspecific(x,y)	(TlsSetValue(x,y) ? 0 : ErrCode())
#define pthread_mutex_unlock(x)	ReleaseMutex(*x)
#define pthread_mutex_lock(x)	WaitForSingleObject(*x, INFINITE)
#define pthread_cond_signal(x)	SetEvent(*x)
#define pthread_cond_wait(cond,mutex)	do{SignalObjectAndWait(*mutex, *cond, INFINITE, FALSE); WaitForSingleObject(*mutex, INFINITE);}while(0)
#define THREAD_CREATE(thr,start,arg) \
	(((thr) = CreateThread(NULL, 0, start, arg, 0, NULL)) ? 0 : ErrCode())
#define THREAD_FINISH(thr) \
	(WaitForSingleObject(thr, INFINITE) ? ErrCode() : 0)
#define LOCK_MUTEX0(mutex)		WaitForSingleObject(mutex, INFINITE)
#define UNLOCK_MUTEX(mutex)		ReleaseMutex(mutex)
#define mdb_mutex_consistent(mutex)	0
#define getpid()	GetCurrentProcessId()
#define	MDB_FDATASYNC(fd)	(!FlushFileBuffers(fd))
#define	MDB_MSYNC(addr,len,flags)	(!FlushViewOfFile(addr,len))
#define	ErrCode()	GetLastError()
#define GET_PAGESIZE(x) {SYSTEM_INFO si; GetSystemInfo(&si); (x) = si.dwPageSize;}
#define	close(fd)	(CloseHandle(fd) ? 0 : -1)
#define	munmap(ptr,len)	UnmapViewOfFile(ptr)
#ifdef PROCESS_QUERY_LIMITED_INFORMATION
#define MDB_PROCESS_QUERY_LIMITED_INFORMATION PROCESS_QUERY_LIMITED_INFORMATION
#else
#define MDB_PROCESS_QUERY_LIMITED_INFORMATION 0x1000
#endif
#else
#define THREAD_RET	void *
#define THREAD_CREATE(thr,start,arg)	pthread_create(&thr,NULL,start,arg)
#define THREAD_FINISH(thr)	pthread_join(thr,NULL)

	/** For MDB_LOCK_FORMAT: True if readers take a pid lock in the lockfile */
#define MDB_PIDLOCK			1

#ifdef MDB_USE_POSIX_SEM

typedef sem_t *mdb_mutex_t, *mdb_mutexref_t;
#define LOCK_MUTEX0(mutex)		mdb_sem_wait(mutex)
#define UNLOCK_MUTEX(mutex)		sem_post(mutex)

static int
mdb_sem_wait(sem_t *sem)
{
   int rc;
   while ((rc = sem_wait(sem)) && (rc = errno) == EINTR) ;
   return rc;
}

#elif defined MDB_USE_SYSV_SEM

typedef struct mdb_mutex {
	int semid;
	int semnum;
	int *locked;
} mdb_mutex_t[1], *mdb_mutexref_t;

#define LOCK_MUTEX0(mutex)		mdb_sem_wait(mutex)
#define UNLOCK_MUTEX(mutex)		do { \
	struct sembuf sb = { 0, 1, SEM_UNDO }; \
	sb.sem_num = (mutex)->semnum; \
	*(mutex)->locked = 0; \
	semop((mutex)->semid, &sb, 1); \
} while(0)

static int
mdb_sem_wait(mdb_mutexref_t sem)
{
	int rc, *locked = sem->locked;
	struct sembuf sb = { 0, -1, SEM_UNDO };
	sb.sem_num = sem->semnum;
	do {
		if (!semop(sem->semid, &sb, 1)) {
			rc = *locked ? MDB_OWNERDEAD : MDB_SUCCESS;
			*locked = 1;
			break;
		}
	} while ((rc = errno) == EINTR);
	return rc;
}

#define mdb_mutex_consistent(mutex)	0

#else	/* MDB_USE_POSIX_MUTEX: */
	/** Shared mutex/semaphore as the original is stored.
	 *
	 *	Not for copies.  Instead it can be assigned to an #mdb_mutexref_t.
	 *	When mdb_mutexref_t is a pointer and mdb_mutex_t is not, then it
	 *	is array[size 1] so it can be assigned to the pointer.
	 */
typedef pthread_mutex_t mdb_mutex_t[1];
	/** Reference to an #mdb_mutex_t */
typedef pthread_mutex_t *mdb_mutexref_t;
	/** Lock the reader or writer mutex.
	 *	Returns 0 or a code to give #mdb_mutex_failed(), as in #LOCK_MUTEX().
	 */
#define LOCK_MUTEX0(mutex)	pthread_mutex_lock(mutex)
	/** Unlock the reader or writer mutex.
	 */
#define UNLOCK_MUTEX(mutex)	pthread_mutex_unlock(mutex)
	/** Mark mutex-protected data as repaired, after death of previous owner.
	 */
#define mdb_mutex_consistent(mutex)	pthread_mutex_consistent(mutex)
#endif	/* MDB_USE_POSIX_SEM || MDB_USE_SYSV_SEM */

	/** Get the error code for the last failed system function.
	 */
#define	ErrCode()	errno

	/** An abstraction for a file handle.
	 *	On POSIX systems file handles are small integers. On Windows
	 *	they're opaque pointers.
	 */
#define	HANDLE	int

	/**	A value for an invalid file handle.
	 *	Mainly used to initialize file variables and signify that they are
	 *	unused.
	 */
#define INVALID_HANDLE_VALUE	(-1)

	/** Get the size of a memory page for the system.
	 *	This is the basic size that the platform's memory manager uses, and is
	 *	fundamental to the use of memory-mapped files.
	 */
#define	GET_PAGESIZE(x)	((x) = sysconf(_SC_PAGE_SIZE))
#endif
```



编译软件加上 -g3

```shell
make XCFLAGS=-g3
```

objdump 导出宏

```sh
[ljl@localhost liblmdb]$ objdump --dwarf=macro liblmdb.so  | grep LOCK_MUTEX0
 DW_MACRO_define_strp - lineno : 442 macro : LOCK_MUTEX0(mutex) pthread_mutex_lock(mutex)
 DW_MACRO_define_strp - lineno : 499 macro : LOCK_MUTEX(rc,env,mutex) (((rc) = LOCK_MUTEX0(mutex)) && ((rc) = mdb_mutex_failed(env, mutex, rc)))
```

