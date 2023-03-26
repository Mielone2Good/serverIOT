import requests
import json

url = "http://127.0.0.1:8000/login"

payload = json.dumps({
  "username": "admin",
  "password": "1234"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
