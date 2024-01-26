from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
import json
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

REAL_DEBRID_API_TOKEN = os.getenv("REAL_DEBRID_API_TOKEN")
API_URL = os.getenv("API_URL")

def process_result(result):
    if isinstance(result, dict):
        hash_value = result.get('hash')
        if hash_value:
            # Check instant availability with Real-Debrid API
            rd_api_url = f'https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{hash_value}/method?auth_token={REAL_DEBRID_API_TOKEN}'
            rd_response = requests.get(rd_api_url)
            rd_response.raise_for_status()

            try:
                rd_data = rd_response.json()

                # Traverse nested dictionaries to extract file information
                for _, rd_entries in rd_data.items():
                    for rd_entry in rd_entries:
                        for file_info in rd_entry.values():
                            filename = file_info.get('filename')
                            filesize = file_info.get('filesize')

                            # Use filename and filesize as needed

                if rd_data.get('status') == 'OK':
                    return result

            except json.JSONDecodeError:
                logging.exception('Error decoding JSON response from Real-Debrid API')

    return None

@app.get('/search', response_class=JSONResponse)
def search_torrent(query: str):
    try:
        # Query the Nexus API
        nexus_api_url = f'{API_URL}/api/v1/all/search?query={query}'
        response = requests.get(nexus_api_url)
        response.raise_for_status()

        # If results are found from the Nexus API, check Real-Debrid availability
        try:
            data = json.loads(response.text)
            filtered_results = []

            for result in data:
                processed_result = process_result(result)
                if processed_result:
                    filtered_results.append(processed_result)

            return {'status': 'success', 'result': filtered_results}

        except json.JSONDecodeError:
            logging.exception('Error decoding JSON response from Nexus API')
            raise HTTPException(status_code=500, detail='Error decoding JSON response from Nexus API')

    except requests.exceptions.RequestException as e:
        # If an error occurred during the requests, log the error and return an error
        logging.exception(f'Error: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Error: {str(e)}')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8978)


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
