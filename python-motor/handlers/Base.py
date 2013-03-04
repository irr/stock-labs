from bson import json_util
from datetime import datetime
from json import dumps
from logging import getLogger as log

from tornado.template import Loader
from tornado.web import asynchronous, RequestHandler, HTTPError
from tornado import gen

import types, motor

class BaseHandler(RequestHandler):
    @property
    def db(self):
        return self.application.db

class IndexHandler(RequestHandler):
    @asynchronous
    def get(self):
        self.render('index.html')

class StockHandler(BaseHandler):
    @gen.engine
    def do_find(self, symbol):
        cursor = self.db.symbols.find({'S': symbol}, limit = 2147483647)
        data = (yield motor.Op(cursor.to_list))
        self._on_data(data, None)

    @asynchronous
    def get(self):
        symbol = self.get_argument("symbol", None)
        if symbol == None:
            self.db.command({"distinct": "symbols", "key": "S"}, callback = self._on_symbols)    
        else:
            self.do_find(symbol)
            #self.db.symbols.find({'S': symbol}, limit = 2147483647, callback = self._on_data)

    def _on_symbols(self, response, error):
        if error:
            raise HTTPError(500)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(''.join([self.get_argument("callback"), 
                   "([", dumps(response["values"], default=json_util.default), "]);"]))
        self.finish()

    def _on_data(self, response, error):
        if error or not type(response) == types.ListType:
            raise HTTPError(500)
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
