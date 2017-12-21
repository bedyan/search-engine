#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.shortcuts import render
from .models import UrlFile, WordPosition
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.validators import URLValidator, ValidationError
from crawler import Crawler
import math
import re
# Create your views here.


class Answer(object):
    def __init__(self, number, url_file, text):
        self.url_file = url_file
        self.text = text
        self.number = number


class Searcher(object):
    def __init__(self):
        self.search_results = list()
        self.link_dict = dict()
        self.doc_count = len(UrlFile.objects.all())
        self.doc_text = dict()

    def find_documents(self, words):
        for word in words:
            word_urls = WordPosition.objects.filter(word=word)
            for word_item in word_urls:
                score = math.log((self.doc_count - len(word_urls) + 0.5) / float(len(word_urls) + 0.5))
                if score < 0.1:
                    score = 0.1
                doc = word_item.url_file
                if doc in self.link_dict:
                    self.link_dict[doc] += score * word_item.rank
                else:
                    self.link_dict[doc] = score * word_item.rank
                    temp = re.sub(ur'[\W|\d]', u' ', doc.text, flags=re.UNICODE).split()
                    doc_len = len(temp)
                    self.doc_text[doc] = ' '.join(temp[doc_len // 2 - 15: doc_len // 2 + 15])
        search_results = sorted(list(self.link_dict.items()), key=lambda x: x[1], reverse=True)
        for pos, elem in enumerate(search_results):
            url, rank = elem
            self.search_results.append(Answer(pos, url,self.doc_text[url]))


def url_list(request):
    file = UrlFile.objects.all()
    words = WordPosition.objects.filter(url_file=file)
    if request.method == 'GET':
        qd = request.GET
    elif request.method == 'POST':
        qd = request.POST['query']
    return render(request, 'search/home.html', {'html_index':1})


def url_answer(request):
    query = u''
    try:
        if request.method == "POST":
            query = request.POST.get('query')
        else:
            query = request.GET.get('query')
    except:
        pass
    links_list = list()
    links = set()
    qq = re.sub(ur'[\W|\d]', u' ', query, flags=re.UNICODE)
    words = query.lower().split(' ')
    searcher = Searcher()
    searcher.find_documents(words)
    links_list = searcher.search_results
    paginator = Paginator(links_list, 15)

    page = request.GET.get('page')
    try:
        links_list = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        links_list = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        links_list = paginator.page(page)
    pages = []
    for num in range(int(page) - 2, int(page) + 3):
        if num < 1 or num > paginator.num_pages:
            continue
        pages.append(num)

    return render(request, 'search/url_list.html', {'links': links_list, 'query':query, 'pages':pages, 'page_count':paginator.num_pages, 'html_index':1, 'short_text':searcher.doc_text})


def all_docs(request):
    links = UrlFile.objects.all()
    paginator = Paginator(links, 30)
    page = request.GET.get('page')
    try:
        links = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        links = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        links = paginator.page(page)
    my_range = []
    for num in range(int(page) - 2, int(page) + 3):
        if num < 1 or num > paginator.num_pages:
            continue
        my_range.append(num)

    return render(request, 'search/all_docs.html', {'links':links, 'pages':my_range, 'page_count':paginator.num_pages, 'html_index':2})


def add_doc(request):
    if request.method == "POST":
        urls_for_indexing = []
        uv = URLValidator(schemes=['http', 'https'])

        urls_from_form = request.POST.get('url')
        if urls_from_form:
            list_urls = urls_from_form.split(", ")
            for url in list_urls:
                try:
                    uv(url)
                except ValidationError:
                    continue

                urls_for_indexing.append(url)

        file_with_urls = request.FILES.get('file_url')
        if file_with_urls:
            for url in file_with_urls:
                url = url.strip()
                try:
                    uv(url)
                except ValidationError:
                    continue

                urls_for_indexing.append(url)
        if len(urls_for_indexing):
            crawler = Crawler(urls_for_indexing, width=20, deep=3)
            crawler.craaawl()
            text = 'Finished'
        else:
            text = 'Invalid URL'

    else:
        text = ''

    return render(request, 'search/add_doc.html', {'text':text })
