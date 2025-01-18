import requests

url = "https://public.opendatasoft.com/explore/embed/dataset/openaq/table/?disjunctive.measurements_parameter&disjunctive.location&disjunctive.city&sort=measurements_lastupdated"

data = requests.get(url).json()
print(data['results'])

for result in data['results']:
    print(result['country'])
