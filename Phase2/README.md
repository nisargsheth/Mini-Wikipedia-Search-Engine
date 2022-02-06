# Phase-2

## Type of queries:

### Plain queries:
Lionel Messi

Sachin Tendulkar
### Field queries:
| Field | Symbol         |
|-------|----------------|
| t     | Title          |
| b     | Body           |
| i     | Infobox        |
| c     | Category       |
| l     | External Links |
| r     | References     |

**t:World Cup i:2019 c:cricket**

Denotes Search for World Cup in title, 2019 in infobox and cricket in category.

## How to run:

#### indexer.py

    python indexer.py <wiki_dump_path>
   **Note:** Index creation can take a long time depending on hardware resources.
   After completion , run: 
   

    python secondary.py
    python id_to_title.py

####  search.py

    python search.py
    
####  Link to wiki dump:

[Click to download](https://dumps.wikimedia.org/enwiki/20220201/enwiki-20220201-pages-articles-multistream.xml.bz2)
