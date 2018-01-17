# -*- coding: utf-8 -*-
import requests
from lxml import etree
import re
import json
from pymongo import MongoClient
import time


search_page_request_headers = {'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Connection':'keep-alive',
    'Cookie':'bid=XXwdbE1Nm0I; ll="108296"; __yadk_uid=oSlJYfbikmx32pJr21KjPDUwMN2MZxZV; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1516202313%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; __utmt=1; _vwo_uuid_v2=F7E27FE3FFDA62669244A0F8C8CD6B44|659295dc2056fdd72d7591396f99218c; __utma=30149280.352048505.1510450109.1515985047.1516202313.5; __utmb=30149280.0.10.1516202313; __utmc=30149280; __utmz=30149280.1515985047.4.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=223695111.1651390079.1514290790.1515985047.1516202313.3; __utmb=223695111.2.10.1516202313; __utmc=223695111; __utmz=223695111.1515985047.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _pk_id.100001.4cf6=75f2883da544c580.1514290790.3.1516202329.1515985047.; _pk_ses.100001.4cf6=*',
    'Host':'movie.douban.com',
    'Referer':'https://movie.douban.com/tag/',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

movie_page_request_headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Cookie':'bid=XXwdbE1Nm0I; ll="108296"; __yadk_uid=oSlJYfbikmx32pJr21KjPDUwMN2MZxZV; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1516202313%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; __utmt=1; _pk_id.100001.4cf6=75f2883da544c580.1514290790.3.1516202786.1515985047.; _pk_ses.100001.4cf6=*; __utma=30149280.352048505.1510450109.1515985047.1516202313.5; __utmb=30149280.0.10.1516202313; __utmc=30149280; __utmz=30149280.1515985047.4.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=223695111.1651390079.1514290790.1515985047.1516202313.3; __utmb=223695111.5.10.1516202313; __utmc=223695111; __utmz=223695111.1515985047.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _vwo_uuid_v2=F7E27FE3FFDA62669244A0F8C8CD6B44|659295dc2056fdd72d7591396f99218c',
    'Host':'movie.douban.com',
    'Referer':'https://movie.douban.com/tag/',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

rate_range = '0,10' # The range of movies to search for by audience ratings.

movie_tags = '电影' # The types of art works.


def change_search_page_request_headers(new_request_headers):
    global search_page_request_headers
    search_page_request_headers = new_request_headers


def change_movie_page_request_headers(new_request_headers):
    global movie_page_request_headers
    movie_page_request_headers = new_request_headers


def change_movie_range(new_rate_range):
    """You may change the range of movies to search for by audience ratings.

    On the scale of 0 to 10. Integers only. For example,'8,10' is a valid argument. """

    global rate_range
    rate_range = new_rate_range


def change_movie_tags(new_movie_tags):
    """You may change the types of art works to search for by providing tags from below.

    全部形式:电影,电视剧,综艺,动画,纪录片,短片
    全部类型:剧情,爱情,喜剧,科幻,动作,悬疑,犯罪,恐怖,青春,励志,战争,文艺,黑色,幽默,传记,情色,暴力,音乐,家庭
    全部地区:大陆,美国,香港,台湾,日本,韩国,英国,法国,德国,意大利,西班牙,印度,泰国,俄罗斯,伊朗,加拿大,澳大利亚,爱尔兰,瑞典,巴西,丹麦
    全部特色:经典,冷门佳片,魔幻,黑帮,女性

    For example,'香港,电影' is a valid argument."""

    global movie_tags
    movie_tags = new_movie_tags


def main():
    # Initialize the database and collection that store the obtained information.
    client = MongoClient('localhost',27017)
    database = client['douban']
    movies_data = database['douban_movies_data']

    movies_data.remove()   # Clear any previous data set that has the same name.
    counter = 0
    while True:
        start_offset = counter*20
        global rate_range
        global movie_tags

        # Send a GET request to the search page.
        search_page_url = "https://movie.douban.com/j/new_search_subjects?"
        query_string = {'sort':'T',
        'range':rate_range,
        'tags':movie_tags,
        'start': start_offset
        }
        response = requests.get(url=search_page_url, headers=search_page_request_headers, params=query_string)
        parsed_response = json.loads(response.text)

        if any(parsed_response['data']) == False:
            print("--------------- No more movies ---------------")
            break

        for movie in parsed_response['data']:
            # Send a GET request to the page of each movie.
            global movie_page_request_headers
            movie_page = requests.get(url=movie['url'], headers=movie_page_request_headers)
            structure = etree.HTML(movie_page.text)

            # Extract the title and audience rating of the movie from the search page.
            title = movie['title']
            rate = movie['rate']
            # Some art works do not have one or more of the following properties that need to be extracted from the movie page.
            rating_people = ''
            directors = ''
            script_writers = ''
            actors = ''
            genres = ''
            production_countries_regions = ''
            languages = ''
            initial_release_date = ''
            other_names=''
            imdb_link = ''
            # Extract the following additional information from the movie page using xpath and regular expressions
            try:
                rating_people = structure.xpath('//a[@class="rating_people"]/span/text()')[0]
            except:
                pass
            try:
                directors = structure.xpath('//div[@id="info"]/span/span/a[@rel="v:directedBy"]/text()')
            except:
                pass
            try:
                script_writers = structure.xpath('//div[@id="info"]/span[position()=2]/span[position()=2]/a/text()')
            except:
                pass
            try:
                actors = structure.xpath('//div[@id="info"]/span[@class="actor"]/span[@class="attrs"]/a/text()')
            except:
                pass
            try:
                genres = structure.xpath('//div[@id="info"]/span[@property="v:genre"]/text()')
            except:
                pass
            try:
                production_countries_regions = re.findall(pattern='制片国家/地区:</span>(.*?)<br/>', string=movie_page.text, flags=re.S)[0]
            except:
                pass
            try:
                languages = re.findall(pattern='语言:</span>(.*?)<br/>', string=movie_page.text, flags=re.S)[0]
            except:
                pass
            try:
                initial_release_date = structure.xpath('//div[@id="info"]/span[@property="v:initialReleaseDate"]/text()')
            except:
                pass
            try:
                other_names = re.findall(pattern='又名:</span>(.*?)<br/>', string=movie_page.text, flags=re.S)[0]
            except:
                pass
            try:
                imdb_link = re.findall(pattern='IMDb链接:</span> <a href="(.*?)"', string=movie_page.text, flags=re.S)[0]
            except:
                pass

            # Save the information in database
            movie_data = {'Title':title,
                'Rate':rate,
                'Rating people':rating_people,
                'Directors':directors,
                'Script writers':script_writers,
                'Actors':actors,
                'Genres':genres,
                'Production countries and regions':production_countries_regions,
                'Languages':languages,
                'Initial release date':initial_release_date,
                'Other names': other_names,
                'IMDb link':imdb_link
            }
            movies_data.insert_one(movie_data)

            # Print out some information in the console to keep track of the progress.
            print(title,rate,rating_people,directors,genres,production_countries_regions,initial_release_date)

            time.sleep(1)  # Sleep 1 second before making another request.

        counter+=1


if __name__=='__main__':
    main()
else:
    print('It is recommended to update search page and movie page request headers first to avoid web access failure.')
