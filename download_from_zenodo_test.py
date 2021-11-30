import requests
r = requests.get("https://sandbox.zenodo.org/deposit/916289/NTNU142M-2014-11-16_11-02-45_low.mat")
print(r.status_code)
print(r.json())