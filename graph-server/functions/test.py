from wsgiref.util import request_uri
import requests, json

url = 'http://10.249.46.195:7478/ping'
h1 = requests.get(url=url)
print(h1)
print(h1.text)