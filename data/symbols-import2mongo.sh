#!/bin/bash
# mongo <dbname> --eval "db.dropDatabase()"
# db.symbols.dropIndexes()
# db.symbols.ensureIndex({S:1})
# db.symbols.ensureIndex({S:1, D:1})
# db.symbols.getIndexes()
# db.symbols.find({S:"UOLL4", D:{"$gte": "2010-12-01", "$lte": "2010-12-10"}}).explain()
mongoimport -d stock -c symbols --type csv --file symbols.csv --headerline
