#!/bin/env python3.6



import random
import time
import requests
import asyncio
import aiohttp
import re
import bs4
import asyncio
import os
import urllib.request
import time
import PyPDF2
from urllib.parse import urlparse



def is_absolute(url):
	return bool(urlparse(url).netloc)



async def get_url(url):
    print("Connecting with", url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            # ~ print(resp.status)
            if resp.status == 200:
                print('Done: URL {} '.format(url))
                return (await resp.text(), url)



# extract links with BeautifulSoup
def get_links_bs4(page):
    soup = bs4.BeautifulSoup(page, 'html.parser')
    links = soup.findAll('a', attrs={'href': re.compile("^http://")})
    return links


@asyncio.coroutine  # Décorateur pour marquer les coroutines à base de générateur.
async def process_as_results_come_in(k=3, URLs=['https://www.bbc.com/news/'], PDFs=[]):
    if k > 0:
        coroutines = [get_url(url) for url in URLs]
        URLs = []
        for coroutine in asyncio.as_completed(coroutines):
            try:
                result, url = await coroutine
                links = get_links_bs4(result)
            except:
                links = []
                print('No Urls')
            for link in links:
                try:
                    if is_absolute(link['href']):
                        if ('pdf' or 'PDF') in link['href'][-3:]:
                            PDFs.append(link['href'])
                        else:
                            URLs.append(link['href'])
                    else:
                        if ('pdf' or 'PDF') in link['href'][-3:]:
                            PDFs.append(url + link['href'])
                        else:
                            URLs.append(url + link['href'])
                except:
                    print('No Href links')
        await asyncio.ensure_future(process_as_results_come_in(k - 1, URLs, PDFs))
    if k == 0:
        print(PDFs)
    # ~ print(URLs)
    return PDFs



async def download_coroutine(url):
    l=0
    try:
        request = urllib.request.urlopen(url)
        if request.getcode() == 200:
            print('Web site exists')
        else:
            l=1
            print("Website returned response code: {code}".format(code=request.status_code))
    except:
        print('Web site does not exist')
        l=1
    filename = os.path.basename(url)
    if l==0:
        with open(filename, 'wb') as file_handle:
            while True:
                chunk = request.read(1024)
                if not chunk:
                    break
                file_handle.write(chunk)
        msg = 'Finished downloading {filename}'.format(filename=filename)
    if l==1:
        return 'ERROR'
    else:
        return filename




async def get_pdf_content_lines(fich):
    with open(fich, "rb") as f:
        pdf_reader = PyPDF2.PdfFileReader(f)
        for page in pdf_reader.pages:
            for line in page.extractText().splitlines():
                yield line




async def teste(fichier):
    name = ["lemme", "théorème", "lelasso", "preuve", "proposition", "max", "complexe", "math", "mathématiques"]
    l = 0
    for ligne in get_pdf_content_lines(fichier):
        for i in range(len(name)):
            if str(name[i]) in str(ligne):
                print(name[i] + " :  dans le pdf", fichier + ":peut etre un fichier  ")
                l = 1
    return l



async def main(urls,k):
    PDFs = await process_as_results_come_in(k=k, URLs=urls, PDFs=[])
    coroutines = [download_coroutine(url) for url in PDFs]
    pdf2 = []
    for coroutine in asyncio.as_completed(coroutines):
        filename = await coroutine
        if filename != 'ERROR':
            if teste(filename) == 0:
                pdf2.append(filename)
    for pdf in pdf2:
        try:
            os.remove(pdf)
        except:
            k = 0
    for pdf in PDFs:
        if os.path.basename(pdf) not in pdf2:
            print(os.path.basename(pdf))




if __name__ == '__main__':
    url = ['https://www.bbc.com/news/']
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(urls=url,k=3))


