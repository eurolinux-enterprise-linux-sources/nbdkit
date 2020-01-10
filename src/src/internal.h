/* nbdkit
 * Copyright (C) 2013-2018 Red Hat Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 * * Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *
 * * Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 *
 * * Neither the name of Red Hat nor the names of its contributors may be
 * used to endorse or promote products derived from this software without
 * specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY RED HAT AND CONTRIBUTORS ''AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
 * PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL RED HAT OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */

#ifndef NBDKIT_INTERNAL_H
#define NBDKIT_INTERNAL_H

#include <stdbool.h>
#include <stddef.h>
#include <stdarg.h>
#include <sys/socket.h>
#include <pthread.h>

#include "nbdkit-plugin.h"
#include "nbdkit-filter.h"

#ifdef __APPLE__
#define UNIX_PATH_MAX 104
#else
#define UNIX_PATH_MAX 108
#endif

#ifndef O_CLOEXEC
#define O_CLOEXEC 0
#endif

#ifndef SOCK_CLOEXEC
#define SOCK_CLOEXEC 0
#endif

#ifndef htobe32
#include <byteswap.h>
# if __BYTE_ORDER == __LITTLE_ENDIAN
#  define htobe16(x) __bswap_16 (x)
#  define htole16(x) (x)
#  define be16toh(x) __bswap_16 (x)
#  define le16toh(x) (x)

#  define htobe32(x) __bswap_32 (x)
#  define htole32(x) (x)
#  define be32toh(x) __bswap_32 (x)
#  define le32toh(x) (x)

#  define htobe64(x) __bswap_64 (x)
#  define htole64(x) (x)
#  define be64toh(x) __bswap_64 (x)
#  define le64toh(x) (x)

# else
#  define htobe16(x) (x)
#  define htole16(x) __bswap_16 (x)
#  define be16toh(x) (x)
#  define le16toh(x) __bswap_16 (x)

#  define htobe32(x) (x)
#  define htole32(x) __bswap_32 (x)
#  define be32toh(x) (x)
#  define le32toh(x) __bswap_32 (x)

#  define htobe64(x) (x)
#  define htole64(x) __bswap_64 (x)
#  define be64toh(x) (x)
#  define le64toh(x) __bswap_64 (x)
# endif
#endif

#define container_of(ptr, type, member) ({                       \
      const typeof (((type *) 0)->member) *__mptr = (ptr);       \
      (type *) ((char *) __mptr - offsetof(type, member));       \
    })

#define NBDKIT_FLAG_MAY_TRIM (1<<0) /* Maps to !NBD_CMD_FLAG_NO_HOLE */
#define NBDKIT_FLAG_FUA      (1<<1) /* Maps to NBD_CMD_FLAG_FUA */

/* main.c */
extern const char *exportname;
extern const char *ipaddr;
extern int newstyle;
extern const char *port;
extern int readonly;
extern const char *selinux_label;
extern int tls;
extern const char *tls_certificates_dir;
extern int tls_verify_peer;
extern char *unixsocket;
extern int verbose;
extern int threads;

extern volatile int quit;
extern int quit_fd;

extern struct backend *backend;
#define for_each_backend(b) for (b = backend; b != NULL; b = b->next)

/* cleanup.c */
extern void cleanup_free (void *ptr);
#define CLEANUP_FREE __attribute__((cleanup (cleanup_free)))
extern void cleanup_unlock (pthread_mutex_t **ptr);
#define CLEANUP_UNLOCK __attribute__((cleanup (cleanup_unlock)))
#define ACQUIRE_LOCK_FOR_CURRENT_SCOPE(mutex) \
  CLEANUP_UNLOCK pthread_mutex_t *_lock = mutex; \
  pthread_mutex_lock (_lock)

/* connections.c */
struct connection;
typedef int (*connection_recv_function) (struct connection *, void *buf, size_t len);
typedef int (*connection_send_function) (struct connection *, const void *buf, size_t len);
typedef void (*connection_close_function) (struct connection *);
extern int handle_single_connection (int sockin, int sockout);
extern int connection_set_handle (struct connection *conn, size_t i, void *handle);
extern void *connection_get_handle (struct connection *conn, size_t i);
extern pthread_mutex_t *connection_get_request_lock (struct connection *conn);
extern void connection_set_crypto_session (struct connection *conn, void *session);
extern void *connection_get_crypto_session (struct connection *conn);
extern void connection_set_recv (struct connection *, connection_recv_function);
extern void connection_set_send (struct connection *, connection_send_function);
extern void connection_set_close (struct connection *, connection_close_function);

/* crypto.c */
#define root_tls_certificates_dir sysconfdir "/pki/" PACKAGE_NAME
extern void crypto_init (int tls_set_on_cli);
extern void crypto_free (void);
extern int crypto_negotiate_tls (struct connection *conn, int sockin, int sockout);

/* errors.c */
#define debug nbdkit_debug

struct backend {
  /* Next filter or plugin in the chain.  This is always NULL for
   * plugins and never NULL for filters.
   */
  struct backend *next;

  /* A unique index used to fetch the handle from the connections
   * object.  The plugin (last in the chain) has index 0, and the
   * filters have index 1, 2, ... depending how "far" they are from
   * the plugin.
   */
  size_t i;

  void (*free) (struct backend *);
  int (*thread_model) (struct backend *);
  const char *(*name) (struct backend *);
  const char *(*plugin_name) (struct backend *);
  void (*usage) (struct backend *);
  const char *(*version) (struct backend *);
  void (*dump_fields) (struct backend *);
  void (*config) (struct backend *, const char *key, const char *value);
  void (*config_complete) (struct backend *);
  int (*errno_is_preserved) (struct backend *);
  int (*open) (struct backend *, struct connection *conn, int readonly);
  int (*prepare) (struct backend *, struct connection *conn);
  int (*finalize) (struct backend *, struct connection *conn);
  void (*close) (struct backend *, struct connection *conn);
  int64_t (*get_size) (struct backend *, struct connection *conn);
  int (*can_write) (struct backend *, struct connection *conn);
  int (*can_flush) (struct backend *, struct connection *conn);
  int (*is_rotational) (struct backend *, struct connection *conn);
  int (*can_trim) (struct backend *, struct connection *conn);
  int (*pread) (struct backend *, struct connection *conn, void *buf, uint32_t count, uint64_t offset, uint32_t flags);
  int (*pwrite) (struct backend *, struct connection *conn, const void *buf, uint32_t count, uint64_t offset, uint32_t flags);
  int (*flush) (struct backend *, struct connection *conn, uint32_t flags);
  int (*trim) (struct backend *, struct connection *conn, uint32_t count, uint64_t offset, uint32_t flags);
  int (*zero) (struct backend *, struct connection *conn, uint32_t count, uint64_t offset, uint32_t flags);
};

/* plugins.c */
extern struct backend *plugin_register (size_t index, const char *filename, void *dl, struct nbdkit_plugin *(*plugin_init) (void));

/* filters.c */
extern struct backend *filter_register (struct backend *next, size_t index, const char *filename, void *dl, struct nbdkit_filter *(*filter_init) (void));

/* locks.c */
extern void lock_init_thread_model (void);
extern void lock_connection (void);
extern void unlock_connection (void);
extern void lock_request (struct connection *conn);
extern void unlock_request (struct connection *conn);
extern void lock_unload (void);
extern void unlock_unload (void);

/* sockets.c */
extern int *bind_unix_socket (size_t *);
extern int *bind_tcpip_socket (size_t *);
extern void accept_incoming_connections (int *socks, size_t nr_socks);
extern void free_listening_sockets (int *socks, size_t nr_socks);

/* threadlocal.c */
extern void threadlocal_init (void);
extern void threadlocal_new_server_thread (void);
extern void threadlocal_set_name (const char *name);
extern void threadlocal_set_instance_num (size_t instance_num);
extern void threadlocal_set_sockaddr (struct sockaddr *addr, socklen_t addrlen);
extern const char *threadlocal_get_name (void);
extern size_t threadlocal_get_instance_num (void);
extern void threadlocal_set_error (int err);
extern int threadlocal_get_error (void);
/*extern void threadlocal_get_sockaddr ();*/

/* Declare program_name. */
#if HAVE_DECL_PROGRAM_INVOCATION_SHORT_NAME == 1
#include <errno.h>
#define program_name program_invocation_short_name
#else
#define program_name "nbdkit"
#endif

#endif /* NBDKIT_INTERNAL_H */
