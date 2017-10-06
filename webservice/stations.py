# -*- coding: utf-8 -*-

import requests
from api_manager import ApiManager

URL = "https://opendata.paris.fr/api/records/1.0/search/?dataset=stations-velib-disponibilites-en-temps-reel&rows=1122&sort=last_update&facet=banking&facet=bonus&facet=status&facet=contract_name&refine.contract_name=Paris&refine.status=OPEN"

URL_METEO = "http://www.infoclimat.fr/public-api/gfs/json?_ll=48.85341,2.3488&_auth=BhxeSQB%2BXX8ALQcwVyEELQBoDzoAdlJ1UCwHZAhtVyoJYlIzAGBXMV8xB3oDLAYwBClTMA02UmJXPFIqDX9QMQZsXjIAa106AG8HYld4BC8ALg9uACBSdVAyB2MIbVcqCWtSPwBmVytfMgdlAzEGLAQ0UzQNLVJ1VzVSMA1gUDQGZ147AGZdPwBmB2xXeAQvADYPZgBrUmxQNwdmCDNXZgljUj4AYFcwX2EHZQMtBjIENlM6DTJSalcyUjcNZlAsBnpeQwAQXSIALwcnVzIEdgAuDzoAYVI%2B&_c=d049fec85622d1dd27f9a768cbfe1d05"

result = requests.get(URL_METEO)

#1122 stations

print result.status_code

print result.json()

OPENDATA_API_URL = "https://opendata.paris.fr/api/records/1.0/search/"

class Stations(ApiManager):

    dataset = "dataset"

    def shape_url(self):

        url = OPENDATA_API_URL + "?"