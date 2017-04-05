import scrapy
import re
import nltk
import repository

# The base url for searching a char in the Purple Culture Dictionary
PURPLE_URL = "https://www.purpleculture.net/dictionary-details/?word={}"

TOTAL_STROKES = "Total strokes:"
RADICAL = "Radical:"
STRUCTURE = "Structure:"

class VocabCrawler(scrapy.Spider):
    """ Implementing the Crawler starting on the word 爱 (love).
    """
    name = 'vocab_crawler'
    start_urls = [PURPLE_URL.format("好")] # Lets start with love!
    
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

        for definition in definitions:
            repository.touch_definition(definition)
            repository.means(char, definition)

        composition = self.get_composition()

        if TOTAL_STROKES in composition:
            idx = composition.index(TOTAL_STROKES)
            total_strokes = composition[idx + 1][1:-2]
            
            print("Total Strokes:", total_strokes)

            repository.touch_char(char, pinyin=pinyin, strokes=total_strokes)
        else:
            repository.touch_char(char, pinyin=pinyin)
        
        if RADICAL in composition:
            idx = composition.index(RADICAL)
            radical = composition[idx + 2]
            
            print("Radical", radical)

            repository.touch_char(radical, is_radical=True)
            repository.has_radical(char, radical)

        if STRUCTURE in composition:
            idx = composition.index(STRUCTURE)
            structure = composition[idx + 1][1:].split(" + ")

            if '*' in structure:
                idx = structure.index('*')
                del structure[idx]

            print("Structure", structure)

            for composee in structure:
                repository.touch_char(composee)
                repository.composed_with(char, composee)

        antonyms = self.get_antonyms()

        for antonym in antonyms:
            repository.touch_char(antonym)
            repository.is_antonym(char, antonym)

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
