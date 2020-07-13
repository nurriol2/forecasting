# Tradeable Item Class
## core attributes
- name - *string*
    - used to instantiate object

- id - *int*
    - (currently) searchable via name from file on disk
    - (long term) online db or webscrape

- table - *pd.DataFrame*
    - indexed by timestamp
    - %d%m%y fromat
    ---
    *columns*
    - daily closing price
    - average daily price
    - trade volume

- web URLs - *string*  
    *class attribute*
    - BASE_URL 
    ---
    *instance attributes*
    - GRAPH_ENDPOINT 
    - VOLUME_ENDPOINT

## behaviors
- naming is robust to capitalization
    - (long term) spelling suggestions
- error handling for non-tradeable items
- 3 core time series (close, avg, vol) available on instance
- plotting time series with a single method call
    - provide signal name (col)--> plot
    - autocompletion for plot details (title, y-axis units)
- new data should be appendable to tradeable item
    - *e.g.* use closing data --> get moving average; append moving average
    

## methods
- ~~search item id from name~~
- web scraping 
    - ~~format endpoints from item id~~
    - parse html for volume data 
    - format API response 
        - timestamps --> %d%m%y
        - fill NaN
        - int and string data where needed
    - saving scraped data to disk
- plotting
    - automatic title and y-axis handling
    - saving plots to disk
- appending new data
    - verify new data size

