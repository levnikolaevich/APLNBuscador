from typing import Any
import scrapy
import os


class APLNSpider(scrapy.Spider):
    name = 'apln_spider'

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.max_pages = 10
        self.visited_urls = set()

    def start_requests(self, urls=None):
        if urls is None:
            urls = ["https://www.ua.es"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Adjusting to use a single .txt file and include page title
        page_name = response.url.split("/")[-2] or 'index'
        if response.url == 'https://www.ua.es':
            page_name = 'index'

        # Path to the output txt file
        save_path = 'page_contents.txt'
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Saving the page name and content with a delimiter
        with open(save_path, 'a', encoding='utf-8') as f:
            f.write(f"Page Name: {page_name} | Content:\n{response.text}\n\n")
        self.log(f'Added content of {page_name} to {save_path}')

        # Mark the current page as visited
        self.visited_urls.add(response.url)

        # Check if the number of visited pages has reached the maximum
        if len(self.visited_urls) >= self.max_pages:
            self.log(f'Number of visited pages reached maximum ({self.max_pages}). Stopping crawler.')
            raise scrapy.exceptions.CloseSpider('Maximum pages reached')

        # Search for and follow links on the current page
        for next_page in response.css('a::attr(href)').getall():
            # Ignore links that do not contain .ua.es
            if '.ua.es' not in next_page:
                continue
            next_url = response.urljoin(next_page)
            if next_url not in self.visited_urls:
                yield scrapy.Request(url=next_url, callback=self.parse)
