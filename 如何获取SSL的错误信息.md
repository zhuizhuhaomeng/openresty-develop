# 为什么要打印错误

当我们遇到问题的时候，我们总希望知道详细的原因，以便快速的解决问题。以SSL_do_handshake为例子分析如何输出ssl的错误信息。

# SSL错误打印的基本过程

通过man  SSL_do_handshake 查看手册了解返回值含义

```
RETURN VALUES
       The following return values can occur:

       0   The TLS/SSL handshake was not successful but was shut down controlled and by the specifications of the TLS/SSL
           protocol. Call SSL_get_error() with the return value ret to find out the reason.

       1   The TLS/SSL handshake was successfully completed, a TLS/SSL connection has been established.

       <0  The TLS/SSL handshake was not successful because a fatal error occurred either at the protocol level or a connection
           failure occurred. The shutdown was not clean. It can also occur of action is need to continue the operation for non-
           blocking BIOs. Call SSL_get_error() with the return value ret to find out the reason.

```



1. ngx_ssl_clear_error(c->log) 清除上一次遗留的错误，比如异步情况下上一次返回重试的错误

2. n = SSL_do_handshake(c->ssl->connection) 执行握手

3. n == 1是成功的情况，做相应处理

4. n != 1时调用sslerr = SSL_get_error(c->ssl->connection, n)获取sslerr的错误信息

   1. sslerr == SSL_ERROR_WANT_READ 或者 sslerr == SSL_ERROR_WANT_WRITE是异步处理的正常情况，等待后续事件触发后继续处理

   2. sslerr == SSL_ERROR_SYSCALL，那边err = errno，获取系统调用错误类型

   3. ```c
      if (sslerr == SSL_ERROR_ZERO_RETURN || ERR_peek_error() == 0) {
          ngx_connection_error(c, err,
                               "peer closed connection in SSL handshake");
      
          return NGX_ERROR;
      }
      ```

   4. 日志等级默认为 NGX_LOG_CRIT
   5. sslerr == SSL_ERROR_SYSCALL，判断是网络相关事件，调整日志等级为NGX_LOG_INFO或者NGX_LOG_ERR
   6. sslerr == SSL_ERROR_SSL ，判断是SSL相关的事件，调整日志等级为NGX_LOG_INFO或者NGX_LOG_ERR
   7. 循环调用ERR_peek_error_line_data、ERR_error_string_n和ERR_get_error输出所有的ssl错误信息



可以看到几个函数 

ERR_peek_error

ERR_peek_error_line_data

ERR_error_string_n

ERR_get_error

同样查看手册可知ssl的错误是存储在队列中的，没有提供遍历错误队列的函数，只能把错误弹出才能够继续看下一个错误。

```
       ERR_get_error() returns the earliest error code from the thread's error queue and removes the entry. This function can be
       called repeatedly until there are no more error codes to return.

       ERR_peek_error() returns the earliest error code from the thread's error queue without modifying it.

       ERR_peek_last_error() returns the latest error code from the thread's error queue without modifying it.

       See ERR_GET_LIB(3) for obtaining information about location and reason of the error, and ERR_error_string(3) for human-
       readable error messages.

       ERR_get_error_line(), ERR_peek_error_line() and ERR_peek_last_error_line() are the same as the above, but they
       additionally store the file name and line number where the error occurred in *file and *line, unless these are NULL.

       ERR_get_error_line_data(), ERR_peek_error_line_data() and ERR_peek_last_error_line_data() store additional data and flags
       associated with the error code in *data and *flags, unless these are NULL. *data contains a string if
       *flags&ERR_TXT_STRING is true.

```





# ngx_ssl_handshare

```c
ngx_int_t
ngx_ssl_handshake(ngx_connection_t *c)
{
    int        n, sslerr;
    ngx_err_t  err;
    ngx_int_t  rc;

#ifdef SSL_READ_EARLY_DATA_SUCCESS
    if (c->ssl->try_early_data) {
        return ngx_ssl_try_early_data(c);
    }
#endif

    if (c->ssl->in_ocsp) {
        return ngx_ssl_ocsp_validate(c);
    }

    ngx_ssl_clear_error(c->log);

    n = SSL_do_handshake(c->ssl->connection);

    ngx_log_debug1(NGX_LOG_DEBUG_EVENT, c->log, 0, "SSL_do_handshake: %d", n);

    if (n == 1) {

        if (ngx_handle_read_event(c->read, 0) != NGX_OK) {
            return NGX_ERROR;
        }

        if (ngx_handle_write_event(c->write, 0) != NGX_OK) {
            return NGX_ERROR;
        }

#if (NGX_DEBUG)
        ngx_ssl_handshake_log(c);
#endif

        c->recv = ngx_ssl_recv;
        c->send = ngx_ssl_write;
        c->recv_chain = ngx_ssl_recv_chain;
        c->send_chain = ngx_ssl_send_chain;

#ifndef SSL_OP_NO_RENEGOTIATION
#if OPENSSL_VERSION_NUMBER < 0x10100000L
#ifdef SSL3_FLAGS_NO_RENEGOTIATE_CIPHERS

        /* initial handshake done, disable renegotiation (CVE-2009-3555) */
        if (c->ssl->connection->s3 && SSL_is_server(c->ssl->connection)) {
            c->ssl->connection->s3->flags |= SSL3_FLAGS_NO_RENEGOTIATE_CIPHERS;
        }

#endif
#endif
#endif

        rc = ngx_ssl_ocsp_validate(c);

        if (rc == NGX_ERROR) {
            return NGX_ERROR;
        }

        if (rc == NGX_AGAIN) {
            c->read->handler = ngx_ssl_handshake_handler;
            c->write->handler = ngx_ssl_handshake_handler;
            return NGX_AGAIN;
        }

        c->ssl->handshaked = 1;

        return NGX_OK;
    }

    sslerr = SSL_get_error(c->ssl->connection, n);

    ngx_log_debug1(NGX_LOG_DEBUG_EVENT, c->log, 0, "SSL_get_error: %d", sslerr);

    if (sslerr == SSL_ERROR_WANT_READ) {
        c->read->ready = 0;
        c->read->handler = ngx_ssl_handshake_handler;
        c->write->handler = ngx_ssl_handshake_handler;

        if (ngx_handle_read_event(c->read, 0) != NGX_OK) {
            return NGX_ERROR;
        }

        if (ngx_handle_write_event(c->write, 0) != NGX_OK) {
            return NGX_ERROR;
        }

        return NGX_AGAIN;
    }

    if (sslerr == SSL_ERROR_WANT_WRITE) {
        c->write->ready = 0;
        c->read->handler = ngx_ssl_handshake_handler;
        c->write->handler = ngx_ssl_handshake_handler;

        if (ngx_handle_read_event(c->read, 0) != NGX_OK) {
            return NGX_ERROR;
        }

        if (ngx_handle_write_event(c->write, 0) != NGX_OK) {
            return NGX_ERROR;
        }

        return NGX_AGAIN;
    }

    err = (sslerr == SSL_ERROR_SYSCALL) ? ngx_errno : 0;

    c->ssl->no_wait_shutdown = 1;
    c->ssl->no_send_shutdown = 1;
    c->read->eof = 1;

    if (sslerr == SSL_ERROR_ZERO_RETURN || ERR_peek_error() == 0) {
        ngx_connection_error(c, err,
                             "peer closed connection in SSL handshake");

        return NGX_ERROR;
    }

    c->read->error = 1;

    ngx_ssl_connection_error(c, sslerr, err, "SSL_do_handshake() failed");

    return NGX_ERROR;
}
```



# ngx_ssl_connection_error

```c
static void
ngx_ssl_connection_error(ngx_connection_t *c, int sslerr, ngx_err_t err,
    char *text)
{
    int         n;
    ngx_uint_t  level;

    level = NGX_LOG_CRIT;

    if (sslerr == SSL_ERROR_SYSCALL) {

        if (err == NGX_ECONNRESET
#if (NGX_WIN32)
            || err == NGX_ECONNABORTED
#endif
            || err == NGX_EPIPE
            || err == NGX_ENOTCONN
            || err == NGX_ETIMEDOUT
            || err == NGX_ECONNREFUSED
            || err == NGX_ENETDOWN
            || err == NGX_ENETUNREACH
            || err == NGX_EHOSTDOWN
            || err == NGX_EHOSTUNREACH)
        {
            switch (c->log_error) {

            case NGX_ERROR_IGNORE_ECONNRESET:
            case NGX_ERROR_INFO:
                level = NGX_LOG_INFO;
                break;

            case NGX_ERROR_ERR:
                level = NGX_LOG_ERR;
                break;

            default:
                break;
            }
        }

    } else if (sslerr == SSL_ERROR_SSL) {

        n = ERR_GET_REASON(ERR_peek_error());

            /* handshake failures */
        if (n == SSL_R_BAD_CHANGE_CIPHER_SPEC                        /*  103 */
#ifdef SSL_R_NO_SUITABLE_KEY_SHARE
            || n == SSL_R_NO_SUITABLE_KEY_SHARE                      /*  101 */
#endif
#ifdef SSL_R_NO_SUITABLE_SIGNATURE_ALGORITHM
            || n == SSL_R_NO_SUITABLE_SIGNATURE_ALGORITHM            /*  118 */
#endif
            || n == SSL_R_BLOCK_CIPHER_PAD_IS_WRONG                  /*  129 */
            || n == SSL_R_DIGEST_CHECK_FAILED                        /*  149 */
            || n == SSL_R_ERROR_IN_RECEIVED_CIPHER_LIST              /*  151 */
            || n == SSL_R_EXCESSIVE_MESSAGE_SIZE                     /*  152 */
            || n == SSL_R_HTTPS_PROXY_REQUEST                        /*  155 */
            || n == SSL_R_HTTP_REQUEST                               /*  156 */
            || n == SSL_R_LENGTH_MISMATCH                            /*  159 */
#ifdef SSL_R_NO_CIPHERS_PASSED
            || n == SSL_R_NO_CIPHERS_PASSED                          /*  182 */
#endif
            || n == SSL_R_NO_CIPHERS_SPECIFIED                       /*  183 */
            || n == SSL_R_NO_COMPRESSION_SPECIFIED                   /*  187 */
            || n == SSL_R_NO_SHARED_CIPHER                           /*  193 */
            || n == SSL_R_RECORD_LENGTH_MISMATCH                     /*  213 */
#ifdef SSL_R_CLIENTHELLO_TLSEXT
            || n == SSL_R_CLIENTHELLO_TLSEXT                         /*  226 */
#endif
#ifdef SSL_R_PARSE_TLSEXT
            || n == SSL_R_PARSE_TLSEXT                               /*  227 */
#endif
#ifdef SSL_R_CALLBACK_FAILED
            || n == SSL_R_CALLBACK_FAILED                            /*  234 */
#endif
            || n == SSL_R_UNEXPECTED_MESSAGE                         /*  244 */
            || n == SSL_R_UNEXPECTED_RECORD                          /*  245 */
            || n == SSL_R_UNKNOWN_ALERT_TYPE                         /*  246 */
            || n == SSL_R_UNKNOWN_PROTOCOL                           /*  252 */
#ifdef SSL_R_NO_COMMON_SIGNATURE_ALGORITHMS
            || n == SSL_R_NO_COMMON_SIGNATURE_ALGORITHMS             /*  253 */
#endif
            || n == SSL_R_UNSUPPORTED_PROTOCOL                       /*  258 */
#ifdef SSL_R_NO_SHARED_GROUP
            || n == SSL_R_NO_SHARED_GROUP                            /*  266 */
#endif
            || n == SSL_R_WRONG_VERSION_NUMBER                       /*  267 */
            || n == SSL_R_DECRYPTION_FAILED_OR_BAD_RECORD_MAC        /*  281 */
#ifdef SSL_R_RENEGOTIATE_EXT_TOO_LONG
            || n == SSL_R_RENEGOTIATE_EXT_TOO_LONG                   /*  335 */
            || n == SSL_R_RENEGOTIATION_ENCODING_ERR                 /*  336 */
            || n == SSL_R_RENEGOTIATION_MISMATCH                     /*  337 */
#endif
#ifdef SSL_R_UNSAFE_LEGACY_RENEGOTIATION_DISABLED
            || n == SSL_R_UNSAFE_LEGACY_RENEGOTIATION_DISABLED       /*  338 */
#endif
#ifdef SSL_R_SCSV_RECEIVED_WHEN_RENEGOTIATING
            || n == SSL_R_SCSV_RECEIVED_WHEN_RENEGOTIATING           /*  345 */
#endif
#ifdef SSL_R_INAPPROPRIATE_FALLBACK
            || n == SSL_R_INAPPROPRIATE_FALLBACK                     /*  373 */
#endif
#ifdef SSL_R_CERT_CB_ERROR
            || n == SSL_R_CERT_CB_ERROR                              /*  377 */
#endif
#ifdef SSL_R_VERSION_TOO_LOW
            || n == SSL_R_VERSION_TOO_LOW                            /*  396 */
#endif
            || n == 1000 /* SSL_R_SSLV3_ALERT_CLOSE_NOTIFY */
#ifdef SSL_R_SSLV3_ALERT_UNEXPECTED_MESSAGE
            || n == SSL_R_SSLV3_ALERT_UNEXPECTED_MESSAGE             /* 1010 */
            || n == SSL_R_SSLV3_ALERT_BAD_RECORD_MAC                 /* 1020 */
            || n == SSL_R_TLSV1_ALERT_DECRYPTION_FAILED              /* 1021 */
            || n == SSL_R_TLSV1_ALERT_RECORD_OVERFLOW                /* 1022 */
            || n == SSL_R_SSLV3_ALERT_DECOMPRESSION_FAILURE          /* 1030 */
            || n == SSL_R_SSLV3_ALERT_HANDSHAKE_FAILURE              /* 1040 */
            || n == SSL_R_SSLV3_ALERT_NO_CERTIFICATE                 /* 1041 */
            || n == SSL_R_SSLV3_ALERT_BAD_CERTIFICATE                /* 1042 */
            || n == SSL_R_SSLV3_ALERT_UNSUPPORTED_CERTIFICATE        /* 1043 */
            || n == SSL_R_SSLV3_ALERT_CERTIFICATE_REVOKED            /* 1044 */
            || n == SSL_R_SSLV3_ALERT_CERTIFICATE_EXPIRED            /* 1045 */
            || n == SSL_R_SSLV3_ALERT_CERTIFICATE_UNKNOWN            /* 1046 */
            || n == SSL_R_SSLV3_ALERT_ILLEGAL_PARAMETER              /* 1047 */
            || n == SSL_R_TLSV1_ALERT_UNKNOWN_CA                     /* 1048 */
            || n == SSL_R_TLSV1_ALERT_ACCESS_DENIED                  /* 1049 */
            || n == SSL_R_TLSV1_ALERT_DECODE_ERROR                   /* 1050 */
            || n == SSL_R_TLSV1_ALERT_DECRYPT_ERROR                  /* 1051 */
            || n == SSL_R_TLSV1_ALERT_EXPORT_RESTRICTION             /* 1060 */
            || n == SSL_R_TLSV1_ALERT_PROTOCOL_VERSION               /* 1070 */
            || n == SSL_R_TLSV1_ALERT_INSUFFICIENT_SECURITY          /* 1071 */
            || n == SSL_R_TLSV1_ALERT_INTERNAL_ERROR                 /* 1080 */
            || n == SSL_R_TLSV1_ALERT_USER_CANCELLED                 /* 1090 */
            || n == SSL_R_TLSV1_ALERT_NO_RENEGOTIATION               /* 1100 */
#endif
            )
        {
            switch (c->log_error) {

            case NGX_ERROR_IGNORE_ECONNRESET:
            case NGX_ERROR_INFO:
                level = NGX_LOG_INFO;
                break;

            case NGX_ERROR_ERR:
                level = NGX_LOG_ERR;
                break;

            default:
                break;
            }
        }
    }

    ngx_ssl_error(level, c->log, err, text);
}
```





# ngx_ssl_error

```
void ngx_cdecl
ngx_ssl_error(ngx_uint_t level, ngx_log_t *log, ngx_err_t err, char *fmt, ...)
{
    int          flags;
    u_long       n;
    va_list      args;
    u_char      *p, *last;
    u_char       errstr[NGX_MAX_CONF_ERRSTR];
    const char  *data;

    last = errstr + NGX_MAX_CONF_ERRSTR;

    va_start(args, fmt);
    p = ngx_vslprintf(errstr, last - 1, fmt, args);
    va_end(args);

    if (ERR_peek_error()) {
        p = ngx_cpystrn(p, (u_char *) " (SSL:", last - p);

        for ( ;; ) {

            n = ERR_peek_error_line_data(NULL, NULL, &data, &flags);

            if (n == 0) {
                break;
            }

            /* ERR_error_string_n() requires at least one byte */

            if (p >= last - 1) {
                goto next;
            }

            *p++ = ' ';

            ERR_error_string_n(n, (char *) p, last - p);

            while (p < last && *p) {
                p++;
            }

            if (p < last && *data && (flags & ERR_TXT_STRING)) {
                *p++ = ':';
                p = ngx_cpystrn(p, (u_char *) data, last - p);
            }

        next:

            (void) ERR_get_error();
        }

        if (p < last) {
            *p++ = ')';
        }
    }

    ngx_log_error(level, log, err, "%*s", p - errstr, errstr);
}
```