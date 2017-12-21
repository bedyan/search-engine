import multiprocessing as mp
import html_parser
import time
import argparse


start_time = time.time()

unique_urls = set()


def _mp_crawler(queue, w):
    while True:
        elem = queue.get()
        if elem is None:
            break
        url, h = elem
        print h, url
        if h == 0 or w == 0:
            break
        else:
            html = html_parser.HtmlParser(url)
            links = html.links
            if not (links == [] or links is None) and h-1 != 0:
                for link in links[:w]:
                    queue.put((link, h-1))
        queue.task_done()
    queue.task_done()


class Crawler(object):
    all_links = list()

    def __init__(self, start_urls, width=20, deep=10):
        self.url_queue = start_urls
        self.deep = deep
        self.width = width

    def craaawl(self):
        nCPU = 8
        queue = mp.JoinableQueue()

        if len(self.url_queue) == 0:
            return None

        for url in self.url_queue:
            queue.put((url, self.deep))

        workers = []
        for i in range(nCPU):
            worker = mp.Process(target=_mp_crawler, args=(queue, self.width))
            workers.append(worker)
            worker.start()

        queue.join()
        for i in range(nCPU):
            queue.put(None)

        for i in range(nCPU):
            workers[i].join(None)


if __name__ == "__main__":
    file_name = ''
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--stored-documents_dir', dest='stored_documents_dir', required=False)
        parser.add_argument('--file-name', dest='file_name', required=True)
        args = parser.parse_args()
#        print args.stored_document_dir
        new_urls = list()
        file_name = args.file_name
        print type(file_name), file_name
    except:
        file_name = '/urls.txt'
    with open(file_name, 'r') as f:
        text = f.read()
        for line in text.split():
            new_urls.append(line)
    print new_urls
    craaaawl = Crawler(['https://djangogirls.org'], 'my_dir')
    craaaawl.craaawl()
    print time.time() - start_time
