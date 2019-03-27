#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
  wiki_dump_parser.py
  Script to convert a xml mediawiki history dump to a csv file with readable useful data
for pandas processing.
  Copyright 2017-2019 Abel 'Akronix' Serrano Juste <akronix5@gmail.com>

  Lines 106 to 194 are added by Jonne Deurloo
  The rest of the code has a few minor changes to work with links
"""

import xml.parsers.expat
import sys

__version__ = '2.0.1'

Debug = False

csv_separator = "?"

start_ignore = ["|Armed forces of ", "|Demography of ", "|Demographics of ", "|Economy of ", "|Foreign relations of ", "|Geography of ", "|Government of ",
                 "|History of ", "|Index of ", "|List of ", "|Military of ", "|Outline of ", "|Politics of ", "|Telecommunications in " "|Timeline of ", "|Transport in", "|Wikipedia:"]
end_ignore = ["(disambiguation)|", 'bibliography|', 'discography|']

start_symbols = ['<!--', '<ref',   '<code',   '<source',   '<syntaxhighlight']
end_symbols   = ['-->',  '</ref>', '</code>', '</source>', '</syntaxhighlight>', '/>']
def xml_to_csv(filename):

    ### BEGIN xmt_to_csv var declarations ###
    # Shared variables for parser subfunctions:
    ## output_csv, _current_tag, _parent
    # page_title,page_links

    output_csv = None
    _parent = None
    _current_tag = ''
    page_title = page_links = ''

    def start_tag(tag, attrs):
        nonlocal output_csv, _current_tag, _parent
        nonlocal page_title, page_links

        _current_tag = tag

        if tag == 'page' or tag == 'revision':
            _parent = tag

        if tag == 'upload':
            print("!! Warning: '<upload>' element not being handled", file=sys.stderr)

    def data_handler(data):
        nonlocal output_csv, _current_tag, _parent
        nonlocal page_title, page_links

        if _current_tag == '':  # Don't process blank "orphan" data between tags!!
            return

        if _parent:
            if _parent == 'page':
                if _current_tag == 'title':
                    page_title = '|' + data + '|'
            elif _parent == 'revision':
                if _current_tag == 'text':
                    data = data.replace('\n', ' ').replace('\r', '')
                    page_links += data

    def end_tag(tag):
        nonlocal output_csv, _current_tag, _parent
        nonlocal page_title, page_links

        def has_empty_field(l):
            field_empty = False
            i = 0
            while (not field_empty and i < len(l)):
                field_empty = (l[i] == '')
                i = i + 1
            return field_empty

        # uploading one level of parent if any of these tags close
        if tag == 'page':
            _parent = None
        elif tag == 'revision':
            _parent = 'page'
        elif tag == 'contributor':
            _parent = 'revision'

        # print revision to revision output csv
        if tag == 'revision':

            revision_row = [page_title, make_list(
                remove_non_links(filter_links(page_links, page_title)))]

            # Do not print (skip) revisions that has any of the fields not available
            if (not has_empty_field(revision_row)) and (not is_unwanted_title(page_title)):
                output_csv.write(csv_separator.join(revision_row) + '\n')
            # else:
                # print(
                #     "The following line has imcomplete info and therefore it's been removed from the dataset:")
                # print(revision_row)

            # Debug lines to standard output
            if Debug:
                print(csv_separator.join(revision_row))

            # Clearing data that has to be recalculated for every row:
            page_links = ''

        _current_tag = ''  # Very important!!! Otherwise blank "orphan" data between tags remain in _current_tag and trigger data_handler!! >:(

    def is_unwanted_title(t):
        return isinstance(starts_with(t, start_ignore), int) or (isinstance(ends_with(t, end_ignore), int) and len(t.split()) > 1)
    
    def filter_links(text, title):
        text = text.replace('[[', ' [[').replace(']]', ']] ')
        text = text.replace('<br>', ' ')
        text = text.replace('<br', '<ref ')

        for start_symbol in start_symbols:
            text = text.replace(start_symbol, ' ' + start_symbol + ' ')
        for end_symbol in end_symbols:
            text = text.replace(end_symbol, end_symbol + ' ')

        split = text.split(' ')

        if (split[0].upper() == '#REDIRECT'):
            return ''
        else:
            return_txt = []
            link = 0
            skip = 0
            start = end = None
            for word in split:
                start = start if isinstance(
                    start, int) else starts_with(word, start_symbols)
                
                if isinstance(start, int) and (start == starts_with(word, start_symbols)):
                    skip += 1
                    continue
                
                end = ends_with(word, end_symbols)
                if isinstance(end, int) and (end == start):
                    skip -= 1
                    end = start = None
                    continue

                if (end == 5):
                    skip -= 1
                    end = start = None
                    continue

                if skip == 0:
                    if word.startswith('[['):
                        link += 1
                    if word.endswith(']]') and link > 0:
                        link -= 1
                        return_txt.append(word)

                    if link > 0 and not word.endswith(']]'):
                        return_txt.append(word)

            return ' '.join(return_txt)

    def remove_non_links(text):
        split = text.split(' ')
        return_txt = []
        other = 0

        start_symbols = ['[[File:', '[[Category:',
                         '[[Image:', '[[Wikipedia:', '[[wikt:']

        for word in split:
            if isinstance(starts_with(word, start_symbols), int):
                other += 1
                if word.endswith(']]'):
                    other -= 1
                    continue
            elif word.startswith('[[') and other > 0:
                other += 1

            if other == 0:
                return_txt.append(word)

            if word.endswith(']]'):
                if other != 0:
                    other -= 1

        return ' '.join(return_txt).replace('?', '')

    def make_list(text):
        text = text[2:-2]
        return_txt = []

        for word in text.split(']] [['):
            return_txt.append(word.split('|')[0])

        return_txt = [title for title in return_txt if not is_unwanted_title(title)]
        return ' // '.join(return_txt)

    def starts_with(word, elements):
        for idx, elem in enumerate(elements):
            if word.startswith(elem):
                return idx

        return None

    def ends_with(word, elements):
        for idx, elem in enumerate(elements):
            if word.endswith(elem):
                return idx

        return None

    ### BEGIN xml_to_csv body ###

    # Initializing xml parser
    parser = xml.parsers.expat.ParserCreate()
    input_file = open(filename, 'rb')

    parser.StartElementHandler = start_tag
    parser.EndElementHandler = end_tag
    parser.CharacterDataHandler = data_handler
    parser.buffer_text = True
    parser.buffer_size = 1024

    # writing header for output csv file
    output_csv = open(filename[0:-3]+"csv", 'w', encoding='utf8')
    output_csv.write(csv_separator.join(["title", "links"]))
    output_csv.write("\n")

    # Parsing xml and writting proccesed data to output csv
    print("Processing...")
    parser.ParseFile(input_file)
    print("Done processing")

    input_file.close()
    output_csv.close()

    return True
