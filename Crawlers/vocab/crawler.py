import scrapy
from neo4j.v1 import GraphDatabase, basic_auth

# The base url for searching a char in the Purple Culture Dictionary
PURPLE_URL = "https://www.purpleculture.net/dictionary-details/?word={}"

# The Authentication for acessing the Neo4j Database
BASIC_AUTH = basic_auth("neo4j", "cogch")

# Initialises the Driver
driver = GraphDatabase.driver("bolt://localhost:7687", auth=BASIC_AUTH)

class VocabCrawler(scrapy.Spider):
    """ Implementing the Crawler starting on the word 爱 (love).
    """
    name = 'vocab_crawler'
    start_urls = [PURPLE_URL.format("爱")] # Lets start with love!

    def parse(self, response):
        char = response.css("ruby ::text").extract_first()
        