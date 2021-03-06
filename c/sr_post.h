/* vim:set ft=c ts=2 sw=2 sts=2 et cindent: */

#ifndef SR_POST_H
#define SR_POST_H 1

/*
 * Usage info after license block.
 *
 * This code is by Peter Silva copyright (c) 2017 part of MetPX.
 * copyright is to the Government of Canada. code is GPL.
 *
 * based on a amqp_sendstring from rabbitmq-c package
 * the original license is below:
 */

/* 
  Minimal c implementation to allow posting of sr_post(7) messages.

  call an sr_context_init to set things up.
  then sr_post will post files,
  then sr_close to tear the connection down.

  there is an all in one function: connect_and_post that does all of the above.

 */

#include "sr_context.h"
#include "sr_consume.h"

void sr_post_message(struct sr_context *sr_c, struct sr_message_t *m);
/* 
   post the given message using the established context.
   (posts over an existing connection.)
*/ 


void sr_post(struct sr_context *sr_c, const char *fn, struct stat *sb); 
/* 
   post the given file name using the established context.
   (posts over an existing connection.)

   The struct stat is normally the result of lstat(fn,sb);
   sr_post reads:  st_size, st_atim, st_mtim, and st_mode.
   those fields are used to build the advertisement.

   if passed sb=NULL, then the sr_post generates an 'R' (remove) message
   for the named file.

 */

void sr_post_rename(struct sr_context *sr_c, const char *oldname, const char *newname);
/* 
   post rename results in a post for removal of the old name, and creation of the new name.

 */

int sr_post_init( struct sr_context *sr_c );
 /*
   At beginning of posting session, initialize (involves declaring an exchange.)
  */

int sr_post_cleanup( struct sr_context *sr_c );
 /*
   Clean up broker resources declared by post_init (deletes an exchange.)
  */

#endif
