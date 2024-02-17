
<h2 align='center'>Nexus</h2>
<p align="center">
<a href="https://github.com/Pukabyte"><img title="Author" src="https://img.shields.io/badge/Author-Pukabyte-red.svg?style=for-the-badge&logo=github"></a>
</p>

<p align="center">
<a href="https://github.com/Pukabyte"><img title="Followers" src="https://img.shields.io/github/followers/Pukabyte?color=teal&style=flat-square"></a>
<a href="https://github.com/Pukabyte/Nexus/stargazers/"><img title="Stars" src="https://img.shields.io/github/stars/Pukabyte/Nexus?color=brown&style=flat-square"></a>
<a href="https://github.com/Pukabyte/Nexus/network/members"><img title="Forks" src="https://img.shields.io/github/forks/Pukabyte/Nexus?color=lightgrey&style=flat-square"></a>
<a href="https://github.com/Pukabyte/Nexus/issues"><img title="issues" src="https://img.shields.io/github/issues/Pukabyte/Nexus?style=flat-square">
</a>
<img src='https://visitor-badge.glitch.me/badge?page_id=Pukabyte.Nexus'>
</p>

<p align="center">
<span style='font-size: 19px'>
An Unofficial API for <span style='font-weight:600;'>1337x</span>, <span style='font-weight:600;'>Piratebay</span>, <span style='font-weight:bold;'>Nyaasi</span>, <span style='font-weight:bold;'>Torlock</span>, <span style='font-weight:bold;'>Torrent Galaxy</span>, <span style='font-weight:600;'>Zooqle</span>, <span style='font-weight:600;'>Kickass</span>, <span style='font-weight:600;'>Bitsearch</span>, <span style='font-weight:600;'>MagnetDL, </span>Libgen, YTS, Limetorrent, TorrentFunk, Glodls, TorrentProject and YourBittorrent
</span>
</p>

#  On Demand Real-Debrid Cached Indexer

Feels like Torrentio, acts like real-debrid for torrents.

##  Work in Progress!

Do not attempt to use this code yet as it will do nothing lol  

##  Basic Workflow

As this is still a work in progress, the direction of the app may, and probably will change.

- User sends GET request with a query of a Title, or IMDb ID 
	- Will eventually support more external ID's
- Scrape all indexers
- Return results to user (JSON response)

##  TO-DO

Eventually we want to build a cached database of data that's community driven.

- [ ] Add Scheduler to recheck database for cached status and remove when item is no longer cached.
- [ ] Add scheduler to check for more results for titles in database for cached status.
- [ ] Add parser module to allow for building json responses.
- [ ] Allow IMDb ID's to be used as search queries.
- [ ] Hosted centralised database that each self hosted instance can connect to and add data to.

Everyone is welcome to submit PR's and help make this epic!

## Installation

```sh

# Clone the repo
$ git clone https://github.com/Pukabyte/Nexus

# Go to the repository
$ cd Nexus

# Install virtualenv
$ pip install virtualenv

# Create Virtual Env
$ py -3 -m venv nexus

# Activate Virtual Env [Windows]
$ .\nexus\Scripts\activate

# Activate Virtual Env [Linux]
$ source nexus/bin/activate

# Install Dependencies
$ pip install -r requirements.txt

# Start
$ python main.py

# (optional) To Use a PROXY, set the HTTP Proxy environment variable
# You can also use a tor proxy using dperson/torproxy:latest
$ export HTTP_PROXY="http://proxy-host:proxy-port"

# To access API Open any browser/API Testing tool & move to the given URL
$ localhost:8009 

```

## Supported Sites

|    Website     |     Keyword      |             Url              | Cloudfare |
| :------------: | :--------------: | :--------------------------: | :-------: |
|     1337x      |     `1337x`      |       https://1337x.to       |     ✅     |
| Torrent Galaxy |      `tgx`       |   https://torrentgalaxy.to   |     ❌     |
|    Torlock     |    `torlock`     |   https://www.torlock.com    |     ❌     |
|   PirateBay    |   `piratebay`    |  https://thepiratebay10.org  |     ❌     |
|     Nyaasi     |     `nyaasi`     |       https://nyaa.si        |     ❌     |
|     Zooqle     |     `zooqle`     |      https://zooqle.com      |     ❌     |
|    KickAss     |    `kickass`     |  https://kickasstorrents.to  |     ❌     |
|   Bitsearch    |   `bitsearch`    |     https://bitsearch.to     |     ❌     |
|    MagnetDL    |    `magnetdl`    |   https://www.magnetdl.com   |     ✅     |
|     Libgen     |     `libgen`     |      https://libgen.is       |     ❌     |
|      YTS       |      `yts`       |        https://yts.mx        |     ❌     |
|  Limetorrent   |  `limetorrent`   | https://www.limetorrents.pro |     ❌     |
|  TorrentFunk   |  `torrentfunk`   | https://www.torrentfunk.com  |     ❌     |
|     Glodls     |     `glodls`     |      https://glodls.to       |     ❌     |
| TorrentProject | `torrentproject` | https://torrentproject2.com  |     ❌     |
| YourBittorrent |      `ybt`       |  https://yourbittorrent.com  |     ❌     |


## API Endpoints

Supported sites list

> `/sites`

<br>

Search

> /search?query=avengers

| Parameter | Required |  Type   | Default |                         Example                          |
| :-------: | :------: | :-----: | :-----: | :------------------------------------------------------: |
|   query   |    ✅     | string  |  None   |        `/search?site=1337x&query=avengers`         |
|   limit   |    ❌     | integer | Default |    `/search?site=1337x&query=avengers&limit=20`    |
|   page    |    ❌     | integer |    1    | `/search?site=1337x&query=avengers&limit=0&page=2` |

</p>
</details>
<br>

<details open>
<summary style='font-size: 15px'><span style='font-size: 20px;font-weight:bold;'>Trending</span></summary>
<p>

> `/trending`

| Parameter | Required |  Type   | Default |                         Example                         |
| :-------: | :------: | :-----: | :-----: | :-----------------------------------------------------: |
|   site    |    ✅     | string  |  None   |              `/trending?site=1337x`               |
|   limit   |    ❌     | integer | Default |          `/trending?site=1337x&limit=10`          |
| category  |    ❌     | string  |  None   |    `/trending?site=1337x&limit=0&category=tv`     |
|   page    |    ❌     | integer |    1    | `/trending?site=1337x&limit=6&category=tv&page=2` |

<br>

Recent

> `/recent`

| Parameter | Required |  Type   | Default |                        Example                         |
| :-------: | :------: | :-----: | :-----: | :----------------------------------------------------: |
|   site    |    ✅     | string  |  None   |               `/recent?site=1337x`               |
|   limit   |    ❌     | integer | Default |           `/recent?site=1337x&limit=7`           |
| category  |    ❌     | string  |  None   |     `/recent?site=1337x&limit=0&category=tv`     |
|   page    |    ❌     | integer |    1    | `/recent?site=1337x&limit=15&category=tv&page=2` |

<br>

<details open>
<summary style='font-size: 15px'><span style='font-size: 20px;font-weight:bold;'>Search By Category</span></summary>
<p>

> `/search/category`

| Parameter | Required |  Type   | Default |                                Example                                 |
| :-------: | :------: | :-----: | :-----: | :--------------------------------------------------------------------: |
|   site    |    ✅     | string  |  None   |                      `/search/category?site=1337x`                      |
|   query   |    ✅     | string  |  None   |              `/search/category?site=1337x&query=avengers`               |
| category  |    ✅     | string  |  None   |      `/search/category?site=1337x&query=avengers&category=movies`       |
|   limit   |    ❌     | integer | Default |  `/search/category?site=1337x&query=avengers&category=movies&limit=10`  |
|   page    |    ❌     | integer |    1    | `/search/category?site=1337x&query=avengers&category=tv&limit=0&page=2` |

<br>

Get trending from all sites

> `/all/trending`

| Parameter | Required |  Type   | Default |            Example            |
| :-------: | :------: | :-----: | :-----: | :---------------------------: |
|   limit   |    ❌     | integer | Default | `/all/trending?limit=2` |

<br>

Get recent from all sites

> `/all/recent`

| Parameter | Required |  Type   | Default |           Example           |
| :-------: | :------: | :-----: | :-----: | :-------------------------: |
|   limit   |    ❌     | integer | Default | `/all/recent?limit=2` |


## Getting Started with the API

### Search Request

> /search?query=eternals

See response
```json
{
  "data": [
    { 
      "name": "Eternals.2021.REPACK.IMAX.WEB-DL.1080p.seleZen.mkv",
      "infohash": "BCAB80422BBEA1FED70BC7BA43FD350F6644215A",
      "site": "https://bitsearch.to"
    }
  ],
  "total": 102,
  "time": 3.7571887969970703
}
```
