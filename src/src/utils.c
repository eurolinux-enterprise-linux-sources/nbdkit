/* nbdkit
 * Copyright (C) 2013 Red Hat Inc.
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
#include <stdbool.h>
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>
#include <errno.h>

#include "nbdkit-plugin.h"
#include "internal.h"

char *
nbdkit_absolute_path (const char *path)
{
  CLEANUP_FREE char *pwd = NULL;
  char *ret;

  if (path == NULL || *path == '\0') {
    nbdkit_error ("cannot convert null or empty path to an absolute path");
    return NULL;
  }

  if (*path == '/') {
    ret = strdup (path);
    if (!ret) {
      nbdkit_error ("strdup: %m");
      return NULL;
    }
    return ret;
  }

  pwd = get_current_dir_name ();
  if (pwd == NULL) {
    nbdkit_error ("get_current_dir_name: %m");
    return NULL;
  }

  if (asprintf (&ret, "%s/%s", pwd, path) == -1) {
    nbdkit_error ("asprintf: %m");
    return NULL;
  }

  return ret;
}

/* XXX Multiple problems with this function.  Really we should use the
 * 'human*' functions from gnulib.
 */
int64_t
nbdkit_parse_size (const char *str)
{
  uint64_t size;
  char t;

  if (sscanf (str, "%" SCNu64 "%c", &size, &t) == 2) {
    switch (t) {
    case 'b': case 'B':
      return (int64_t) size;
    case 'k': case 'K':
      return (int64_t) size * 1024;
    case 'm': case 'M':
      return (int64_t) size * 1024 * 1024;
    case 'g': case 'G':
      return (int64_t) size * 1024 * 1024 * 1024;
    case 't': case 'T':
      return (int64_t) size * 1024 * 1024 * 1024 * 1024;
    case 'p': case 'P':
      return (int64_t) size * 1024 * 1024 * 1024 * 1024 * 1024;
    case 'e': case 'E':
      return (int64_t) size * 1024 * 1024 * 1024 * 1024 * 1024 * 1024;

    case 's': case 'S':         /* "sectors", ie. units of 512 bytes,
                                 * even if that's not the real sector size
                                 */
      return (int64_t) size * 512;

    default:
      nbdkit_error ("could not parse size: unknown specifier '%c'", t);
      return -1;
    }
  }

  /* bytes */
  if (sscanf (str, "%" SCNu64, &size) == 1)
    return (int64_t) size;

  nbdkit_error ("could not parse size string (%s)", str);
  return -1;
}

/* Read a password from configuration value. */
int
nbdkit_read_password (const char *value, char **password)
{
  int tty, err;;
  struct termios orig, temp;
  ssize_t r;
  size_t n;
  FILE *fp;

  /* Read from stdin. */
  if (strcmp (value, "-") == 0) {
    printf ("password: ");

    /* Set no echo. */
    tty = isatty (0);
    if (tty) {
      tcgetattr (0, &orig);
      temp = orig;
      temp.c_lflag &= ~ECHO;
      tcsetattr (0, TCSAFLUSH, &temp);
    }

    r = getline (password, &n, stdin);
    err = errno;

    /* Restore echo. */
    if (tty)
      tcsetattr (0, TCSAFLUSH, &orig);

    /* Complete the printf above. */
    printf ("\n");

    if (r == -1) {
      errno = err;
      nbdkit_error ("could not read password from stdin: %m");
      return -1;
    }
    if (*password && r > 0 && (*password)[r-1] == '\n')
      (*password)[r-1] = '\0';
  }

  /* Read password from a file. */
  else if (value[0] == '+') {
    fp = fopen (&value[1], "r");
    if (fp == NULL) {
      nbdkit_error ("open %s: %m", &value[1]);
      return -1;
    }
    r = getline (password, &n, fp);
    err = errno;
    fclose (fp);
    if (r == -1) {
      errno = err;
      nbdkit_error ("could not read password from file %s: %m", &value[1]);
      return -1;
    }
    if (*password && r > 0 && (*password)[r-1] == '\n')
      (*password)[r-1] = '\0';
  }

  /* Parameter is the password. */
  else {
    *password = strdup (value);
    if (*password == NULL) {
      nbdkit_error ("strdup: %m");
      return -1;
    }
  }

  return 0;
}
