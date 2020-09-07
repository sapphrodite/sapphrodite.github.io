from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join

class article_data:
    date = []
    title = ""
    topics = []
    filename = ""
    source_location = ""

    def __lt__ (self, b):
        for i in range(2):
            if self.date[i] < b.date[i]: 
                return True
        return False

class tag:
    name = ""
    attr = ""
    def __init__(self, name, attr = ""):
        self.name = name
        self.attr = attr

class document_constructor:
    output = ""
    __level__ = 0

    def increase_indent(self):
        self.__level__ += 1
    def decrease_indent(self):
        self.__level__ -= 1
    def append(self, string):
        self.output += generate_indentation(self.__level__) + string + "\n"
    def add_open_tag(self, tag):
        string = "<" + tag.name
        if tag.attr != "":
            string += " " + tag.attr
        string += ">" 
        self.append(string)
        self.__level__ += 1
    def add_close_tag(self, tag):
        self.__level__ -= 1
        self.append("</" + tag.name + ">")

    def append_inside_tag(self, tag, f, *args):
        self.add_open_tag(tag)
        f(*args, self)
        self.add_close_tag(tag)

def generate_indentation(depth):
    string = ""
    for _ in range(depth):
        string += "    "
    return string


#######################################################################################
##      Header code - generates the contents of the <head> tag and site header       ## 
#######################################################################################

# Inserts HTML file metadata
def insert_file_header(article_data, generator):
    generator.append("<meta charset=\"UTF-8\">")
    generator.append("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
    generator.append("<link rel=\"stylesheet\" href=\"/static/theme.css\">")
    generator.append("<title> title! </title>")

# Inserts HTML for the site navigation bar
def insert_navmenu(generator): 
    generator.append("<li> <a href=\"/\"> Main page </a> </li>")
    generator.append("<li> <a href=\"/archives/\"> Archives </a> </li>")
    generator.append("<li> <a href=\"https://github.com/sapphrodite\"> GitHub </a> </li>")
    generator.append("<li> <a rel=\"author\" href=\"/pages/about.html\"> About </a> </li>") 
   

def insert_site_header(generator):
    generator.append("<span> Caroline's Development Blog </span>")  
    generator.append_inside_tag(tag("ul", "id = \"navmenu\""), insert_navmenu)



######################################################################################
##      Archive code - generates groups of articles, sorted by date and topic       ##
######################################################################################

# Turn an article list into <li> entries
def generate_article_lis(article_group, generator):
    for article in article_group:
        generator.append("<li> <a href = \"" + article.filename + "\" > " + article.title + "</a> </li>")

# Output an article group as a collapsible menu
def transform_article_group_collapsible(article_group, cat_name, generator): 
    generator.append("<input type = \"checkbox\" id = \"" + cat_name.replace(" ", "_") + "\">")
    generator.append("<label class = \"label-toggle\" for = \"" + cat_name.replace(" ", "_") + "\">" + cat_name + " </label>") 
    generator.append_inside_tag(tag("ul", "class = \"menu-content\""), generate_article_lis, sorted(article_group))
 
# Take a batch of all articles, and transform it into html groups of lists
def transform_article_batch(article_batch, generator): 
    for name in article_batch: 
        generator.append_inside_tag(tag("li"), transform_article_group_collapsible, article_batch[name], name)     

def generate_sidebar(article_metadata_list): 
    articles_by_quarter = {}
    for article in articles:  
        quarter = "Q" + str(int(int(article.date[1]) / int(3)) + 1) + " " + article.date[0]
        if quarter not in articles_by_quarter:
            articles_by_quarter[quarter] = [] 
        articles_by_quarter[quarter].append(article)

    articles_by_topic = {}
    for article in articles:
        for topic in article.topics: 
            if topic not in articles_by_topic:
                articles_by_topic[topic] = []
        articles_by_topic[topic].append(article)

    sidebar_generator = document_constructor()
 
    sidebar_generator.append("<span class = \"navlist-label\" id = \"articles-by-date\"> Articles by Date </span>")  

    sidebar_generator.increase_indent()
    sidebar_generator.increase_indent()

    sidebar_generator.append_inside_tag(tag("ul", "aria-labelledby = \"articles-by-topic\""), transform_article_batch, articles_by_quarter) 
    sidebar_generator.append("<span class = \"navlist-label\" id = \"articles-by-topic\"> Articles by Topic </span>")  
    sidebar_generator.append_inside_tag(tag("ul", "aria-labelledby = \"articles-by-topic\""), transform_article_batch, articles_by_topic) 
    return sidebar_generator.output

######################################################################################
##      Article Header code - generates the header and preview of a blog post       ##
######################################################################################

def generate_section_links(section_list, generator):
    for section_id in section_list:
        generator.append("<li> <a href = \"#" + section_id.replace(" ", "_") + "\">" + section_id + "</a> </li>")

def generate_toc(section_list, generator): 
    generator.append("<h3> Table of Contents </h3>") 
    generator.append_inside_tag(tag("ol"), generate_section_links, section_list)   

def generate_topic_links(topics, generator):
    for topic in topics:
        generator.append("<li> <a href = \"archives/" + topic + ".html\"> " + topic + "</a> </li>")

def generate_article_header(html_tree, article_data, section_list, generator):
    header_content = html_tree.find("header")  
    generator.append("<h1 id = \"article-header\"> " + article_data.title + " </h1>")
    generator.append_inside_tag(tag("ul"), generate_topic_links, article_data.topics)
        
    process_children(header_content, generator)
    generator.append_inside_tag(tag("nav"), generate_toc, section_list) 
  

#######################################################################################
##        Article Code - processes through and formats the main article content      ##
#######################################################################################

# Recursively parse the children of this tag and add them to the string 
def process_children(html_tag, generator): 
    for child in html_tag.children: 
        if isinstance(child, str):
            generator.append(child.strip())
            continue
        generator.append_inside_tag(tag(child.name.strip()), process_children, child)  

# Processes a section and turns it into a text string
def process_section(section, generator):  
    generator.append("<h2>"  + section["id"] + "</h2>")
    process_children(section, generator)  

def generate_article_body(html_tree, article_data, generator):
    section_list = [] 
    for section in html_tree.find_all("section"):
        section_list.append(section["id"]) 


    generator.add_open_tag(tag("article"))
    generator.append_inside_tag(tag("header"), generate_article_header, html_tree, article_data,  section_list)
    for section in html_tree.find_all("section"):
       generator.append_inside_tag(tag("section", "id = \"" + section["id"].replace(" ", "_") + "\""), process_section, section)  
    generator.add_close_tag(tag("article"))

def generate_article(article, navbar_text, footer_text):

    generator = document_constructor() 
    text = open("/home/caroline/data/code/websites/articles/" + article,source_location, "r").read()
    html_tree = BeautifulSoup(text, 'html.parser')
 


    generator.append("<!DOCTYPE html>")
    generator.append("<html lang=\"en\">")
    generator.append_inside_tag(tag("head"), insert_file_header, article_data) 


    generator.add_open_tag(tag("body"))
    generator.append_inside_tag(tag("header", "id = \"site-header\""), insert_site_header)

    generator.add_open_tag(tag("nav", "id = \"article-nav\""))
    generator.append(navbar_text)
    generator.add_close_tag(tag("nav"))


    generator.append_inside_tag(tag("main"), generate_article_body, html_tree, article)

 
 
    generator.add_close_tag(tag("body"))
    generator.append("</html>")
 
    f = open("demofile3.html", "w")
    f.write(generator.output)
    f.close()
    
    return article


def get_article_metadata(filename):
    text = open("/home/caroline/data/code/websites/articles/" + filename, "r").read()
    html_tree = BeautifulSoup(text, 'html.parser')
    article = article_data() 
    article.date = html_tree.find("article-creation").string.split()
    article.title = html_tree.find("article-title").string
    article.topics = html_tree.find("article-topics").string.split()
    article.filename = "articles/" + article.title.replace(" ", "_") + ".html"
    return article



##########################
##      Main code       ##
##########################

def generate_footer(prev_article, next_article):
    prinf

dir = "/home/caroline/data/code/websites/article_sources/"
article_files = [f for f in listdir(dir) if isfile(join(dir, f))] 

articles = []
for file in article_files:
    articles.append(get_article_metadata(file))
articles.sort()

sidebar_string = generate_sidebar(articles)

for index, article in enumerate(articles):

    generate_article(article, sidebar_string, generate_footer())

print("yeehaw")





 