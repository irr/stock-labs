import logging, time, json, types, datetime
import asyncmongo
from bson import json_util

import tornado.web
from tornado.template import Loader

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render('index.html')

class QuotesHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        symbol = self.get_argument("symbol", None)
        if symbol == None:
            self.db.command({"distinct": "symbols", "key": "S"}, callback = self._on_response_symbols)    
        else:
            self.db.symbols.find({'S': symbol}, limit = 2147483647, callback = self._on_response_data)

    def _on_response_symbols(self, response, error):
        if error:
            raise tornado.web.HTTPError(500)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write("%s([%s]);" % 
            (self.get_argument("callback"), json.dumps(response["values"], default=json_util.default)))
        self.finish()
        # json_string  = json.dumps(obj, default=json_util.default)
        # mongo_object = json.loads(js, object_hook=json_util.object_hook)

    def _on_response_data(self, response, error):
        if error or not isinstance(response, types.ListType):
            raise tornado.web.HTTPError(500)
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        lst = [[self.get_argument("symbol")]]
        for t in response:
            date = map(int, t["D"].split("-"))
            data = [int(datetime.datetime(date[0],date[1],date[2]).strftime('%s')) * 1000]
            data.extend([float(t[x]) for x in ["O", "H", "L", "C", "V"]])
            lst.append(data)  
        self.write("%s(%s);" % 
            (self.get_argument("callback"), json.dumps(lst, default=json_util.default)))
        self.finish()
