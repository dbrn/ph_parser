import argparse
from os import path, remove

import requests
from bs4 import BeautifulSoup as Soup

# let's initialize our argument parser
parser = argparse.ArgumentParser()
parser.add_argument("keywords", help='The keywords you want to look for between "" (eg. "teen blonde")')
parser.add_argument("pages", help="The range of pages you want to scrap. (eg. 1-20)")
args = parser.parse_args()

# let's transform the page-range into a tuple
if str(args.pages).isdigit() is False:
    page_range = tuple(map(int, str(args.pages).split("-")))
else:
    page_range = (1, int(args.pages))

# let's parse multiple keywords
keyword = ""
keyword_list = str(args.keywords).split()
for key in keyword_list:
    keyword += key + "+"

# remove the last "+" char
keyword = keyword[:-1]

# let's set everything up for request
ph_url = r"https://www.pornhub.com/video/search?"
params = {"search": keyword, "o": "mr", "page": 1}

# if a list of the same keywords exists, delete it
if path.exists(f"{keyword.replace('+', '_')}.list.csv"):
    remove(f"{keyword.replace('+', '_')}.list.csv")

# for each page in the range tuple...
for page_num in range(page_range[0], page_range[1] + 1):
    params["page"] = page_num
    page = requests.get(ph_url, params)
    print(f"scraping: {page.url}")

    # let bs parse the html we got back and store the video-blocks in a list
    page_soup = Soup(page.text, "html.parser")
    video_blocks = page_soup.find_all("div", {"class": "thumbnail-info-wrapper clearfix"})

    # create a csv file that will list all the videos we got back
    # from the scraping
    with open(f"{keyword.replace('+', '_')}.list.csv", "a") as file:
        if page_num == page_range[0]:

            # if this is the first iteration, set the csv labels
            file.write("url,description,uploader\n")
        for video_block in video_blocks:
            try:
                file.write(str("http://www.pornhub.com" + video_block.span.a["href"]).strip() + ",")
                file.write(str(video_block.span.a.text).replace(",", " ").title().strip() + ",")
                file.write(str(video_block.div.div.a.text).strip() + "\n")

            # in case of error skip this line by creating a new one
            except AttributeError:
                file.write("\n")
