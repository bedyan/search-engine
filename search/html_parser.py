# -*- coding: utf-8 -*-
import urlparse
import robotparser
import urllib2
from bs4 import BeautifulSoup
import re
import os.path
from base64 import b16encode
import time
import os
import sys
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from .models import UrlFile, WordPosition

class HtmlParser(object):
    def __init__(self, url):
        self.url = unicode(url)
        self.is_error = False
        self.links = list()
        self.soup = BeautifulSoup('', 'html.parser')
        self.storage_dir = 'temp'
        self.error = 'All right'
        self.title = None
        self.text = ''
        try:
            #print '-----------------Start working with ', self.url
            self.download_html()
            self.text_from_html()
            self.title_from_html()
            self.list_of_links_from_html()
        except Exception:
            self.is_error = True

    def download_html(self):
        try:
            objects_list = UrlFile.objects.filter(url=b16encode(unicode(self.url)))
            if len(objects_list) != 0:
                self.error = True
                return None
            parsed_url = urlparse.urlparse(unicode(self.url))
            rp = robotparser.RobotFileParser()
            rp.set_url(parsed_url.scheme + "://" + parsed_url.hostname + "/robots.txt")
            rp.read()
            if rp.can_fetch("*", self.url):
                html_doc = urllib2.urlopen(self.url).read()
                self.soup = BeautifulSoup(html_doc, 'html.parser')
        except:
            self.is_error = True
            self.soup = None
            return None

    def text_from_html(self):
        if not self.is_error:
            if True:
            #stored_text_file_name = os.path.join(self.storage_dir, b16encode(self.url))
            #if not os.path.exists(stored_text_file_name):
            #    stored_text_file = open(stored_text_file_name, 'w')
                [s.replace_with(' ') for s in self.soup.find_all(['style', 'script', '[document]', 'head', 'title'])]
                #self.text = ' '.join(self.soup.get_text().split())
                self.text = self.soup.get_text()
                self.text = '\n '.join(self.text.split())
                text = re.sub(u'\.|\,|\"|\'|\:|\!|\?|\*|\-|\+|\_|\(|\)|\&|\^|\%|\$|\#|\@|\~|\{|\}|\[|\]|\`', ' ', self.text)
                text = text.replace('\\', ' ').replace('/', ' ').replace('|', ' ').lower()
                #stored_text_file.write(text.encode('utf8'))
                #stored_text_file.close()
                UrlFile.objects.create(url=b16encode(unicode(self.url)), text=text.encode('utf-8'))
        else:
            self.text = None

    def title_from_html(self):
        if not self.is_error:
            try:
                self.title = self.soup.title.string.encode('utf-8')
            except Exception:
                self.title= None
        else:
            self.title = None

    def dict_of_words_from_html(self):
        pass

    def list_of_links_from_html(self):
        if not self.is_error:
            links = set()
            parsed_url = urlparse.urlparse(self.url)
            rp = robotparser.RobotFileParser()
            robots_url = parsed_url.scheme + "://" + parsed_url.hostname + "/robots.txt"
            aaa = tuple([parsed_url.scheme, parsed_url.hostname, '/robots.txt', '','',''])
            robots_url_parsed = urlparse.urlunparse(aaa)
            rp.set_url(robots_url_parsed)
            regex = re.compile(r'.*\.(doc|rss|docx|pdf|jpg|exe|pkg|msi|png|zip|tiff|php|gif|chm|asc|dmg)$')
            rp.read()
            for elem in self.soup.find_all('a'):
                link = elem.get('href')
                #print link
                temp = ''
                if link is None:
                    continue
                if link.startswith('//'):
                    temp = parsed_url.scheme + ':' + link
                elif not regex.match(link) is None:
                    print 'IGNORE:   ', link
                    continue
                elif link.startswith('/'):
                    temp = (parsed_url.scheme + '://' + parsed_url.hostname + link).encode('utf-8')
                    if unicode(str(temp)) != unicode(temp):
                        print str(temp)
                        print unicode(temp)
                        continue
                    #print temp
                elif link.startswith('http://') or link.startswith('https://'):
                    temp = link
                elif link.startswith('#') or link.startswith('javascript:'):
                    continue
                elif '://' in link:
                    continue
                else:
                    temp = urlparse.urljoin(unicode(self.url), unicode(link))
                parsed_temp = urlparse.urlparse(temp)
                if rp.can_fetch('*', temp) and parsed_temp.hostname == parsed_url.hostname:
                    objects_list = UrlFile.objects.filter(url=b16encode(unicode(temp)))
                    if len(objects_list) == 0:
                        links.add(temp)
            self.links = list(links)
                #print 'link', temp
        else:
            self.links = None

def search_warnings():
    print "Hello from html_parser.search_warnings()"
    my_url = HtmlParser('https://www.python.org/')

    #print len(my_url.links), my_url.links
    parsers = []
    alal = 'jfk'
    time.sleep(3)
    for link in my_url.links[:20]:
        try:
            pars = HtmlParser(link)
            print pars.is_error, link
            print '\t', pars.links
            parsers.append(pars)
            time.sleep(3)
        except:
            pass
    print len(my_url.links), my_url.links
    print my_url.is_error


if __name__=='__main__':
    print 'Hello from main'
    search_warnings()