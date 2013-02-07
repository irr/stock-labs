from bson import json_util
from datetime import datetime
from json import dumps
from logging import getLogger as log
from pymongo import MongoClient

from tornado.ioloop import IOLoop
from tornado.template import Loader
from tornado.web import asynchronous, RequestHandler, HTTPError

class IndexHandler(RequestHandler):
    @asynchronous
    def get(self):
        self.render('index.html')

class StockHandler(RequestHandler):
    def run_background(self, func, callback, args=(), kwds={}):
        def _callback(result):
            IOLoop.instance().add_callback(lambda: callback(result))
        self.application.workers.apply_async(func, args, kwds, _callback)

    def distinct(self, args):
        options = self.application.options
        connection = MongoClient(options.db_host, options.db_port, 
            max_pool_size = 0, auto_start_request = True, use_greenlets = False)
        db = connection[options.db_name]
        response = db.command({"distinct": "symbols", "key": "S"})
        connection.end_request()
        return response

    def find(self, symbol):
        options = self.application.options
        connection = MongoClient(options.db_host, options.db_port, 
            max_pool_size = 0, auto_start_request = True, use_greenlets = False)
        db = connection[options.db_name]
        response = db.symbols.find({'S': symbol})
        connection.end_request()
        return response

    @asynchronous
    def get(self):
        symbol = self.get_argument("symbol", None)
        if symbol == None:
            self.run_background(self.distinct, self._on_symbols, (None,))
        else:
            self.run_background(self.find, self._on_data, (symbol,))

    def _on_symbols(self, response):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(''.join([self.get_argument("callback"), 
                   "([", dumps(response["values"], default=json_util.default), "]);"]))
        self.finish()

    def _on_data(self, response):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        lst = [[self.get_argument("symbol")]]
        for t in response:
            date = [int(i) for i in  t["D"].split("-")]
            data = [int(datetime(date[0],date[1],date[2]).strftime('%s')) * 1000]
            data.extend([float(t[x]) for x in ["O", "H", "L", "C", "V"]])
            lst.append(data)  
        self.write(''.join([self.get_argument("callback"),
                   "(", dumps(lst, default=json_util.default), ");"]))
        self.finish()
