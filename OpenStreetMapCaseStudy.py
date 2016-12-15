#!/usr/bin/env python
# -*- coding: utf-8 -*-


import xml.etree.ElementTree as ET  
import pprint
import re
from collections import defaultdict
import cerberus
import codecs
import csv
import sqlite3

# ================================================== #
#      Creating a sample file and viewing data       #
# ================================================== #


OSM_FILE = "santiago.osm"  
SAMPLE_FILE = "sample.osm"
k = 10 # Parameter: take every k-th top level element


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

''' The following code uses the get_element function, as well as the parameter k, to create a sample 1/kth the size of the original '''

with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))
    output.write('</osm>')


''' The following code prints the first 10 elements of the osm file '''

print "First ten elements of the sample file:"
for i, element in enumerate(get_element('sample.osm')):
    print(ET.tostring(element, encoding='utf-8'))
    if i == 10:
        break

'''The following code creates a dictionary of dictionaries of the secondary tags found in a node and prints it'''
 if the value is not an empty dictionary 

tree = ET.parse('sample.osm')
root = tree.getroot()
nodecount = 0
node_dict = {}
for node in root.findall('node'):
    node_dict[nodecount] = {}
    tagcount = 0
    for tag in node.findall('tag'):
        node_dict[nodecount][tagcount] = tag.attrib['k'] + ":" + (tag.attrib['v'])
        tagcount +=1
    nodecount += 1

print "Node tags:"
for i in node_dict:
    if bool(node_dict[i]):
        pprint.pprint(node_dict[i])



# ================================================== #
#               Auditing Functions                   #
# ================================================== #

def count_tags(filename):
    """
    Finds the different tag names and counts the instances of each in an XML file     
         Args:
                filename: an XML file
         Returns:
                tag_dict: a dictionary with keys of all the tag names, and values equal to how many times the tag appears in the file
    """

    tag_dict = {}
    iter = ET.iterparse(open(filename, "r"))
    for _, item in iter:
        if item.tag in tag_dict.keys():
            tag_dict[item.tag] +=1
        else:
            tag_dict[item.tag] = 1
    return tag_dict


#creates regular expressions for lower case characters, lower case characters including one or more colons, and non alphanumeric characters
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    """
    Determines the type of tag present in an element    
         Args:
                element: an element of an XML file
                keys: a dictionary where key values are the type of key, and the count is the value 
         Returns:
                   keys: an updated version of the argument
    """
    if element.tag == "tag":
        attr = element.attrib['k']
        if lower.search(attr):
            keys["lower"] += 1
        elif lower_colon.search(attr):
            keys["lower_colon"] += 1
        elif problemchars.search(attr):
            keys["problemchars"] +=1
        else:
            keys["other"] += 1
    return keys


def tagkeycount(filename):
    """
    Determines the type of tag present in an element    
         Args:
                element: an element of an XML file
                keys: a dictionary where key values are the type of key, and the count is the value 
         Returns:
                keys: an updated version of the argument
    """
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys

def probchars(filename):
    """
    Determines the type of tag present in an element    
         Args:
                filename: an XML file
         Returns:
                prob_tags: a dictionary of the tags which contain problematic characters
    """
    prob_tags = {}
    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            attr = element.attrib['k']
            if problemchars.search(attr):
                prob_tags[element] = attr, element.attrib['v']
    return prob_tags

def tagkeys(filename):
    """
    Counts the various key attributes found in tags of an xml file
         Args:
                filename: an XML file
         Returns:
                prob_tags: a dictionary of keys used in tags, and how many times they appear
    """
    tag_keys = {}
    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            attr = element.attrib['k']
            if attr in tag_keys.keys():
                tag_keys[attr] +=1
            else:
                tag_keys[attr] =1
    return tag_keys


def dict_print_by_value(d):
    """
    Prints a dictionary ordered by its values in descending order
    Reference:
    http://stackoverflow.com/questions/11228812/print-a-dict-sorted-by-values    
         Args:
                d: any dictionary
    """
    d_view = [ (v,k) for k,v in d.iteritems() ]
    d_view.sort(reverse=True) 
    for v,k in d_view:
        print ("%s: %d" % (k,v))

def try_int(s):

    try:
        return int(s)
    except ValueError:
        return str(s)

def house_numbers(filename):
    '''
    #Searches for house numbers that are not integer values
    Args: 
        filename - an OSM file
    Returns:
        number_errors: A list of non-int values 
    '''
    number_errors = []
    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            if element.attrib['k'] == "addr:housenumber":
                if not isinstance( try_int(element.attrib['v']), int ):
                    number_errors.append(element.attrib['v'])
    return number_errors

numbers = re.compile('\d')



def streets(filename):
    """
    Creates a dictionary of all street names found under the "addr:street" tag
    Args: 
        filename - an OSM file
    Returns:
        streets - a dictionary of street names and how many times they occur
    """
    streets = {}
    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            if element.attrib['k'] == "addr:street":
                if element.attrib['v'] not in streets:
                    streets[element.attrib['v']] = 1
                else:
                    streets[element.attrib['v']] += 1
    return streets

def tagfinder(filename, tag):
    """
    Creates a dictionary of all values for a given key
    Args: 
        filename - an OSM file
        tag - the key value for a given tag
    Returns:
        names - a dictionary of value names for a given key and how many times they occur
    """
    names = {}
    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            if element.attrib['k'] == tag:
                if element.attrib['v'] not in names:
                    names[element.attrib['v']] = 1
                else:
                    names[element.attrib['v']] += 1
  
    return names

def get_user(element):
    ''' Returns the user id from an element'''
    if element.get('uid'):
        return element.get('uid')
        print element.get('uid')
    else:
        return None

def number_users(filename):
    ''' Returns the number of unique user ids in an osm file'''
    users = set()
    for _, element in ET.iterparse(filename):
        if get_user(element):
            if get_user(element) not in users:
                users.add(get_user(element))
    return users

users = number_users('santiago.osm')
print "There are {0} unique users contributing to this data set.".format(len(users))

tags = count_tags('sample.osm')
print "Tags present"
pprint.pprint(tags)

keys = tagkeycount('sample.osm')
print "Types of tags present:"
pprint.pprint(keys)

print "Problematic tags:"
pprint.pprint(probchars('sample.osm'))

tag_key_values = tagkeys('sample.osm')
print "Tag Keys:"
dict_print_by_value(tag_key_values)

print "Addr:housenumber values which are not integers:"
pprint.pprint(house_numbers('sample.osm'))
print "There are {0} total house numbers which are not integers.".format(len(house_numbers('sample.osm')))

street_values = streets('sample.osm')
print "Streets:"
pprint.pprint(street_values)

'''Prints street names with "."'''
streetcount = 0
for street in street_values:
    if street.find('.')!=-1:
        streetcount +=1
        print street #.decode('utf-8') 

print "There are {0} streets with the '.' character in them.".format(streetcount)

print "Name values:"
dict_print_by_value(tagfinder('sample.osm', 'name'))
print "Addr:interpolation values:"
dict_print_by_value(tagfinder('sample.osm', 'addr:interpolation'))
print "Highway values:"
dict_print_by_value(tagfinder('sample.osm', 'highway'))
print "Source values:"
dict_print_by_value(tagfinder('sample.osm', 'source'))
print "Id_origin values:"
dict_print_by_value(tagfinder('sample.osm', 'id_origin'))

'''Creates a dictionary of nodes, each node has a list of the secondary tags assigned to it'''

tag_list={}
nodecount=0
for node in root.findall('node'):
    tag_list[nodecount] = []
    for tag in node.findall('tag'):
        tag_list[nodecount].append(tag.attrib['k'])
    nodecount += 1

'''Counts the number of nodes which have both an amenity and name tag and nodes that have only an amenity tag with no name,
same for street names and regular name tags '''

ns_count =0
na_count = 0
amenity_only = 0
street_only =0

for node in tag_list:
    if ('name' in tag_list[node]):
        if ('amenity' in tag_list[node]):
            na_count +=1
        if ('addr:street' in tag_list[node]):
            ns_count +=1
    elif ('amenity' in tag_list[node]):
        amenity_only +=1
    elif ('addr:street' in tag_list[node]):
        street_only +=1
        
print "Nodes with both amenity and name tags: " + str(na_count)
print "Nodes with with an amenity but no name tag: " + str(amenity_only)
print
print "Nodes with both addr:street and name tags: " + str(ns_count)
print "Nodes with with street but no name tag: " + str(street_only)


# ================================================== #
#                  Fixing functions                  #
# ================================================== #

'''mapping dictionary for fixing abbreviations in street names'''

mapping = { "A.": "Avenida",
            "Av.": "Avenida",
            "Av" : "Avenida",
            "Avda." : "Avenida",
            "Avda" : "Avenida",
            "Ave.": "Avenida",
            "Ave": "Avenida",
            "Co.": "Cerro",
            "Co" : "Cerro",
            "Psje." : "Pasaje",
            "Psje" : "Pasaje",
            "Pje." : "Pasaje",
            "Pje" : "Pasaje",
            "Fco." : "Francisco",
            "Fco" : "Francisco",
            "Sta. " : "Santa",
            "Sta" : "Santa"
            }

''' mapping dictionary to update sources '''

sources= {'www.ine.cl' : 'Instituto Nacional de Estadistica www.ine.cl',
            'Instituto Nacional De Estadisticas': 'Instituto Nacional de Estadistica www.ine.cl',
            'Bing' : "Bing",
            "bing" : "Bing",
            "2016 por KG" : "Reconocimiento cartográfico 2016 por KG"}


def update_streetname(name, mapping):
    '''Changes a portion of a key to a its value in a mapping dictionary'''
    for error in mapping.keys():
        if error in name:
            name = re.sub(r'\b' + error + r'\b\.?', mapping[error], name)
    return name

def update_sourcename(name, mapping):
    '''Changes a name from a key to a its value in a mapping dictionary'''
    for error in mapping.keys():
        if error in name:
            name = ma

streets = ["Av.", "Ave", "Avda.", "Avenida", "Calle", "Camino", "Diagonal",  "Pje", "Pje.", "Psje", "Pasaje"]

def name_street_fix(element, street_values, street):
    ''' For "name" values: 
    if it contains an already exising street name, the tag key is changed to addr:street
    if contains a common street abbreviation or classifier, the tag key is changed to addr:street
    Args:
        element: element from an OSM file
        street_values: a list of street names from the OSM file
        streets: a list of common street abbreviations 
    Returns:
        element: updated element 
    '''

    if element.attrib['k'] == "name":
        for street in street_values:
            if element.attrib['v'] == street:
                    element.attrib['k'] = 'addr:street'
        # If the name value has a common street classifier in it, the tag key is changed to "addr:street"   
        for street in streets:
            if element.attrib['v'].find(street):
                element.attrib['k'] = 'addr:street'
    return element

                  
def addressfix(element):
    '''
    If a housenumber does not contain any numeric characters, it's key tag ("k"=) is changed to a "name" rather than "addr:housenumber" 
    Args: 
        element - an element from an OSM file
    Returns:
        element - updated element
    '''
    if element.attrib['k'] == "addr:housenumber":
        if not(numbers.search(element.attrib['v'])):
            if (element.attrib['v'] != "s/n"): 
                if (element.attrib['v'] != "S/N"):
                    print element.attrib['v']
                    element.attrib['k'] = 'name'
    return element


def Hualtatasfix(element):
    ''' For "addr:interpolation" values:
    If the value is neither "odd" nor "even" changes the tag key to addr:street and returns the element
    '''

    if element.attrib['k'] == 'addr:interpolation':
        if (element.attrib['v'] != 'even' and element.attrib['v'] != 'odd'):
            element.attrib['k'] = 'addr:name'
    return element

          
def fix(element):
    ''' Runs all fix functions on an element '''
    element = addressfix(element)
    element = Hualtatasfix(element)
    element = name_street_fix(element, street_values, street)
    if elem.attrib['k'] == "addr:street":
        element.attrib['v'] = update_streetname(element.attrib['v'], mapping)
    if element.attrib['k'] == 'source':
        element.attrib['v'] = update_sourcename(element.attrib['v'], sources)
    return element


# ================================================== #
#                  Schema for CSV files              #
# ================================================== #

schema = {
    'node': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'lat': {'required': True, 'type': 'float', 'coerce': float},
            'lon': {'required': True, 'type': 'float', 'coerce': float},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'node_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    },
    'way': {
        'type': 'dict',
        'schema': {
            'id': {'required': True, 'type': 'integer', 'coerce': int},
            'user': {'required': True, 'type': 'string'},
            'uid': {'required': True, 'type': 'integer', 'coerce': int},
            'version': {'required': True, 'type': 'string'},
            'changeset': {'required': True, 'type': 'integer', 'coerce': int},
            'timestamp': {'required': True, 'type': 'string'}
        }
    },
    'way_nodes': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'node_id': {'required': True, 'type': 'integer', 'coerce': int},
                'position': {'required': True, 'type': 'integer', 'coerce': int}
            }
        }
    },
    'way_tags': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'required': True, 'type': 'integer', 'coerce': int},
                'key': {'required': True, 'type': 'string'},
                'value': {'required': True, 'type': 'string'},
                'type': {'required': True, 'type': 'string'}
            }
        }
    }
}


# ================================================== #
#       Element shaping/CSV file creation            #
# ================================================== #


OSM_PATH = "santiago.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    way_tags = []
    
    #Create node data structure
    if element.tag == 'node':
    #Fills in node_attribs dictionary
        for item in element.attrib:
            if item in node_attr_fields:
                node_attribs[item] = element.attrib[item]
    #Fills in secondary tags list of dicts
        for child in element:
            temp = {}
            temp["id"] = element.attrib['id']
            temp["value"] = child.attrib['v']
            child = fix(child)
            if re.match(problem_chars, child.attrib['k']):
                pass
            k = child.attrib['k'].split(":")
            if len(k)==1:
                temp["type"] = default_tag_type
                temp["key"] = child.attrib["k"]
            if len(k)==2:
                temp["type"] = k[0]
                temp["key"] = k[1]
            elif len(k)>2:
                k = child.attrib['k'].split(":", 1)
                temp["type"] = k[0]
                temp["key"] = k[1]
            tags.append(temp)

    #Create way data structure
    if element.tag == 'way':
    #Fills in the way attribs dictionary
        for item in element.attrib:
            if item in way_attr_fields:
                way_attribs[item] = element.attrib[item]
                
    #Fills in the way_nodes list
        count = 0
        for child in element:
            if child.tag == "nd":
                temp1 = {}
                temp1["id"] = element.attrib["id"]
                temp1["node_id"] = child.attrib["ref"]
                temp1["position"] = count
                count +=1
                way_nodes.append(temp1)
                
    #Fills in the tags list of dicts for way
            if child.tag == "tag":
                temp2 = {}
                temp2["id"] = element.attrib["id"]
                temp2["value"] = child.attrib["v"]
                if re.match(problem_chars, child.attrib['k']):
                    pass
                child =fix(child)
                k = child.attrib['k'].split(":")
                if len(k)==1:
                    temp2["type"] = default_tag_type
                    temp2["key"] = child.attrib["k"]
                if len(k)==2:
                    temp2["type"] = k[0]
                    temp2["key"] = k[1]
                elif len(k)>2:
                    k = child.attrib['k'].split(":", 1)
                    temp2["type"] = k[0]
                    temp2["key"] = k[1]
                way_tags.append(temp2)
                
    if element.tag == 'node':            
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': way_tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))

class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #

def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)



# ================================================== #
#               SQL Querying                         #
# ================================================== #


'''Fetch records from santiago.db'''

db = sqlite3.connect("santiago.db")
c = db.cursor()

def execute_query(QUERY):
    '''executes an SQL query and prints the results '''
    c.execute(QUERY)
    rows = c.fetchall()
    pprint.pprint(rows)


nodes_count = '''
SELECT COUNT(*)
FROM nodes;
'''
print "The number nodes:"
execute_query(nodes_count)

#Count the number of ways
ways_count = '''
SELECT COUNT(*)
FROM ways;
'''
print "The number ways:"
execute_query(ways_count)

#Count the number of distinct users
users = '''
SELECT COUNT(DISTINCT(uid))          
FROM (SELECT uid FROM nodes 
UNION SELECT uid FROM ways);
'''
print "The number distinct users:"
execute_query(users)

#Display top ten users and their contributions
top10u = '''
SELECT nodes_ways.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) nodes_ways
GROUP BY nodes_ways.user
ORDER BY num DESC
LIMIT 10; '''

print "The top ten contributing users:"
execute_query(top10u)

#Finds the top five amenity tags from the top user 'Julio_Costa_Zambelli'
Juliotop5 = '''
SELECT tags.value, COUNT(*) as count 
FROM (SELECT key, user, value FROM (nodes JOIN nodes_tags ON nodes.id=nodes_tags.id) UNION ALL 
SELECT key, user, value FROM (ways JOIN ways_tags ON ways.id=ways_tags.id))tags

WHERE tags.user =  'Julio_Costa_Zambelli'
and tags.key = 'amenity'
GROUP BY tags.value
ORDER BY count DESC
limit 5; '''

print "Top five amenities from the top user, Julio_Costa_Zambelli :"
execute_query(Juliotop5)

#Counts the number of users contributing once
onehitwonder = '''
SELECT COUNT(*) 
FROM
    (SELECT e.user, COUNT(*) as num
     FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
     GROUP BY e.user
     HAVING num=1)  u;'''

print "Number of users contributing once:"
execute_query(onehitwonder)

#Prints the number of users contributing more than 10,000 elements
tenthou = '''
SELECT COUNT(*) 
FROM
    (SELECT e.user, COUNT(*) as num
     FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
     GROUP BY e.user
     HAVING num>10000)  u;'''

print "Number of users with over one thousand contributions:"
execute_query(tenthou)

tenthou2 = '''
SELECT sum(u.num) 
FROM
    (SELECT e.user, COUNT(*) as num
     FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
     GROUP BY e.user
     HAVING num>10000)  u;'''

print "Number of users with over one thousand contributions:"
execute_query(tenthou2)

#Comunas of Santiago listed by most common
comunas = '''
SELECT tags.value, COUNT(*) as count 
FROM (SELECT * FROM nodes_tags UNION ALL 
      SELECT * FROM ways_tags) tags
WHERE tags.key LIKE '%city'
GROUP BY tags.value
ORDER BY count DESC; '''

print "Comunas of Santiago listed from most to least data points"
execute_query(comunas)


#Finds the number of entries under various tags with the "is_in" key
comunas2 = '''
SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='is_in'
GROUP BY value
ORDER BY num DESC
LIMIT 10;'''

print " 'Is-in' tags listed from most to least data points"
execute_query(comunas2)

#Lists the top ten most common amenities
top10amen = '''
SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='amenity'
GROUP BY value
ORDER BY num DESC
LIMIT 10;'''

print "Top 10 amenities"
execute_query(top10amen)

#Top school operators 
schools = '''
SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='school') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='operator'
GROUP BY nodes_tags.value
ORDER BY num DESC;
'''

print "Top school operators"
execute_query(schools)

#Values for the "highway" key from most to least common
highway = '''
SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='highway' 
GROUP BY value
ORDER BY num DESC;'''

print "Top highway values"
execute_query(highway)


#Values for the "railway" key from most to least common
railway = '''
SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='railway' 
GROUP BY value
ORDER BY num DESC;'''

print "Top railway values"
execute_query(railway)


#Top 20 types of restaurants
rest = '''
SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='cuisine'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 20;'''

print "Top 20 types of restaurants"
execute_query(rest)

#Top 10 data sources
sources = '''
SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='source'
GROUP BY value
ORDER BY num DESC
LIMIT 10;'''

print "Top 10 data sources"
execute_query(data)

#Top ten amenities in Providencia
provi_amen = '''
SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='Providencia') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='amenity'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 10;'''

print "Top 10 amenities in Providencia"
execute_query(provi_amen)

#Top ten comunas with bicycle parking
bici = '''
SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='bicycle_parking') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key LIKE '%city'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 10;'''

print "Top 10 comunas with bicycle parking"
execute_query(bici)

#Top ten comunas by bus stop
busstops = '''
SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='bus_stop') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key LIKE '%city'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 10;'''

print "Top 10 comunas with busstops"
execute_query(busstops)

#Top ten comunas by number of schools
schoolcomunas = '''
SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='school') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key LIKE '%city'
GROUP BY nodes_tags.value
ORDER BY num DESC
Limit 10;'''

print "Top 10 comunas with schools"
execute_query(schoolcomunas)

#Top ten amenities in Lo Barnechea
lobaamen = '''
SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='Lo Barnechea') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='amenity'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 10;'''

print "Top 10 comunas amenities in Lo Barnechea"
execute_query(lobaamen)

#Top ten comunas by number of restaurants
restcomunas = '''
SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key LIKE '%city'
GROUP BY nodes_tags.value
ORDER BY num DESC
Limit 10;'''

print "Top 10 comunas with restaurants"
execute_query(restcomunas)

#Top ten comunas by number of banks
bankcomunas = '''
SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='bank') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key LIKE '%city'
GROUP BY nodes_tags.value
ORDER BY num DESC
Limit 10;'''

print "Top 10 comunas with banks"
execute_query(bankcomunas)

db.close()