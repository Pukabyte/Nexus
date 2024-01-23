from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Database setup
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    database=os.getenv("POSTGRES_DATABASE")
)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS torrents (
        id SERIAL PRIMARY KEY,
        title TEXT,
        imdb_id TEXT,
        name TEXT,
        size TEXT,
        hash TEXT,
        torrent_url TEXT,
        magnet TEXT,
        data TEXT
    )
''')
conn.commit()

REAL_DEBRID_API_TOKEN = os.getenv("REAL_DEBRID_API_TOKEN")
API_URL = os.getenv("API_URL")

@app.get('/search', response_class=JSONResponse)
def search_torrent(query: str):
    # Search the database
    cursor.execute('SELECT * FROM torrents WHERE title=%s OR imdb_id=%s', (query, query))
    result = cursor.fetchone()

    if result:
        # If found in the database, return the result
        return {'status': 'success', 'result': json.loads(result[8])}
    else:
        # If not found in the database, query the API
        api_url = f'{API_URL}/api/v1/all/search?query={query}'

        response = requests.get(api_url)

        if response.status_code == 200:
            # If results are found from the API, check with Real-Debrid API for instant availability
            data = response.json()

            for result in data:
                name = result.get('name')
                size = result.get('size')
                hash_value = result.get('hash')
                torrent_url = result.get('torrent') if hash_value else None
                magnet = result.get('magnet') if not hash_value and not torrent_url else None

                # Check instant availability with Real-Debrid API
                rd_api_url = f'https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/{hash_value}/method?auth_token={REAL_DEBRID_API_TOKEN}'
                rd_response = requests.get(rd_api_url)

                if rd_response.status_code == 200:
                    rd_data = rd_response.json()
                    if rd_data.get('status') == 'OK':
                        # If instant availability, save to the database and return the result
                        cursor.execute('INSERT INTO torrents (title, imdb_id, name, size, hash, torrent_url, magnet, data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                                       (query, query, name, size, hash_value, torrent_url, magnet, json.dumps(data)))

                        conn.commit()
                        return {'status': 'success', 'result': data}
                    else:
                        # If not instantly available on Real-Debrid, return an error
                        raise HTTPException(status_code=404, detail='Torrent not instantly available on Real-Debrid')
                else:
                    # If an error occurred while checking with Real-Debrid API, return an error
                    raise HTTPException(status_code=500, detail='Error checking with Real-Debrid API')
            else:
                # If no results found from the API, return an error
                raise HTTPException(status_code=404, detail='No results found from the API')
        else:
            # If an error occurred while querying the API, return an error
            raise HTTPException(status_code=500, detail='Error querying the API')

if __name__ == '__main__':
    import uvicorn
uvicorn.run(app, host='0.0.0.0', port=8978)
