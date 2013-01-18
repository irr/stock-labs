-- nginx -c /home/irocha/git/stock-labs/lua/config/nginx.conf
-- http "http://localhost:8080/quotes?callback=ivan&symbol=UOLL4"

local cjson = require "cjson"
local mysql = require "resty.mysql"

local function splitv(str, sep)
    local s = str..sep
    return s:match((s:gsub("[^"..sep.."]*"..sep, "([^"..sep.."]*)"..sep)))
end

local function query_mysql()
    local db = mysql:new()
    db:connect{
                host = "127.0.0.1",
                port = 3306,
                database = "stock",
                user = "root",
                password = "mysql"
              }

    local args = ngx.req.get_uri_args()
    local callback = args["callback"]
    local symbol = args["symbol"]

    if not symbol then
        local res, err, errno, sqlstate = db:query("select distinct(s) from symbols order by s;");
        local syms = {}
        for i = 1, #res do
            table.insert(syms, res[i].s)
        end    
        ngx.say(callback.."(["..cjson.encode(syms).."]);")
    else
        local sql = string.format("select * from symbols where s = '%s';", symbol)
        local res, err, errno, sqlstate = db:query(sql)

        local json = callback.."([[\'"..symbol.."\']"..((#res > 0) and "," or "")
        for i = 1, #res do
            local y, m, d = splitv(res[i].D, "-")
            local r = cjson.encode({os.time{year=y, month=m, day=d}*1000, 
                res[i].O, res[i].H, res[i].L, res[i].C, res[i].V})        
            json = json..r..((i ~= #res) and "," or "")
        end
        ngx.say(json.."]);")
    end

    db:set_keepalive(0, 10)
    
    return not err
end

local ok, res = ngx.thread.wait(ngx.thread.spawn(query_mysql))

if (not ok) or (not res) then
    ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)    
end
