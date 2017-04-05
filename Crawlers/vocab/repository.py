from py2neo import Graph
from py2neo import Node
from py2neo import Relationship

graph = Graph(password="cogch")

class HasRadical(Relationship): pass
class ComposedWith(Relationship): pass
class IsAntonym(Relationship): pass
class Means(Relationship): pass

def Character(char, **kwargs):
    return Node("Character", char=char, **kwargs)

def Definition(definition, **kwargs):
    return Node("Definition", definition=definition, **kwargs)    

def Word(word, **kwargs):
    return Node("Word", word=word, **kwargs)

def touch_char(char, **kwargs):
    node = Character(char, **kwargs)
    graph.merge(node, "Character", {"char": char})

def touch_definition(definition, **kwargs):
    node = Definition(definition, **kwargs)
    graph.merge(node, "Character", {"definition": definition})

def touch_word(word, **kwargs):
    node = Word(word.strip("*"), **kwargs)
    graph.merge(node, "Word", {"word": word})

def has_radical(char, radical):
    rel = HasRadical(Character(char), Character(radical))
    graph.merge(rel)

def composed_with(composed, composee):
    if len(composed) > 1:
        rel = ComposedWith(Word(composed), Character(composee))
    else:
        rel = ComposedWith(Character(composed), Character(composee))
    
    graph.merge(rel)

def is_antonym(antonym, antonymee):
    rel = IsAntonym(Character(antonym), Character(antonymee))
    graph.merge(rel)

    rel = IsAntonym(Character(antonymee), Character(antonym))
    graph.merge(rel)

def means(word, definition):
    if len(word) > 1:
        rel = Means(Word(word), Definition(definition))
    else:
        rel = Means(Character(word), Definition(definition))
    
    graph.merge(rel)