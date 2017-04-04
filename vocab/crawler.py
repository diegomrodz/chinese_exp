import scrapy

PURPLE_URL = "https://www.purpleculture.net/dictionary-details/?word={}"

class VocabCrawler(scrapy.Spider):
    name = 'vocab_crawler'
    start_urls = [PURPLE_URL.format("爱")] # Lets start with love!

    def parse(self, response):
        pass