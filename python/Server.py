# python -B Server.py --help
# python -B Server.py --logging=debug

# http localhost:8888/
# http localhost:8888/dynamic
# http localhost:8888/static/index.html
# http localhost:8888/query

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado import gen
from tornado.options import define, options

import os, sys, signal, time, logging, traceback, uuid

import asyncmongo

from handlers import *


define("config", help="config file", default=None, type=str)
define("address", help="binding host", default="localhost", type=str)
define("port", help="binding port", default=8888, type=int)

define("db_pool", help="database pool-id", default="stock", type=str)
define("db_name", help="database name", default="stock", type=str)
define("db_host", help="database host", default="localhost", type=str)
define("db_port", help="database port", default=27017, type=int)


def shutdown():
    io_loop = tornado.ioloop.IOLoop.instance()
    if io_loop.running():
        io_loop.stop()
    logging.getLogger().info("server stopped")


def on_signal(sig, frame):
    if http_server != None:
        logging.getLogger().info("shutting down server...")
        http_server.stop()
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)


def main():
    global http_server

    try:
        signal.signal(signal.SIGTERM, on_signal)
        
        tornado.options.parse_command_line()
        if options.config != None:
            tornado.options.parse_config_file(options.config)

        path = os.path.join(os.path.dirname(__file__), "templates")

        application = tornado.web.Application([
            (r'/', IndexHandler),
            (r'/quotes', QuotesHandler)],
            template_path=path, 
            static_path=os.path.join(os.path.dirname(__file__), "static"), 
            debug=True)

        application.db = asyncmongo.Client(
            pool_id = str(uuid.uuid1()), 
            host = options.db_host, 
            port = options.db_port, 
            dbname = options.db_name)

        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(options.port, options.address)
        logging.getLogger().info("server listening on port %s:%d" % 
            (options.address, options.port))
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.getLogger().debug("autoreload enabled")
            tornado.autoreload.start()        
        tornado.ioloop.IOLoop.instance().start()

    except KeyboardInterrupt:
        logging.getLogger().info("exiting...")

    except BaseException as ex:
        logging.getLogger().error("exiting due: [%s][%s]" % 
            (str(ex), str(traceback.format_exc().splitlines())))
        sys.exit(1)


if __name__ == '__main__':
    main()
