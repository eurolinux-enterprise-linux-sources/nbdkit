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

#include <config.h>

#include <stdio.h>
#include <stdlib.h>

#include "internal.h"

/* Note that the plugin's thread model cannot change after being
 * loaded, so caching it here is safe.
 */
static int thread_model;

static pthread_mutex_t connection_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t all_requests_lock = PTHREAD_MUTEX_INITIALIZER;
static pthread_rwlock_t unload_prevention_lock = PTHREAD_RWLOCK_INITIALIZER;

void
lock_init_thread_model (void)
{
  thread_model = backend->thread_model (backend);
}

void
lock_connection (void)
{
  if (thread_model <= NBDKIT_THREAD_MODEL_SERIALIZE_CONNECTIONS)
    pthread_mutex_lock (&connection_lock);
}

void
unlock_connection (void)
{
  if (thread_model <= NBDKIT_THREAD_MODEL_SERIALIZE_CONNECTIONS)
    pthread_mutex_unlock (&connection_lock);
}

void
lock_request (struct connection *conn)
{
  if (thread_model <= NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS)
    pthread_mutex_lock (&all_requests_lock);

  if (thread_model <= NBDKIT_THREAD_MODEL_SERIALIZE_REQUESTS)
    pthread_mutex_lock (connection_get_request_lock (conn));

  pthread_rwlock_rdlock (&unload_prevention_lock);
}

void
unlock_request (struct connection *conn)
{
  pthread_rwlock_unlock (&unload_prevention_lock);

  if (thread_model <= NBDKIT_THREAD_MODEL_SERIALIZE_REQUESTS)
    pthread_mutex_unlock (connection_get_request_lock (conn));

  if (thread_model <= NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS)
    pthread_mutex_unlock (&all_requests_lock);
}

void
lock_unload (void)
{
  pthread_rwlock_wrlock (&unload_prevention_lock);
}

void
unlock_unload (void)
{
  pthread_rwlock_unlock (&unload_prevention_lock);
}
