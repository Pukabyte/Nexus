from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

REAL_DEBRID_API_TOKEN = os.getenv("REAL_DEBRID_API_TOKEN")
API_URL = os.getenv("API_URL")

@app.get('/search', response_class=JSONResponse)
def search_torrent(query: str):
    # Query the Nexus API
    nexus_api_url = f'{API_URL}/api/v1/all/search?query={query}'
    response = requests.get(nexus_api_url)

    if response.status_code == 200:
        # If results are found from the Nexus API, check Real-Debrid availability
        data = response.json()
        filtered_results = []

        for result in data:
            hash_value = result.get('hash')

            if hash_value:
                # Check instant availability with Real-Debrid API
                rd_api_url = f'https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{hash_value}/method?auth_token={REAL_DEBRID_API_TOKEN}'
                rd_response = requests.get(rd_api_url)

                if rd_response.status_code == 200:
                    rd_data = rd_response.json()
                    if rd_data.get('status') == 'OK':
                        # If instant availability, add to filtered results
                        filtered_results.append(result)
        
        return {'status': 'success', 'result': filtered_results}
    
    else:
        # If an error occurred while querying the Nexus API, return an error
        raise HTTPException(status_code=response.status_code, detail='Error querying the Nexus API')

@app.get('/search-nexus', response_class=JSONResponse)
def search_nexus(query: str):
    # Make a request to nexus.djfeed.xyz
    nexus_url = f'{API_URL}/api/v1/all/search?query={query}'

    response = requests.get(nexus_url)

    if response.status_code == 200:
        # If successful, return the results
        data = response.json()
        return {'status': 'success', 'result': data}
    else:
        # If an error occurred, raise an HTTPException
        raise HTTPException(status_code=500, detail='Error searching Cacharr')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8978)
