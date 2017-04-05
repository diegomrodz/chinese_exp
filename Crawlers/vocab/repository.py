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

def touch_char(char, **kwargs):
    node = Character(char, **kwargs)
    
    if node["count"] is None:
        node["count"] = 1
    else:
        node["count"] += 1

    graph.merge(node, "Character", {"char": node["char"]})

def touch_definition(definition, **kwargs):
    node = Definition(definition, **kwargs)

    if node['count'] is None:
        node['count'] = 1
    else:
        node['count'] += 1
    
    graph.merge(node, "Character", {"definition": node["definition"]})

def has_radical(char, radical):
    rel = HasRadical(Character(char), Character(radical))
    graph.merge(rel)

def composed_with(composed, composee):
    rel = ComposedWith(Character(composed), Character(composee))
    graph.merge(rel)

def is_antonym(antonym, antonymee):
    rel = IsAntonym(Character(antonym), Character(antonymee))
    graph.merge(rel)

    rel = IsAntonym(Character(antonymee), Character(antonym))
    graph.merge(rel)

def means(char, definition):
    rel = Means(Character(char), Definition(definition))
    graph.merge(rel)