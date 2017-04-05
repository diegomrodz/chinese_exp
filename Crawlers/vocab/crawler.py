import scrapy
import re
import nltk
import repository

# The base url for searching a char in the Purple Culture Dictionary
PURPLE_URL = "https://www.purpleculture.net/dictionary-details/?word={}"

TOTAL_STROKES = "Total strokes:"
RADICAL = "Radical:"
STRUCTURE = "Structure:"

visited = []

class VocabCrawler(scrapy.Spider):
    """ Implementing the Crawler starting on the word 爱 (love).
    """
    name = 'vocab_crawler'
    start_urls = [PURPLE_URL.format("爱")] # Lets start with love!
    
    def parse(self, response):
        self.set_response(response)

        word = self.get_word()
   
        visited.append(word)    

        if len(word) > 1:
            requests = self.process_word(word)
        else:
            requests = self.process_char(word[0])
        
        for req in requests:
            yield req

    def process_word(self, word):
        print("[LOG] Processing Word:", word)

        pinyin = "".join(self.get_pinyin())
        repository.touch_word(word, pinyin=pinyin)

        for char in word:
            repository.touch_char(char)
            repository.composed_with(word, char)

            if not char in visited:
                yield scrapy.Request(PURPLE_URL.format(char), callback=self.parse)

        for definition in self.get_definitions():
            if definition != "" and definition != "Classifiers:":
                repository.touch_definition(definition)
                repository.means(word, definition)
    
    def process_char(self, char):
        print("[LOG] Processing Char:", char)

        pinyin = self.get_pinyin()[0]

        for definition in self.get_definitions():
            if definition != "" and definition != "Classifiers:":
                repository.touch_definition(definition)
                repository.means(char, definition)

        composition = self.get_composition()

        if TOTAL_STROKES in composition:
            idx = composition.index(TOTAL_STROKES)
            total_strokes = composition[idx + 1][1:-2]

            repository.touch_char(char, pinyin=pinyin, strokes=total_strokes)
        else:
            repository.touch_char(char, pinyin=pinyin)
        
        if RADICAL in composition:
            idx = composition.index(RADICAL)
            radical = composition[idx + 2]

            if radical != char:
                repository.touch_char(radical, is_radical=True)
                repository.has_radical(char, radical)

                if not radical in visited:
                    yield scrapy.Request(PURPLE_URL.format(radical), callback=self.parse)

        if STRUCTURE in composition:
            idx = composition.index(STRUCTURE)
            structure = composition[idx + 1][1:].split(" + ")

            if '*' in structure:
                idx = structure.index('*')
                del structure[idx]

            for composee in structure:
                if composee != char:
                    repository.touch_char(composee)
                    repository.composed_with(char, composee)

                    if not composee in visited:
                        yield scrapy.Request(PURPLE_URL.format(composee), callback=self.parse)

        antonyms = self.get_antonyms()

        for antonym in antonyms:
            if len(antonym) > 1:
                repository.touch_char(antonym)
            else:
                repository.touch_word(antonym)

            repository.is_antonym(char, antonym)

            if not antonym in visited:
                yield scrapy.Request(PURPLE_URL.format(antonym), callback=self.parse)

        for word in self.get_swords():
            if word != "":
                for part in word.split(","):
                    if not part in visited:
                        yield scrapy.Request(PURPLE_URL.format(part.strip()), callback=self.parse)

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
