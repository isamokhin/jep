# -*- coding: utf-8 -*-
# script for downloading all Journal of Economic Perspectives articles and creating of database of the articles (in csv format)
# messy but working. all pdf files take 688 Mb of disk space

import pandas as pd
from tqdm import tqdm
import requests
import time
from bs4 import BeautifulSoup
import os

BASE_URL = "https://www.aeaweb.org/articles.php?doi=10.1257/jep."
PATH = "JEP/"
df = pd.DataFrame(columns=["year", "issue", "part", "authors", "article", "url", "data_url"])
issues = [(i,j) for i in range(1,31) for j in range(1,5)]
issues = issues[:-3]
seasons = {1: "Winter", 2: "Spring", 3: "Summer", 4: "Fall"}

for issue in tqdm(issues[67:]):
    volume = "{vol}.{iss}".format(vol=issue[0], iss=issue[1])
    year = issue[0]+1986
    season = seasons[issue[1]]
    volf = "%.2d" % issue[0] 
    folder = "JEP Vol. {vol} No. {iss} ({season} {year})".format(vol=volf, iss=issue[1], season=season, year=year)
    if not os.path.exists(PATH+folder):
        os.makedirs(PATH+folder)
    url = BASE_URL+volume
    r = requests.get(url)
    if r.status_code != 200:
        continue
    time.sleep(1)
    print folder
    soup = BeautifulSoup(r.text, "lxml")
    part = "Front Matter"
    count = 0
    for div in tqdm(soup.find_all("div", class_="line_space")):
        gnames = []
        fnames = []
        data_url = ""
        if div.find("div", class_="sub_head"):
            part = div.find("div", class_="sub_head").text
        for span in div.find_all("span", class_="given-name"):
            gnames.append(span.text.strip())
        for span in div.find_all("span", class_="family-name"):
            fnames.append(span.text.strip())
        authors_list = zip(gnames, fnames)
        for a in div.find_all("a"):
            if (a.get('href') and "articles" in a.get('href')) and (len(a.text) > 0):
                article = a.text.strip()
            elif a.get('href') and "pdfplus" in a.get('href'):
                art_url = "https://www.aeaweb.org"+a.get('href')
            elif a.get('href') and "data" in a.get('href'):
                data_url = a.get('href')
        count += 1
        countf = "%.2d" % count
        authorsf = ", ".join(fnames)
        articlef = article.replace("?", ".").replace(":", ".").replace("/", "-")
        filename = u"{count} - {authors} - {article} ({year}).pdf".format(count=countf, authors = authorsf, article = articlef, year=year)
        filepath = PATH+folder+"/"+filename
        f = open(filepath, "w")
        r = requests.get(art_url)
        if "application/pdf" in r.headers['content-type']:
            f.write(r.content)
        f.close()
        authors = " | ".join([t[1]+", "+t[0] for t in authors_list])
        idic = {"year": year, "issue": volume, "article": article, "url": art_url, "data_url": data_url, "authors": authors, "part": part}
        df = df.append(idic, ignore_index=True)

df.to_csv("jep.csv", index=False, encoding="utf-8")

