import sys

import scrapy

from scrapy.crawler import CrawlerProcess
import os
import fdb
from io import StringIO
import requests
import datetime
import logging
import pprint
import re
from time import sleep, time
############ tasks ###############
# todo:languages and translating
############ tasks ###############

_user_search_entity = 142
start_spider_message = """
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###############################################
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                START SPIDER
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###############################################
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
"""
invalid_page_message = """
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###############################################
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                INVALID PAGE
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###############################################
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
"""
writing_in_file_message = """
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###############################################
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                WRITING IN FILE
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###############################################
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
"""
spider_finished = """
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###############################################
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                SPIDER FINISHED
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
###############################################
$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
"""



def get_target_words():
    return ['boiling&point', 'vapor', 'reaction', 'chemical&formul', "melting&point", 'molar', 'weight', 'mass']


def check_url(url):
    return url


def get_from_wikipedia_manual():
    search_word = search_word = sys.argv[1]
    limits = 5
    response = requests.get(
        "https://en.wikipedia.org/w/api.php?action=opensearch&search={}&limit={}&namespace=0&format=json".format(
            search_word, limits))
    response2 = response.json()
    suggestions = response2[1]
    suggestion_urls = response2[3]
    if len(suggestions) == len(suggestion_urls):
        for i in range(len(suggestion_urls)):
            print(i+1, ":", suggestions[i])
            print(suggestion_urls[i])
    search_result_number = int(input("Enter the number: "))
    url = suggestion_urls[search_result_number - 1]
    print(url)
    input("you want to search for " + suggestions[search_result_number - 1])
    # words that we are looking for
    # here we can get it from database
    words = get_target_words()
    words += input("Enter any words split theme by '/' : ").split(sep="/")
    cb_kwargs = {"target_words": words, "main": suggestions[search_result_number - 1]}
    result = {
        "url": url,
        "cb_kwargs": cb_kwargs
    }
    return result

#html = """
#<body>
#<p> boiling point </p>
#</body>
#"""
#resp = Selector(text=html, type="html")
#Selector.xpath()
class Detector(scrapy.Spider):
    name = 'detector'

    def start_requests(self):
        mode = 1  # mode defines the way that we want to scrape the web
        if mode == 1:
            request_result = get_from_wikipedia_manual()
        url = request_result['url']
        cb_kwargs = request_result['cb_kwargs']

        yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=cb_kwargs)


    def parse(self, response, **kwargs):

        logging.critical(start_spider_message)
        print('request:', response.request)
        print('lang:', ResponseController.get_languages(response)['page'])
        words = response.cb_kwargs['target_words']
        # main_word = response.cb_kwargs['main']
        # keywords are words which the page marked them as keywords such as meta tags and h1,2,3,..,6
        keywords = ResponseController.get_key_words(response)
        title = keywords.get("title")
        print("title:", title)
        key_words = keywords.get("keywords")
        print("key words: ", key_words)
        headers = keywords.get('headers')
        # showing h1 to h6
        for key in headers:
            print(key, ":", headers[key])

        is_page_valid = ResponseController.is_page_valid_for_these_words(response, words)

        if is_page_valid:
            start_time = time()
            words_and_useful_tags_dict = ResponseController.get_useful_tag2(response, words, ignore_case=True)

            # words_and_useful_tags_dict = ResponseController.get_useful_tags(response, words)
            DatabaseConnection.save_useful_tags(words_and_useful_tags_dict, main_word=response.cb_kwargs['main'],
                                                refrence=response.request)  # we have to get ent id from the database
            for word in words_and_useful_tags_dict:
                print(word, words_and_useful_tags_dict[word]["word_point"])

            pretty_str = str(pprint.pformat(words_and_useful_tags_dict))
            logging.debug("\n" + pretty_str)
            print("--- %s seconds ---" % (time() - start_time))

        else:
            logging.critical(invalid_page_message)

        sections = {
            "images": 1,
            "pdf": 2
        }
        for section in sections:
            # download images:
            # get the tables:
            # get the pdf
            result = input("do you want to have {}? if yes Enter 1\n".format(section))
            if result == "1":
                if sections[section] == 1:
                    DatabaseConnection.download_save_img_to_db(response, response.request,
                                                               121)  # here we have to get methane id or get it inside the database
                elif sections[section] == 2:
                    pass  # download pdf

        logging.critical(spider_finished)
class DatabaseConnection:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_BASE_DIR = os.path.join(BASE_DIR,
                                 "SEDB.FDB")  # todo: we have to fix database directory using such this code os.path.join(BASE_DIR, "spamer", "spiders", "DB", "SEDB.FDB")


    @staticmethod
    def store_result(user_input_phrase_for_search, found_result, mimetype):
        con = fdb.connect(dsn=DatabaseConnection.DATA_BASE_DIR, user='SYSDBA',
                          password='masterkey')
        cur = con.cursor()
        is_result_string = isinstance(found_result, str)

        cur.execute('select PHRASEID from EXISTING_PHRASES where PHRASESTRING=?;', (user_input_phrase_for_search,))
        phrase_id = cur.fetchone()  # 0 false  1 true
        if (phrase_id != None):
            phrase_id = phrase_id[0]
        else:
            cur.execute('select gen_id(EXISTING_PHRASES_PHRASEID_GEN, 1) from rdb$database;')
            phrase_id = cur.fetchone()[0]
            cur.execute('insert into EXISTING_PHRASES (PHRASEID,PHRASESTRING,LANGID) values(?,?,?);',
                        (phrase_id, user_input_phrase_for_search, 0))

        cur.execute('select DROWID from ENTITIESRELATEDPHRASES where (PHRASEID=? and ENTID=?);',
                    (phrase_id, _user_search_entity))
        drowid = cur.fetchone()
        if (drowid != None):
            drowid = drowid[0]
        else:
            cur.execute('select gen_id(ENTSRELATEDPHRAS_ROWID_GEN, 1)from rdb$database;')
            drowid = cur.fetchone()[0]
            cur.execute('insert into ENTITIESRELATEDPHRASES (ENTID,PHRASEID,DROWID) values(?,?,?);',
                        (_user_search_entity, phrase_id, drowid))

        cur.execute('select gen_id(SEARCHS_SEARCHID_GEN, 1)from rdb$database;')
        searchid = cur.fetchone()[0]
        cur.execute('insert into SEARCHS (SEARCHID,ENT_PHRASEID,REFERENCE_ADDRESS,SEARCH_TIME) values(?,?,?,?);',
                    (searchid, drowid, 'example.wikipedia.ir', datetime.datetime.now()))
        # print(searchid)
        print(is_result_string)
        if (is_result_string):
            cur.execute("insert into RESULTS (SEARCHID,RESULT,MIMETYPE) values (?,?,?);",
                        (searchid, found_result.encode(encoding='utf8', errors='ignore'), mimetype))
        else:  # is image
            cur.execute("insert into RESULTS (SEARCHID,RESULT,MIMETYPE) values (?,?,?);",
                        (searchid, found_result.read(), mimetype))

        con.commit()
    @staticmethod
    def save_useful_tags(words_and_useful_tags_dict, main_word, refrence):  # refrence must be added
        final_body = ""
        for word in words_and_useful_tags_dict:
            title = "<h2>{}</h2>".format(word)
            tags_of_this_word = words_and_useful_tags_dict[word]['useful_tags']
            string_tags = title + "<br>".join(tags_of_this_word)
            final_body += string_tags
        final_body = final_body
        DatabaseConnection.store_result(main_word, final_body, 'text/html')



    @staticmethod
    def download_save_pdf_to_db(response):
        """
        all_hrefs_contains_http = ResponseController.get_hrefs_contains_http(response)
        pdf_urls = [url.strip() for url in all_hrefs_contains_http if url.strip().endswith(".pdf")]
        print(pdf_urls)
        for j in range(len(pdf_urls)):
            pdf_url = pdf_urls[j]
            print(pdf_url)
            if int(input("1")):
                resp = requests.get(pdf_url)
                input("2")
                pdf_file = open("D:\\programming\\scraP\\spammer\\spamer\\spamer\\spiders\\pdf\\{}.pdf".format(j), "wb")
                pdf_file.write(resp.content)
                pdf_file.close()
        :param response:
        :return:
        """
        pass

    @staticmethod
    def download_save_img_to_db(response, refrence, Ent_id):
        main_word = response.cb_kwargs['main']
        searched_words = response.cb_kwargs['target_words']

        path = DatabaseConnection.DATA_BASE_DIR
        con = fdb.connect(dsn=path, user='SYSDBA', password='masterkey')
        cur = con.cursor()
        _admin_for_manual_search_id = 0  # a phrase for manuall Searching
        img_directory_path = "D:\\programming\\scraP\\spammer\\spamer\\spamer\\spiders\\imgs\\"
        bad_imgs_lines = open(img_directory_path + "bad.txt", "r")
        bad_urls = bad_imgs_lines.readlines()
        bad_urls = [urls.strip() for urls in bad_urls]
        bad_imgs_lines.close()

        bad_imgs2 = open(img_directory_path + "bad.txt", "a")
        imgs = ResponseController.get_images(response)
        for i in range(len(imgs)):
            img = imgs[i]
            is_bad = True
            src = img['src']
            img_format = img['format']
            if src in bad_urls:
                print("it is in bad databases")
                print("///////////////////" + src + "///////////////")
            else:
                print(src)
                if bool(re.search(main_word, src, flags=re.RegexFlag.IGNORECASE)):
                    is_bad = False
                else:
                    for word in searched_words:
                        spitted_words = word.split(sep="&")
                        for w in spitted_words:
                            if bool(re.search(w, src, flags=re.RegexFlag.IGNORECASE)):
                                is_bad = False
                                break
                        break

                if is_bad:
                    is_bad = bool(input("is it bad so enter 1"))
                if is_bad:
                    bad_imgs2.write(src + "\n")
                else:
                    res = requests.get(img['src'])
                    img_file = open(img_directory_path + "{}_{}.{}".format(main_word, i, img_format), "wb")
                    img_file.write(res.content)
                    img_file.close()

                    img_file = open(img_directory_path + "{}_{}.{}".format(main_word, i, img_format), "rb")
                    content = img_file.read()
                    img_file.close()

                    cur.execute('select gen_id(ENTSRELATEDPHRAS_ROWID_GEN, 1)from rdb$database;')
                    drowid = cur.fetchone()[0]
                    cur.execute('insert into ENTITIESRELATEDPHRASES (ENTID,PHRASEID,DROWID) values(?,?,?);',
                                (Ent_id, _admin_for_manual_search_id, drowid))
                    # print(drowid)

                    cur.execute('select gen_id(SEARCHS_SEARCHID_GiEN, 1)from rdb$database;')
                    searchid = cur.fetchone()[0]
                    cur.execute(
                        'insert into SEARCHS (SEARCHID,ENT_PHRASEID,REFERENCE_ADDRESS,SEARCH_TIME) values(?,?,?,?);',
                        (searchid, drowid, refrence, datetime.datetime.now()))
                    # print(searchid)

                    cur.execute("insert into RESULTS (SEARCHID,RESULT,MIMETYPE) values (?,?,?);",
                                (searchid, StringIO(content), 'image/{}'.format(img_format)))

                    # delete after save it into the db

                    if os.path.exists("{}}.{}".format(i, img_format)):
                        os.remove("{}}.{}".format(i, img_format))
                    else:
                        print("The file does not exist")

        bad_imgs2.close()
        # print(cur.fetchall())
        # con.commit()
class ResponseController:

    @staticmethod
    def get_key_words(response):
        title = response.xpath('//title/text()').get().strip()
        keywords_tag = response.xpath('//meta[contains(name, "keywords")]')  # must be test
        keywords = keywords_tag.xpath('/@content').getall()
        h1 = ResponseController.clean_texts_in_list(response.xpath('//h1/text()').getall())
        h2 = ResponseController.clean_texts_in_list(response.xpath('//h2/text()').getall())
        h3 = ResponseController.clean_texts_in_list(response.xpath('//h3/text()').getall())
        h4 = ResponseController.clean_texts_in_list(response.xpath('//h4/text()').getall())
        h5 = ResponseController.clean_texts_in_list(response.xpath('//h5/text()').getall())
        h6 = ResponseController.clean_texts_in_list(response.xpath('//h6/text()').getall())
        result = {'title': title,
                  'keywords': keywords,
                  'headers': {
                      'h1': h1,
                      'h2': h2,
                      'h3': h3,
                      'h4': h4,
                      'h5': h5,
                      'h6': h6,
                  }
                  }
        return result

    @staticmethod
    def get_languages(response):
        langs = response.xpath('//*[@lang]')
        languages = {
            'page': None,
            'a': [],
            'other': []

        }
        for tag in langs:
            tagname = ResponseController.get_tag_name(tag)
            if tagname == 'html' or tagname == 'meta':
                languages['page'] = tag.xpath('./@lang').get()
            elif tagname == 'a':
                languages['a'].append(tag)
            else:
                languages['other'].append(tag)

        return languages

    @staticmethod
    def get_full_xpath(tag):
        pass

    @staticmethod
    def get_all_tables(response):
        all_table_xpath = response.xpath('//table')
        all_table = []
        for table in all_table_xpath:
            all_table.append(table.xpath('.').get())
        return all_table

    @staticmethod
    def are_we_inside_a_table(tag):
        flag = False
        table_words = ["td", "tr", "th"]
        table_words2 = ["td", "tr", "th", "table"]
        tag_name = ResponseController.get_tag_name(tag)
        if tag_name in table_words:
            return True
        if ResponseController.has_parent_tag(tag) and ResponseController.get_tag_name(
                ResponseController.get_the_parent_tag(tag)) in table_words2:
            return True
        if ResponseController.has_grand_parent(tag) and ResponseController.get_tag_name(
                ResponseController.get_the_grand_parent_tag(tag)) in table_words2:
            return True

        return False

    @staticmethod
    def get_images(response):
        images = response.xpath('//img')

        imgs = []
        for img in images:
            src = img.xpath('./@src').get()
            alt = img.xpath('./@alt').get()
            index = -1
            while src[index] != ".":
                index -= 1
            if src.startswith('//'):
                src = "https:" + src
            elif src.startswith("/"):
                src = "https://en.wikipedia.org/" + src
            img_format = src[index + 1:]
            imgs.append(
                {
                    "img_tag": img.get(),
                    "src": src,
                    "alt": alt,
                    "format": img_format
                }
            )
        return imgs

    @staticmethod
    def get_videos(response):
        videos = response.xpath('//video')  # has text and <source src="" type="video/mp4"
        if len(videos) == 0:
            return videos
        vids = []
        for video in videos:
            sourece_tags = video.xpath('./source')
            sources = []
            for tag in sourece_tags:
                sources.append(
                    {
                        "source": tag,
                        "src": tag.xpath('./@src'),
                        "type": tag.xpath('./@type')
                    }
                )

            vids.append(
                {
                    "tag": video,
                    "text": video.xpath('./text()'),
                    "sources": sources
                }
            )

    @staticmethod
    def get_audios(response):
        audios = response.xpath('//audio')  # has text and <source src="" type="audio/mpeg"
        if len(audios) == 0:
            return audios
        auds = []
        for audio in audios:
            sourece_tags = audio.xpath('./source')
            sources = []
            for tag in sourece_tags:
                sources.append(
                    {
                        "source": tag,
                        "src": tag.xpath('./@src'),
                        "type": tag.xpath('./@type')
                    }
                )

            auds.append(
                {
                    "tag": audio,
                    "text": audio.xpath('./text()'),
                    "sources": sources
                }
            )

    @staticmethod
    def go_up_till_table_row(tag):

        if ResponseController.are_we_inside_a_table(tag):
            tag_name = ResponseController.get_tag_name(tag)
            if tag_name != "table":
                if tag_name == "tr":
                    return tag
                upper_tag = ResponseController.get_the_parent_tag(tag)
                counter = 0
                while ResponseController.get_tag_name(upper_tag) != "tr" and counter < 6:
                    upper_tag = ResponseController.get_the_parent_tag(upper_tag)
                    counter += 1
                return upper_tag

    @staticmethod
    def get_tag_name(tag):  # needs debug!!
        return tag.xpath('name()').get()

    @staticmethod
    def get_all_tags(response):
        # all tags
        message = 'all tags'
        next_tags_message = 'next: all tags contains a text'
        all_tags = response.xpath('//*')
        # ResponseController.draw_tags(all_tags, message, next_tags_message)
        return all_tags

    @staticmethod
    def get_the_whole_page_content(response):  # needs debug!
        return response.xpath('string()').get()
        """
        whole_text = ""
        for text in response.xpath('//*/text()').getall():
            text2 = text.strip()
            whole_text += text2
        """

    @staticmethod
    def get_tags_contain_specific_word_without_jingoolak(response, word):
        return response.xpath('//*[contains(text(), "{}"'.format(word))

    @staticmethod
    def does_the_tag_contains_specific_word_without_jingoolak(tag, word):
        text = tag.xpath('./text()').get().strip()
        return bool(re.search(word, text))

    @staticmethod
    def get_the_tag_string(tag):
        return tag.xpath('string()').get().strip()

    @staticmethod
    def does_the_tag_contains_specific_word(tag, word):
        text = ResponseController.get_tag_text(tag)
        result = ResponseController.match_word_text_full_of_jingoolak(text, word)
        # if result:  # this is very useful because this needs debuging for example for words like T or he or He
        # pass
        # logging.debug("word: " + word + " / text: " + text + " / " + ResponseController.get_tag_name(
        #    tag) + " / is matched: " + str(result))
        return result

    @staticmethod
    def match_word_text_full_of_jingoolak(text, word):
        if text == "":
            return False
        if len(word) < 3:
            if len(ResponseController.two_chars_search(text, word, ignore_case=False,
                                                       find_first_match=True).get(word)) == 0:
                return False
            else:
                return True
        else:
            result = bool(re.search(word, text, flags=re.RegexFlag.IGNORECASE))
            if len(text) > 1000:
                return False
            return result

    @staticmethod
    def does_the_page_contains_specific_word_without_jingoolak(response, word):
        whole_text = ResponseController.get_the_whole_page_content(response)
        return bool(re.search(word, whole_text))

    @staticmethod
    def does_the_page_contains_specific_word(response, word):
        whole_text = ResponseController.get_the_whole_page_content(response)
        result = ResponseController.match_word_text_full_of_jingoolak(whole_text, word)

    @staticmethod
    def get_tag_text(tag):  # must be checked , do all tags contain text()?
        text = tag.xpath('./text()').get()
        if text is None:
            return ""
        else:
            return text.strip()

    @staticmethod
    def has_child(tag):
        if len(tag.xpath('./*')) > 0:
            return True
        else:
            return False

    @staticmethod
    def get_children_tags(tag):
        return tag.xpath('./*')

    @staticmethod
    def get_children_tag_number(tag):
        return len(ResponseController.get_children_tags(tag))

    @staticmethod
    def get_hrefs(response):
        # all hrefs of a tags
        message = 'all hrefs of a tags'
        next_tags_message = 'next:all hrefs do not starts from https or http'
        hrefs = response.xpath('//*/@href')
        # ResponseController.draw_tags(hrefs, message, next_tags_message)
        return hrefs

    @staticmethod
    def get_tag_which_href_contains_specific_word(response, word):  # need to check
        return response.xpath('//*[contains(@href, "{}")]'.format(word))

    @staticmethod
    def get_hrefs_contains_http(response):
        # all hrefs which start from https or http
        message = 'all hrefs start from https or http'
        next_tags_message = 'next: inside href'
        outside_href = response.xpath('//a[contains(@href,"http")]/@href').getall()
        # ResponseController.draw_tags(outside_href, message, next_tags_message)
        return outside_href

    @staticmethod
    def get_inside_hrefs(response):
        # inside href
        message = 'inside href'
        next_tags_message = 'next: tags contains another tags(has a child)'
        inside_href = response.xpath(
            '//a[starts-with(@href,"/") and not(contains(@href, "http")) and not(contains(@href, "www"))]/@href')
        # ResponseController.draw_tags(inside_href, message, next_tags_message)
        return inside_href

    @staticmethod
    def get_complete_url_for_inside_href(inside_href, response):
        base_url = re.search(r"(^http.+\..{2,3})", response.url).group()
        final_url = base_url + inside_href
        return final_url

    @staticmethod
    def has_href(tag):
        if len(tag.xpath('./@href')) > 0:
            return True
        else:
            return False

    @staticmethod
    def has_inside_href(tag):
        href = tag.xpath('@href').get()
        if href.startswith('/'):
            if not (bool(re.search(r'http', href, href)) or bool(re.search(r'www', href))):
                return True
        return False

    @staticmethod
    def has_parent_tag(tag):
        parents = tag.xpath('..')
        if len(parents) > 0:
            return True
        else:
            return False

    @staticmethod
    def get_the_parent_tag(tag):
        return tag.xpath('..')

    @staticmethod
    def has_grand_parent(tag):
        if len(tag.xpath('..').xpath("..")) > 0:
            return True
        else:
            return False

    @staticmethod
    def get_the_grand_parent_tag(tag):
        return tag.xpath('..').xpath("..")[0]

    @staticmethod
    def get_sibling_tags(tag):
        return tag.xpath('following-sibling::*')

    @staticmethod
    def has_sibling(tag):
        if len(tag.xpath('following-sibling::*')) > 0:
            return True
        else:
            return False

    @staticmethod
    def has_uncle(tag):
        if not ResponseController.has_parent_tag(tag):
            return False
        else:
            return ResponseController.has_sibling(ResponseController.get_the_parent_tag(tag))

    @staticmethod
    def get_uncle(tag):
        return ResponseController.get_the_parent_tag(tag).xpath('following-sibling::*')

    @staticmethod
    def get_sibling(tag):
        return tag.xpath('following-sibling::*')

    @staticmethod
    def draw_tags(tags, message, next_tags_message, unit_time=60, step_time_activated=False, step_time=7):
        for tag in tags.getall():
            logging.debug("\n" + tag + "\n{}\n{}".format("#" * 10, "$" * 10))
            if step_time_activated:
                sleep(step_time)
        logging.debug(message)
        logging.debug(next_tags_message)
        sleep(unit_time)
        input()

    @staticmethod
    def two_chars_search(target_string, word):
        a = target_string.strip("\n")
        for b in a:
            item = b.strip(" ")
            length = len(item)
            if 1 < length < 4:
                if bool(re.search(word, target_string, flags=re.RegexFlag.IGNORECASE)):
                    return True
        return False

    @staticmethod
    def better_search(target_string, words, ignore_case=False):  # words = {word1:[indexes], word2[indexes]}
        length = len(target_string)
        if ignore_case:
            target_string = target_string.lower()
            for word in words:
                words[word.lower()] = words[word]
                words.pop(word)
        for word in words:
            if len(word) > length:
                words.pop(word)
            if len(word) == length:
                if word == target_string:
                    words[word].append(0)
                    return words
        for i in range(length):
            for word in words:
                word_length = len(word)
                first_char = word[0]
                char_in_target_string = target_string[i]
                if char_in_target_string == first_char:
                    if target_string[i:i + word_length] == word:
                        if i != 0:
                            if bool(re.search(r"\W", target_string[i - 1])):
                                words[word].append(i)
                        elif bool(re.search(r"\W", target_string[i + word_length])):
                            words[word].append(i)
        return words

    @staticmethod
    def is_page_valid_for_these_words(response, words):  # this method is one of the initial methods which must be used
        index = 0  # critical index is count of target words

        whole_text = ResponseController.get_the_whole_page_content(response).lower()
        for word in words:
            Ws = word.split("&")
            words_count = 0
            for w in Ws:
                if len(w) < 3:
                    if ResponseController.two_chars_search(w, word):
                        words_count += len(re.findall(w, whole_text, re.RegexFlag.IGNORECASE))

                else:
                    if bool(re.search(w, whole_text, flags=re.RegexFlag.IGNORECASE)):
                        words_count += len(re.findall(w, whole_text, re.RegexFlag.IGNORECASE))
                        index += words_count
            if words_count > 0:
                print("word {} is matched. repeated time: {}".format(word, words_count))
        if index > len(words):
            print("final value of this page: {}".format(index))
            return True
        else:
            return False

    @staticmethod
    def get_useful_tags(response, words):
        all_tags = ResponseController.get_all_tags(response)
        result = dict()
        for word in words:
            multiple_words = word.split(sep="&")  # this part has some bugs
            word_result_dict = {
                'word_point': 0,
                'useful_tags': {}
            }
            for tag in all_tags:

                if len(multiple_words) == 1:
                    if bool(re.search(r"\d", word)):
                        tag_string = ResponseController.get_the_tag_string(tag)
                        if bool(re.search(word, tag_string)):
                            if len(tag_string) < 500:
                                word_result_dict['word_point'] += 1
                                word_result_dict['useful_tags'][
                                    word + "_" + str(time())] = ResponseController.get_the_tag_string(tag)
                    if ResponseController.does_the_tag_contains_specific_word(tag, word):
                        if ResponseController.are_we_inside_a_table(tag):
                            new_tag_till_tr = tag
                            while ResponseController.get_tag_name(new_tag_till_tr) != "tr":
                                new_tag_till_tr = ResponseController.get_the_parent_tag(new_tag_till_tr)
                            tag = new_tag_till_tr

                        word_result_dict['word_point'] += 1
                        word_result_dict['useful_tags'][word + "_" + str(time())] = ResponseController.get_tag_text(tag)

                elif len(multiple_words) > 1:
                    number_of_conditions = len(multiple_words)
                    condition_done = 0
                    for w in multiple_words:
                        if bool(re.search(r"\d", w)):
                            tag_string = ResponseController.get_the_tag_string(tag)
                            if bool(re.search(w, tag_string)):
                                if len(tag_string) < 500:
                                    word_result_dict['word_point'] += 1
                                    word_result_dict['useful_tags'][
                                        word + "_" + str(time())] = ResponseController.get_tag_text(tag)
                        if ResponseController.does_the_tag_contains_specific_word(tag, w):
                            condition_done += 1
                    if number_of_conditions == condition_done:  # means this tag contains our words simultaneously
                        if ResponseController.are_we_inside_a_table(tag):
                            new_tag_till_tr = tag
                            while ResponseController.get_tag_name(new_tag_till_tr) != "tr":
                                new_tag_till_tr = ResponseController.get_the_parent_tag(new_tag_till_tr)
                            tag = new_tag_till_tr
                        word_result_dict['word_point'] += 1
                        word_result_dict['useful_tags'][word + "_" + str(time())] = ResponseController.get_tag_text(tag)
            result[word] = word_result_dict
        return result

    @staticmethod
    def get_useful_tag2(response, words, ignore_case=False):
        words_dic = dict()
        for word in words:
            words_dic[word] = {"word_point": 0,
                               "useful_tags": []
                               }
        all_tags = ResponseController.get_all_tags(response)
        bad_tags_name = ["html", "head", "body", "meta", "img", "script", "tbody", "title", "link", "br",
                         "input", "style", "td", "th", "table"]
        needed_string_tags = ["p", "tr"]
        for tag_num in range(0, len(all_tags)):
            tag = all_tags[tag_num]
            name = ResponseController.get_tag_name(tag)
            if name in bad_tags_name:
                continue
            if name == "a" and ResponseController.get_tag_name(ResponseController.get_the_parent_tag(tag)) == "p":
                continue
            tag_string = ResponseController.get_the_tag_string(tag).strip()
            tag_text = ResponseController.get_tag_text(tag).strip()
            if name in needed_string_tags:
                final_text = tag_string
            else:
                final_text = tag_text

            if len(final_text) < 2:
                continue
            if ResponseController.get_tag_name(tag) in ['sub', 'sup'] and bool(re.search(r"\d", tag_text)):
                continue
            for word in words:
                if bool(re.search(r"\d", word)):
                    final_text = tag_string
                Ws = word.split(sep="&")
                number_of_conditions = len(Ws)
                condition_done = 0
                for w in Ws:
                    if ignore_case:
                        if len(w) < 3:
                            result = ResponseController.two_chars_search(final_text, w)
                            if result:
                                condition_done += 1
                        else:
                            if bool(re.search(w, final_text, flags=re.RegexFlag.IGNORECASE)):
                                condition_done += 1
                    else:
                        if len(w) < 3:
                            result = ResponseController.two_chars_search(final_text, w)
                            if result:
                                condition_done += 1
                        else:
                            if bool(re.search(w, final_text)):
                                condition_done += 1

                if condition_done >= number_of_conditions:
                    words_dic[word]["word_point"] += 1
                    words_dic[word]["useful_tags"].append(tag.xpath('.').get())
                    print(name, word, number_of_conditions, condition_done, final_text, sep="//", end="\n*******************************************************\n")
        all_tables = ResponseController.get_all_tables(response)

        words_dic["all_tables"] = {"useful_tags": all_tables, "word_point":len(all_tables)}
        return words_dic

    ############ NOT USEFUL METHODS ################

    @staticmethod
    def get_tag_has_child(response):
        # tags contains another tags(has a child)
        message = 'tags contains another tags(has a child)'
        next_tags_message = 'next: containing another tags which the child tag has a text'
        tags_which_has_a_tag = response.xpath('//*[*]')
        return tags_which_has_a_tag
        # ResponseController.draw_tags(tags_which_has_a_tag, message, next_tags_message)

    @staticmethod
    def get_tag_has_both_child_and_text(response):
        # tags which has both a text and a child
        message = 'tags which has both a text and a child'
        next_tags_message = 'next: tags which has a text and a child which the child also has a text'
        tags_which_which_has_both_child_and_text = response.xpath('//*[text() and *]')
        return tags_which_which_has_both_child_and_text
        # ResponseController.draw_tags(tags_which_which_has_both_child_and_text, message, next_tags_message)

    @staticmethod
    def get_tags_which_has_text_and_child_has_text(response):
        # tags which has a text and a child which the child also has a text
        message = 'tags which has a text and a child which the child also has a text'
        next_tags_message = 'next: tags which has a parent'
        tags_and_child_both_has_text = response.xpath('//*[text() and ./*/text()]')
        return tags_and_child_both_has_text
        # ResponseController.draw_tags(tags_and_child_both_has_text, message, next_tags_message)

    @staticmethod
    def get_tags_which_has_parent(response):
        # tags which has a parent
        message = 'tags which has a parent'
        next_tags_message = 'next: tags which has grand parent'
        tags_has_parent = response.xpath('//*[..]')
        # ResponseController.draw_tags(tags_has_parent, message, next_tags_message)
        return tags_has_parent

    @staticmethod
    def get_tags_which_has_text_and_parent(response):
        # tags which has text and parent
        message = 'tags which has text and parent'
        next_tags_message = 'next: tags which has an uncle'
        tags_which_has_parent_and_text = response.xpath('//*[.. and text()]')
        # ResponseController.draw_tags(tags_which_has_parent_and_text, message, next_tags_message)
        return tags_which_has_parent_and_text

    @staticmethod
    def get_tags_which_has_uncle(response):
        # tags which has an uncle
        message = 'tags which has an uncle'
        next_tags_message = 'next: finished  :D'
        tags_has_uncle = response.xpath('//*[.. and ../text()]')
        # ResponseController.draw_tags(tags_has_uncle,, message, next_tags_message)
        return tags_has_uncle

    @staticmethod
    def get_tags_contain_specific_word_and_children_does_not_contain_that(response,
                                                                          word):  # this method may be more useful than the upper
        return response.xpath('//*[contains(text(), "{}") and //* not contains(text(), "{}")]'.format(word, word))

    @staticmethod
    def get_tags_contains_text(response):
        # all tags contains a text
        message = 'all tags contains a text'
        next_tags_message = 'next:all a tags containing a href attr'
        all_texted_tags = response.xpath('//*[text()]')
        return all_texted_tags
        # ResponseController.draw_tags(all_texted_tags, message, next_tags_message)

    @staticmethod
    def clean_texts_in_list(list_of_str):
        new_list = []
        for string in list_of_str:
            new_string = string.strip()
            if new_string is not None:
                if len(new_string) != 0:
                    new_list.append(new_string)
        return new_list


process = CrawlerProcess()
process.crawl(Detector)
process.start()