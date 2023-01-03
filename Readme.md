# S1mple Notion Analytics
A basic python script used for counting the number of sub-pages & databases inside a notion page.

In this repo, there are 2 ways to start analytics: 
- naive_analytics.py: crawling one by one
- threading_analytics.py: schedule crawler with thread pool

Both ways' performances are aggressively limited by how notion api worker works with the notion api. For example, notion api's rate limit is an average of 3 requests per second. However, throughout experiment, there are other non-published rate limits, which are not been handled correctly by the notion api worker. Therefore, this analytic script can get into some troubles when number of pages is too big.

On the other hand, main.py is provided as an example of how to run analytics.

- To run the analytics with a worker, please specify it in .env file 
    ```
    NOTION_WORKER=https://notion-api.splitbee.io/v1/
    ```
  
- To approach the private page, please specify the token in .env file
    ```
    NOTION_TOKEN=<token>
    ```
    Notion api token can be retrieved by following the instruction in https://www.redgregory.com/notion/2020/6/15/9zuzav95gwzwewdu1dspweqbv481s5

- In addition, by setting the environment variable `RUN_MODE`, different types of .env can be used correspondingly
    - RUN_MODE=prod: .env.prod
    - RUN_MODE=local: .env.local