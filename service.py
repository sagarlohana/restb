import json
import requests
import asyncio
from aiohttp import ClientSession

def remove_under(string):
	return string.replace("_", " ").title()

async def fetch(url, session, image_url, model_id):
    payload = {
        # Add the client key to the parameters dictionary
        'client_key': 'acc1ab0931706f2ddc11460c54f69aa586155461a296d3322100c95579573ea5',
        'model_id': model_id,
        'image_url': image_url

        # Other parameters...
    }
    async with session.get(url, params=payload) as response:
        return await response.read()

async def run(image_url_list, url, model_id):
    tasks = []

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        for image_url in image_url_list:
            task = asyncio.ensure_future(fetch(url, session, image_url, model_id))
            tasks.append(task)
            await asyncio.sleep(0.08)

        responses = await asyncio.gather(*tasks)
        # you now have all response bodies in this variable
        # print (responses)
        return responses

def services(image_url_list, url, model_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(run(image_url_list, url, model_id))
    loop.run_until_complete(future)
    return (future.result())

def roomF(image_url_list, t_list):
	url = 'https://api-eu.restb.ai/classify'
	model_id = 'real_estate_global_v2'
	responses = services(image_url_list, url, model_id)

	for i in range (len(image_url_list)):
		responses[i] = responses[i].decode('utf8').replace("'", '"')
		responses[i] = json.loads(responses[i])
		if responses[i]["error"] == "true":
			payload = {
	        'client_key': 'acc1ab0931706f2ddc11460c54f69aa586155461a296d3322100c95579573ea5',
	        'model_id': model_id,
	        'image_url': image_url_list[i]
	    	}
			err_resp = requests.get(url, params=payload, allow_redirects=True, timeout=30)
			responses[i] = err_resp.json()
		detectedRoomType = remove_under(responses[i]["response"]["probabilities"][0][0][0])
		t_list.append(detectedRoomType)


def featF(image_url_list, t_list):
	url = 'https://api-eu.restb.ai/segmentation'
	model_id = 're_features_v3'

	responses = services(image_url_list, url, model_id)

	for i in range (len(image_url_list)):
		responses[i] = responses[i].decode('utf8').replace("'", '"')
		responses[i] = json.loads(responses[i])
		if responses[i]["error"] == "true":
			payload = {
	        'client_key': 'acc1ab0931706f2ddc11460c54f69aa586155461a296d3322100c95579573ea5',
	        'model_id': model_id,
	        'image_url': image_url_list[i]
	    	}
			err_resp = requests.get(url, params=payload, allow_redirects=True, timeout=30)
			responses[i] = err_resp.json()
		featuresList = [] 
		for feat in responses[i]["response"]["objects"]:
			featuresList.append(remove_under(feat))
			# Checking if detected features list is empty, if it is then store "no_features"
		if (featuresList):
			t_list.append(featuresList)
		else:
			t_list.append("No Features")
	
def waterF(image_url_list, t_list):
	url = 'https://api-eu.restb.ai/segmentation'
	model_id = 're_logo'

	responses = services(image_url_list, url, model_id)

	for i in range (len(image_url_list)):
		responses[i] = responses[i].decode('utf8').replace("'", '"')
		responses[i] = json.loads(responses[i])
		if responses[i]["error"] == "true":
			payload = {
	        'client_key': 'acc1ab0931706f2ddc11460c54f69aa586155461a296d3322100c95579573ea5',
	        'model_id': model_id,
	        'image_url': image_url_list[i]
	    	}
			err_resp = requests.get(url, params=payload, allow_redirects=True, timeout=30)
			responses[i] = err_resp.json()

		logoWatermark = responses[i]["response"]["objects"]
		if (len(logoWatermark) == 0):
			logoWatermark = "No"
		elif (len(logoWatermark) == 2):
			logoWatermark = "Logo and Watermark"
		elif (logoWatermark == "logo"):
			logoWatermark = "Logo"
		else:
			logoWatermark = "Watermark"
		t_list.append(logoWatermark)