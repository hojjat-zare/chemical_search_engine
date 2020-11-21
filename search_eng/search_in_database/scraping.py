import scrapy
from scrapy import Selector
import re
from urllib.request import urlopen

class Search_methods:


    ################ this method find xpath of given selector ########################
    ############### return is some thing like: ./body[1]/div[2]/div[3]/div[1]/div[1] #####################
    @staticmethod
    def find_absolute_xpath(node_selector):
        paths = []
        absolute_xpath = ""
        # paths.append(node_selector.xpath("name()").get())
        condition = True
        parent = node_selector
        tag_name = ""
        while(tag_name!="body" and parent!=[]):
            tag_name = parent.xpath("name()").get()
            tag_number = int(float(parent.xpath("count(preceding-sibling::{})+1".format(tag_name)).get()))
            paths.append(tag_name+"["+str(tag_number)+"]")
            parent = parent.xpath("..")
        paths.reverse()
        for i in paths:
            absolute_xpath = absolute_xpath + "/" + i
        absolute_xpath = "." + absolute_xpath
        return(absolute_xpath)


    ############### this method is the main method for parsing the page and uses __search_string_in_node_with_given_xpath ##############################
    ############### this method just pass a [] to __search_string_in_node_with_given_xpath and in other words it is a wrapper funtion ##################
    @staticmethod
    def search_in_page(html_node_selector,string,xpath_address,default_max_lengh,**tag__resultMaxLengh):
        yield from Search_methods.__search_string_in_node_with_given_xpath(html_node_selector, string, xpath_address, default_max_lengh,[],**tag__resultMaxLengh)


    ################## this method search string in html_node_selector with given xpath ###################
    @staticmethod
    def __search_string_in_node_with_given_xpath(html_node_selector,string,xpath_address,default_max_lengh,searched_xpaths,**tag__resultMaxLengh):
        elements = html_node_selector.xpath(xpath_address)
        for selector in elements:
            element_string = selector.xpath("string()").get()
            ################## this if check that element contains searched word(string) #####################
            if(re.search(".*{}.*".format(string),element_string,flags = re.IGNORECASE)):
            ##################################################################################################
                ######################## remove excess spaces between words #################
                reformed_string = element_string.replace("\r","").replace("\n", "")
                reformed_string = re.sub(r"  +", " ", reformed_string)
                ############################################################################
                ############### __check_condition method decide if we need to recall the function ################
                ############### if __check_condition return True function recall itself           ##########################
                if(Search_methods.__check_condition(reformed_string,selector,string,default_max_lengh,**tag__resultMaxLengh)):
                ##############################################################################################################
                    yield from Search_methods.__search_string_in_node_with_given_xpath(selector, string,"child::*", default_max_lengh,searched_xpaths,**tag__resultMaxLengh)
                else:
                    reformed_resutl = Search_methods.__get_reformed_result(selector,reformed_string,searched_xpaths)
                    if(reformed_resutl!=None):
                        yield reformed_resutl


    ############### this method used in __search_string_in_node_with_given_xpath ########################
    ############## and checks if __search_string_in_node_with_given_xpath should recall itself or not ###################
    @staticmethod
    def __check_condition(element_string,element_selector,string,default_max_lengh,**tag__resultMaxLengh):
        element_children_number = int(float(element_selector.xpath("count(child::*)").get()))
        element_name = element_selector.xpath("name()").get()
        result_max_lengh = default_max_lengh
        if(element_name in tag__resultMaxLengh):
            result_max_lengh = tag__resultMaxLengh[element_name]
        if(element_name=="tr"):
            return(len(element_string)>result_max_lengh)
        elif(element_name=="table" or element_name=="tbody"):   ############ if element_selector is table so we shold search in its chilren ############
            return(True)
        elif(element_name=="div"):
            ################# this condition checks that div's own text() contain the searched word not in's children ############
            if(re.search(".*{}.*".format(string),"".join(element_selector.xpath("text()").getall()),flags = re.IGNORECASE)):
                return(False)
            else:
                return(True)
        else:
            return(len(element_string)>result_max_lengh and element_children_number>0)


    ############# this method is used in __search_string_in_node_with_given_xpath and reforme result and can exclusively for each tag use diffrent method ##########
    @staticmethod
    def __get_reformed_result(element_selector,element_string,searched_xpaths):
        element_xpath = Search_methods.find_absolute_xpath(element_selector)
        element_name= element_selector.xpath("name()").get()
        condition = True
        for path in searched_xpaths:
            if(path in element_xpath):
                condition = False
        if(condition):
            searched_xpaths.append(element_xpath)
            if(element_name=="tr"):
                if((int(float(element_selector.xpath("count(child::th)").get())) + int(float(element_selector.xpath("count(child::td)").get())))<5):
                    return(element_string)
                else:
                    return element_string ########################## this part has not done ##########################################
            if(element_name=="div"):
                return(element_string)############################# this part has not done ############################################
            else:
                return(element_string)



# class QuotesSpider(scrapy.Spider):
#     name = "quotes"
#     start_urls = [
#         'https://en.wikipedia.org/wiki/Hydrogen',
#         'https://www.rsc.org/periodic-table/element/1/hydrogen'
#     ]
#
#     def parse(self, response):
#         searched_xpaths = []
#         page = response.url.split("/")[-2]
#         filename = 'quotes-%s.html' % page
#         targets = search_in_table_rows(response,"boiling",searched_xpaths)
#         with open(filename, 'w') as f:
#             for t in targets:
#                 f.write(t)
#             for i in searched_xpaths:
#                 f.write(i)


string = "boiling"
html = urlopen('https://en.wikipedia.org/wiki/Hydrogen')
html_str = html.read()
res = Selector(text=html_str,type="html")
####################### this method begins from <body> tag and goes down to find proper result ##################
targets = Search_methods.search_in_page(res, string, '//body', 500,tr=100,p=500,div=500)
#################################################################################################################

print("\n\nresult from https://en.wikipedia.org/wiki/Hydrogen:")
for t in targets:
    print(t)
