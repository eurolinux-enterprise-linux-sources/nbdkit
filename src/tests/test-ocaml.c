/* nbdkit
 * Copyright (C) 2014 Red Hat Inc.
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
#include <stdint.h>
#include <inttypes.h>
#include <string.h>
#include <unistd.h>

#include <guestfs.h>

#include "test.h"

int
main (int argc, char *argv[])
{
  guestfs_h *g;
  int r;
  char *data;
  size_t i, size;

  /* The OCaml tests fail valgrind, so skip them.  We should be able
   * to get this working with a bit of effort.  XXX
   */
  if (getenv ("NBDKIT_VALGRIND") != NULL) {
    fprintf (stderr, "ocaml test skipped under valgrind.\n");
    exit (77);                  /* Tells automake to skip the test. */
  }

  if (test_start_nbdkit ("./test-ocaml-plugin.so", "a=1", "b=2", "c=3",
                         NULL) == -1)
    exit (EXIT_FAILURE);

  g = guestfs_create ();
  if (g == NULL) {
    perror ("guestfs_create");
    exit (EXIT_FAILURE);
  }

  r = guestfs_add_drive_opts (g, "",
                              GUESTFS_ADD_DRIVE_OPTS_FORMAT, "raw",
                              GUESTFS_ADD_DRIVE_OPTS_PROTOCOL, "nbd",
                              GUESTFS_ADD_DRIVE_OPTS_SERVER, server,
                              -1);
  if (r == -1)
    exit (EXIT_FAILURE);

  if (guestfs_launch (g) == -1)
    exit (EXIT_FAILURE);

  /* Check the inital data read from the plugin is \x01-\x08,
   * repeated 512 times.
   */
  data = guestfs_pread_device (g, "/dev/sda", 8 * 512, 0, &size);
  if (!data)
    exit (EXIT_FAILURE);
  if (size != 8 * 512) {
    fprintf (stderr, "%s FAILED: unexpected size (actual: %zu, expected: 512)\n",
             program_name, size);
    exit (EXIT_FAILURE);
  }

  for (i = 0; i < 512 * 8; i += 8) {
    if (data[i] != 1 || data[i+1] != 2 ||
        data[i+2] != 3 || data[i+3] != 4 ||
        data[i+4] != 5 || data[i+5] != 6 ||
        data[i+6] != 7 || data[i+7] != 8) {
      fprintf (stderr, "%s FAILED: unexpected data returned at offset %zu\n",
               program_name, i);
      exit (EXIT_FAILURE);
    }
  }

  /* Write some alternate data, and read it back. */
  for (i = 0; i < 512 * 8; ++i) {
    data[i] = i & 0x7f;
  }

  for (i = 0; i < 8 * 512; i += 4) {
    if (guestfs_pwrite_device (g, "/dev/sda", &data[i], 4, i) == -1)
      exit (EXIT_FAILURE);
  }

  free (data);

  data = guestfs_pread_device (g, "/dev/sda", 8 * 512, 0, &size);
  if (!data)
    exit (EXIT_FAILURE);
  if (size != 8 * 512) {
    fprintf (stderr, "%s FAILED: unexpected size (actual: %zu, expected: 512)\n",
             program_name, size);
    exit (EXIT_FAILURE);
  }

  for (i = 0; i < 512 * 8; ++i) {
    if (data[i] != (i & 0x7f)) {
      fprintf (stderr, "%s FAILED: unexpected data returned at offset %zu\n",
               program_name, i);
      exit (EXIT_FAILURE);
    }
  }

  free (data);

  guestfs_close (g);
  exit (EXIT_SUCCESS);
}
