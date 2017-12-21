#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import json
import os
import base64
from multiprocessing.dummy import Pool
import re

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from search.models import UrlFile, WordPosition

unique_error_docs = set()
average_doc_lenght = 0

banned_words = [u'и', u'а', u'но', u'да', u'или', u'что', u'как', u'чтобы', \
                u'с', u'к', u'на', u'от', u'над', u'по', u'у', u'о', u'под', u'из', \
                u'без', u'для', u'до', u'в', u'около', u'об', u'за',\
                u'a', u'the', u'an', u'in', u'on', u'at', u'to', u'into', u'by', \
                u'from', u'since', u'till', u'into', u'onto', u'before', u'after', u'of',\
                u'about', u'for', u'during', u'with', u'between', u'among', u'except', u'and']

count = 0

# indexing using BM25
def file_indexing(url_file):
    global count
    count += 1
    if count % 10 == 0:
        print count, url_file
    if len(WordPosition.objects.filter(url_file=url_file)) != 0:
        return 0
    global average_doc_lenght
    words = re.sub(ur'[\W|\d]', ur' ', url_file.text, flags=re.UNICODE).strip().split()
    words_dict = dict()
    doc_len = len(words)
    for word in words:
        if word not in banned_words and not re.match(r'^\w+$', word, re.UNICODE) is None and re.match('.*\d.*', word) is None:
            if word not in words_dict:
                words_dict[word] = 1
            else:
                words_dict[word] += 1
    k1 = 2
    b = 0.75
    for word, value in words_dict.items():
        if True:
            score = value * (k1 + 1) / float(value + k1*(1 - b + b * doc_len / float(average_doc_lenght)))

            WordPosition.objects.create(word=word, url_file=url_file, rank=score)
        else:
            pass


def get_average_doc_len():
    global average_doc_lenght
    file_list = UrlFile.objects.all()
    for fle in file_list:
        text = fle.text.split()
        average_doc_lenght += len(text)
    print average_doc_lenght, len(file_list)
    average_doc_lenght /= float(len(file_list))
    print average_doc_lenght


def create_index_from_db():
    file_list = UrlFile.objects.all()
    get_average_doc_len()
    pool = Pool(6)
    pool.map(file_indexing, file_list)
    pool.close()
    pool.join()


if __name__ == "__main__":
    create_index_from_db()
