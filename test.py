import http.client

conn = http.client.HTTPSConnection("api.t1qq.com")
payload = ''
headers = {
   'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
   'Accept': '*/*',
   'Host': 'api.t1qq.com',
   'Connection': 'keep-alive'
}
conn.request("GET", "/api/tool/wzrr/ydtp?key=vBpEzoiC9z5A9c9Nn83IhLn6M9&id=489048724", payload, headers)
res = conn.getresponse()
data = res.read()
print(data)