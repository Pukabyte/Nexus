# This is a work in progress
Do not attempt to use this code yet as it will do nothing lol
Written from scratch, with no experience in coding with the help of chatgpt.

# On Demand Real-Debrid Cached Indexer
Feels like Torrentio, Acts like real-debrid for torrents.

# Basic Workflow
- Send query (Title / IMDBID)
- Search Database
- If results are found, return results to client
- If not found, query API Url, if not found return error
- If found, check for cached status on realdebrid
- if cached, save data to database and return to client
- if not cached, return error

The first time query is searched it will parse the data and save the data to database
The following times the query is searched, it will search database and return results as if cached.

# TO-DO
- [ ] Test
- [ ] Add Scheduler to recheck database for cached status and remove when item is no longer cached
- [ ] Add scheduler to check for more results for titles in database for cached status
- [ ] Parse data better
- [ ] Allow IMDBID to be used as search query
- [ ] Hosted centralised database that each self hosted instance can connect to and add data to

Everyone is welcome to submit PR's and help make this epic!
