#id
import requests
url=requests.get("https://api.ipify.org/?format=json")
print(url.text)


#loction
url2=requests.get("https://ipinfo.io/<YOUR_IP>/geo")
print(url2.text)
