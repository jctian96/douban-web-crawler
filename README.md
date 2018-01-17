# douban-web-crawler
This is a web crawler program that scrapes movie information from www.douban.com, the most popular movie review website in China. You may choose the genre, production country, range of audience rating, etc. of the movies that you are interested in, and you may include other video forms including TV series, documentary, cartoon, etc. in your search as well. 

This result will include each film's title, user rating, number of rating people, directors, script writers, actors, genres, production countries and regions, languages, initial release date, other names, and IMdb link. 

The data obtained is well suited for many further analysis purposes. For example, some people might be interested in which films received the best ratings from the Chinese audience, and the result could be filtered by only including those movies reviewed by more than 100K people. Other analysis might include who are the best directors and actors, which countries' productions are consumed the most in China, how did the overall rating of Chinese domestically made movies evolve over the years... You decide. However, this program is just about obtaining the data rather than making analysis.

## Setup
### Installation on macOS
pip install requests  
pip install lxml

Install Homebrew by pasting all of the following at a terminal prompt:  
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

brew update  
brew install mongodb

Futher reference of installing MongoDB: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/

## Run
The program could be run either in terminal or an IDE. 

You are advised to change the request headers before running the program to avoid forbidden web access either by using the methods change_search_page_request_headers(new_request_headers) and change_movie_page_request_headers(new_request_headers) in terminal or by changing the global variables search_page_request_headers and movie_page_request_headers in IDE.

The database and collection are initialized as 'douban' and 'douban_movies_data'. You may change these in main().

## Output
The information is saved in MongoDB database. You may export the data to a .csv file by using mongoexport in terminal and open it with Excel. A [sample output](/sample_output.csv) is available.

## Futher Improvement
The program could be improved by applying multithreading or distributed crawling techniques to increase crawling speed and by autogenerating bid string in cookie or using multiple IP addresses to avoid blockage.

For doudou.
