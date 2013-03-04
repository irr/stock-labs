# python -B Server.py --help
# python -B Server.py --logging=debug

# http localhost:8888/
# http localhost:8888/dynamic
# http localhost:8888/static/index.html
# http localhost:8888/query

from logging import DEBUG, getLogger as log
from os.path import dirname, join
from signal import signal, SIGTERM
from sys import exit

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line, parse_config_file
from tornado.web import Application

from traceback import format_exc
from uuid import uuid1

from handlers import *

import motor

define("config", help="config file", default=None, type=str)
define("address", help="binding host", default="localhost", type=str)
define("port", help="binding port", default=8888, type=int)

define("db_name", help="database name", default="stock", type=str)
define("db_host", help="database host", default="localhost", type=str)
define("db_port", help="database port", default=27017, type=int)

def shutdown():
    io_loop = IOLoop.instance()
    if io_loop.running():
        io_loop.stop()
    log().info("server stopped")

def on_signal(sig, frame):
    if http_server != None:
        log().info("shutting down server...")
        http_server.stop()
    IOLoop.instance().add_callback(shutdown)

def main():
    global http_server

    try:
        signal(SIGTERM, on_signal)
        
        parse_command_line()
        if options.config != None:
            parse_config_file(options.config)

        path = join(dirname(__file__), "templates")

        application = Application([
            (r'/', IndexHandler),
            (r'/stock', StockHandler)],
            template_path=path, 
            static_path=join(dirname(__file__), "static"))

        application.db = motor.MotorClient(options.db_host, 
            options.db_port).open_sync()[options.db_name]

        http_server = HTTPServer(application)
        http_server.listen(options.port, options.address)
        log().info("server listening on port %s:%d" % 
            (options.address, options.port))
        if log().isEnabledFor(DEBUG):
            log().debug("autoreload enabled")
            tornado.autoreload.start()        
        IOLoop.instance().start()

    except KeyboardInterrupt:
        log().info("exiting...")

    except BaseException as ex:
        log().error("exiting due: [%s][%s]" % 
            (str(ex), str(format_exc().splitlines())))
        exit(1)

if __name__ == '__main__':
    main()
