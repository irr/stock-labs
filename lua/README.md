stock
-----------

**stock**  is a swing trade visualization tool built on *[Lua]*, *[OpenResty]*, *[Highstock]* with *[JQuery]* and *[MySQL]*

```shell
yum install readline-devel pcre-devel openssl-devel libdrizzle-devel
tar xfva ngx_openresty-1.2.4.14.tar.gz
cd ngx_openresty-1.2.4.14
./configure --prefix=/data/Lua/openresty --with-luajit --with-http_drizzle_module
make -j4 
make install
```

Dependencies
-----------

* [OpenResty]: A full-fledged web application server by bundling the standard Nginx core, lots of 3rd-party Nginx modules, as well as most of their external dependencies
* [Highstock]: Highstock lets you create stock or general timeline charts in pure JavaScript, including sophisticated navigation options like a small navigator series, preset date ranges, date picker, scrolling and panning


Copyright and License
---------------------
Copyright 2012 Ivan Ribeiro Rocha

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

[Lua]: http://www.lua.org/
[OpenResty]: http://openresty.org/
[Highstock]: http://www.highcharts.com/products/highstock
[JQuery]: http://jquery.com/
[MySQL]: http://www.mysql.com/