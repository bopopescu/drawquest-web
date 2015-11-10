# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license. 
# See the NOTICE for more information.
#

from datetime import datetime
import errno
import os
import select
import socket

import gunicorn.http as http
import gunicorn.http.wsgi as wsgi
import gunicorn.util as util
import gunicorn.workers.base as base
import gunicorn.workers.sync
from gunicorn import six


class SyncWorker(gunicorn.workers.sync.SyncWorker):
    def handle(self, listener, client, addr):
        environ = {}
        req = None
        resp = None
        try:
            parser = http.RequestParser(self.cfg, client)
            req = six.next(parser)
            environ, resp = self.handle_request(listener, req, client, addr)
        except http.errors.NoMoreData as e:
            self.log.debug("Ignored premature client disconnection. %s", e)
        except StopIteration as e:
            self.log.debug("Closing connection. %s", e)
        except socket.error as e:
            if e.args[0] != errno.EPIPE:
                self.log.exception("Error processing request.")
            else:
                self.log.debug("Ignoring EPIPE")
        except Exception as e:
            self.handle_error(req, client, addr, e)
        finally:
            util.close(client)
            try:
                if resp is not None:
                    self.cfg.post_request(self, req, environ, resp)
                else:
                    self.log.exception("Error during post_request.")
            except:
                self.log.exception("Error during post_request.")

    def handle_request(self, listener, req, client, addr):
        environ = {}
        resp = None
        try:
            self.cfg.pre_request(self, req)
            request_start = datetime.now()
            resp, environ = wsgi.create(req, client, addr,
                    listener.getsockname(), self.cfg)
            # Force the connection closed until someone shows
            # a buffering proxy that supports Keep-Alive to
            # the backend.
            resp.force_close()
            self.nr += 1
            if self.nr >= self.max_requests:
                self.log.info("Autorestarting worker after current request.")
                self.alive = False
            respiter = self.wsgi(environ, resp.start_response)
            try:
                if isinstance(respiter, environ['wsgi.file_wrapper']):
                    resp.write_file(respiter)
                else:
                    for item in respiter:
                        resp.write(item)
                resp.close()
                request_time = datetime.now() - request_start
                self.log.access(resp, req, environ, request_time)
            finally:
                if hasattr(respiter, "close"):
                    respiter.close()
        except socket.error:
            raise
        except Exception as e:
            if resp.headers_sent:
                # If the requests have already been sent, we should close the
                # connection to indicate the error.
                client.shutdown(socket.SHUT_RDWR)
                client.close()
            # Only send back traceback in HTTP in debug mode.
            self.handle_error(req, client, addr, e)
            return
        return environ, resp

