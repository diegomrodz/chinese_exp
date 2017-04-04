from neo4j.v1 import GraphDatabase, basic_auth
import scrapy
import re
import nltk

# The base url for searching a char in the Purple Culture Dictionary
PURPLE_URL = "https://www.purpleculture.net/dictionary-details/?word={}"

# The Authentication for acessing the Neo4j Database
BASIC_AUTH = basic_auth("neo4j", "cogch")

# Initialises the Driver
driver = GraphDatabase.driver("bolt://localhost:7687", auth=BASIC_AUTH)

TOTAL_STROKES = "Total strokes:"
RADICAL = "Radical:"
STRUCTURE = "Structure:"

class VocabCrawler(scrapy.Spider):
    """ Implementing the Crawler starting on the word 爱 (love).
    """
    name = 'vocab_crawler'
    start_urls = [PURPLE_URL.format("爱")] # Lets start with love!

    def parse(self, response):
        self.set_response(response)

        word = self.get_word()
   
        if len(word) > 1:
            self.process_word(word)
        else:
            self.process_char(word[0])

    def process_word(self, word):
        definitions = self.get_definitions()
        pinyin = self.get_pinyin()

        print(word, list(definitions), pinyin)
    
    def process_char(self, char):
        pinyin = self.get_pinyin()[0]
        definitions = self.get_definitions()
        composition = self.get_composition()

        if TOTAL_STROKES in composition:
            idx = composition.index(TOTAL_STROKES)
            total_strokes = composition[idx + 1][1:-2]
            print("Total Strokes:", total_strokes)
        
        if RADICAL in composition:
            idx = composition.index(RADICAL)
            radical = composition[idx + 2]
            print("Radical", radical)

        if STRUCTURE in composition:
            idx = composition.index(STRUCTURE)
            structure = composition[idx + 1][1:].split(" + ")

            if '*' in structure:
                idx = structure.index('*')
                del structure[idx]

            print("Structure", structure)
        
        antonyms = self.get_antonyms()
        swords = self.get_swords()

        print("#1", antonyms, swords)
        print("#2", char, pinyin, list(definitions), composition)

    def set_response(self, response):
        self.response = response

    def get_definitions(self):
        definitions = self.response.css(".en ::text").extract_first()

        if not definitions is None:
            return map(
                lambda e: re.sub("\(.*\)", "", e).strip(),
                definitions.split("; "))
        return None
    
    def get_word(self):
        return self.response.css("h1 ::text").extract_first().split(" ")[-2]

    def get_pinyin(self):
        return self.response.css("a.pinyin ::text").extract()

    def get_composition(self):
        return self.response.css("p.charstr ::text").extract()
    
    def get_antonyms(self):
        return self.response.css("span.antonym a ::text").extract()
    
    def get_swords(self):
        return self.response.css("a.sword ::text").extract()
