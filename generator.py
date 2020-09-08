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
    generator.append("<link rel=\"stylesheet\" href=\"../theme.css\">")
    generator.append("<title> title! </title>")

# Inserts HTML for the site navigation bar
def insert_navmenu(generator):  
    generator.add_open_tag(tag("ul"))
    generator.append("<li> <a class = \"modlink\" href=\"/\"> Main page </a>")
    generator.append("<li> <a class = \"modlink\" href=\"/archives/\"> Archives </a>") 
    generator.append("<li> <a class = \"modlink\" href=\"https://github.com/sapphrodite\"> GitHub </a>")
    generator.append("<li> <a class = \"modlink\" rel=\"author\" href=\"/pages/about.html\"> About </a>")  
    generator.add_close_tag(tag("ul"))
   

def insert_site_header(generator):
    generator.append("<span> Caroline's Development Blog </span>")  
    generator.append_inside_tag(tag("nav", "id = \"navmenu\""), insert_navmenu)

def generate_page_start(generator):
    generator.append("<!DOCTYPE html>")
    generator.append("<html lang=\"en\">")
    generator.append_inside_tag(tag("head"), insert_file_header, article_data) 

    generator.add_open_tag(tag("body"))
    generator.append_inside_tag(tag("header", "id = \"site-header\""), insert_site_header)

######################################################################################
##      Archive code - generates groups of articles, sorted by date and topic       ##
######################################################################################

def append_article_preview(article, generator):
    text = open(article.filename, "r").read()
    html_tree = BeautifulSoup(text, 'html.parser')
    header = html_tree.find("article").find("header")
    process_children(header, generator)
    generator.append("<a class = \"readmore\" href = \"/" + article.filename + "\"> Read More </a>")
 
def generate_topic_page(article_group, cat_name):
    generator = document_constructor()
    generate_page_start(generator)


    generator.add_open_tag(tag("main", "id = \"archive-main\""))

    generator.append("<h1> Blog Archives: " + cat_name + "</h1>")
    generator.add_open_tag(tag("nav", "class = \"toc\""))
    generator.append_inside_tag(tag("ol"), generate_article_lis, article_group)
    generator.add_close_tag(tag("nav"))
    
    for article in article_group:
        generator.append_inside_tag(tag("section"), append_article_preview, article)
    generator.add_close_tag(tag("main"))
         

    f = open("archives/" + cat_name.replace(" ", "_") + ".html", "w")
    f.write(generator.output)
    f.close()
 
def generate_archives_index(articles_by_quarter, articles_by_topic ): 
    generator = document_constructor()
    generate_page_start(generator)
 
    generator.add_open_tag(tag("main", "id = \"index-main\""))
    generator.append("<h2> Blog Archives </h2>")
    process_archive_batch(articles_by_quarter, articles_by_topic, transform_article_group_archives, generator)

    f = open("archives/index.html", "w")
    f.write(generator.output)
    f.close() 

def generate_batch_topicpages(article_batch): 
    for name in article_batch: 
        generate_topic_page(article_batch[name], name)  

def generate_archives(articles_by_quarter, articles_by_topic):
    generate_archives_index(articles_by_quarter, articles_by_topic)
    generate_batch_topicpages(articles_by_topic)
    generate_batch_topicpages(articles_by_quarter)
    
    


def generate_main_page(article_list):  
    # love 2 hardcode, i'll fix this when i have at least 5 articles
    top5 = article_list[:1]

    generator = document_constructor()
    generate_page_start(generator)

  
    generator.add_open_tag(tag("main", "id = \"archive-main\""))  
    generator.append("""<h4> Hi! This website is currently under construction - this page isn't complete, and the about page is missing, but
    who cares because i'm not sharing with too many people until it's finished - enjoy the one article I have :)</h4>""")
    generator.append("<h1> Recent Articles </h1>") 
    for article in top5:
        generator.append_inside_tag(tag("section"), append_article_preview, article)
    generator.add_close_tag(tag("main"))
         

    f = open("index.html", "w")
    f.write(generator.output)
    f.close()
    



# Take an article list and turn each article into a <li> entry
def generate_article_lis(article_group, generator):
    for article in article_group:
        generator.append("<li> <a href = \"/" + article.filename + "\" > " + article.title + "</a> </li>")

  


# Take a batch of all articles, and transform it an into html list where entries are article groups, formatted according to function
def generate_articlegroups_li(article_batch, function, generator): 
    for name in article_batch: 
        generator.append_inside_tag(tag("li"), function, article_batch[name], name)     

# Combines sect_name and a list-processed article batch into a div, for formatting
def generate_section_div(article_batch, sect_name, function, generate_section_div):
    id = sect_name.replace(" ", "-")
    generate_section_div.append("<span class = \"navlist-label\" id = \"" + id + "\">" + sect_name + "</span>")
    generate_section_div.append_inside_tag(tag("ul", "aria-labelledby = \"" + id + "\""), 
            generate_articlegroups_li, article_batch, function) 

# Processes high-level display for archive groups - whether it generates the main page, archive index or sidebar depends on `function`
def process_archive_batch(articles_by_quarter, articles_by_topic, function, generator ):  
    generator.append_inside_tag(tag("div", "class = \"sidebar-sect\""), generate_section_div, articles_by_quarter, "Articles by Quarter", function)
    generator.append_inside_tag(tag("div", "class = \"sidebar-sect\""), generate_section_div, articles_by_topic, "Articles by Topic", function)



# Output an article group as a collapsible menu - pass this into the batch processor to generate a sidebar
def transform_article_group_collapsible(article_group, cat_name, generator): 
    generator.append("<input type = \"checkbox\" id = \"" + cat_name.replace(" ", "_") + "\">")
    generator.append("<label class = \"label-toggle\" for = \"" + cat_name.replace(" ", "_") + "\">" + cat_name + " </label>") 
    generator.append_inside_tag(tag("ul", "class = \"menu-content\""), generate_article_lis, article_group) 

# Output an article group as a link to that topic page - pass this into the batch processor to generate the archives
def transform_article_group_archives(article_group, cat_name, generator):
    generator.append("<a href = \"/archives/" + cat_name.replace(" ", "_") + ".html\">" +  cat_name + "</a>")  


##################################################################################
##      Header/Footer code - adds the header, footer and article metadata       ##
##################################################################################

def generate_section_links(section_list, generator):
    for section_id in section_list:
        generator.append("<li> <a class = \"modlink\" href = \"#" + section_id.replace(" ", "_") + "\">" + section_id + "</a> </li>")

def generate_toc(section_list, generator):  
    generator.append_inside_tag(tag("ol"), generate_section_links, section_list)   

def generate_topic_links(topics, generator):
    string = "Topics: " 
    for index, topic in enumerate(topics):
        string += "<a class = \"modlink\" href = \"/archives/" + topic + ".html\"> " + topic + "</a>"
        if index + 1 != len(topics):
            string += ", "
    generator.append(string)

def generate_pretty_date(article_data, generator):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    suffix = ""
    day = article_data.date[2]
    if day == 1 or day == 21 or day == 31:
        suffix = "st"
    elif day == 3 or day == 23:
        suffix = "rd"
    elif day == 2 or day == 22:
        suffix = "st"  
    else:
        suffix = "th"
    generator.append("Published on the " + str(day) + suffix + " of " + months[int(article_data.date[1]) - 1] + ", " + str(article_data.date[0]) + "\n")

def generate_data_display(article_data, generator):
    generator.append("<h1 id = \"article-header\"> " + article_data.title + " </h1>")
    generator.append_inside_tag(tag("span"), generate_pretty_date, article_data)
    generator.append_inside_tag(tag("span"), generate_topic_links, article_data.topics)


def generate_article_header(html_tree, article_data, generator):
    header_content = html_tree.find("intro")  
    generate_data_display( article_data, generator)
    process_children(header_content, generator)
  
def generate_footer_nav(prev_article, next_article):
    footer_generator = document_constructor()
    footer_generator.add_open_tag(tag("nav", "id = \"footer-nav\""))
    footer_generator.increase_indent()
    footer_generator.increase_indent()
    footer_generator.add_open_tag(tag("ul"))

    prev_string = "← Prev"
    if prev_article != None:
        prev_string = "<a class = \"modlink\"  href = \"/" + prev_article.filename + "\" >" + prev_string + "</a>"
    
    next_string = "Next →"
    if next_article != None:
        next_string = "<a class = \"modlink\" href = \"/" + next_article.filename + "\" >" + next_string + "</a>" 

    footer_generator.append("<li id=\"prev-button\">" + prev_string)
    footer_generator.append("<li id=\"top-button\"> <a class = \"modlink\"  href = \"#site-header\"> ↑ Top ↑ </a>")
    footer_generator.append("<li id=\"next-button\">" + next_string)

    footer_generator.add_close_tag(tag("ul"))
    footer_generator.add_close_tag(tag("nav"))
    return footer_generator.output

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
    generator.append_inside_tag(tag("header"), generate_article_header, html_tree, article_data)
    generator.append_inside_tag(tag("nav", "class = \"toc\""), generate_toc, section_list) 

    for section in html_tree.find_all("section"):
       generator.append_inside_tag(tag("section", "id = \"" + section["id"].replace(" ", "_") + "\""), process_section, section)  
    generator.add_close_tag(tag("article"))


def generate_article_wrapper(html_tree, navbar_text, generator):
    generator.append_inside_tag(tag("main", "id = \"article-main\""), generate_article_body, html_tree, article)
    generator.add_open_tag(tag("nav", "id = \"article-nav\""))
    generator.append(navbar_text)
    generator.add_close_tag(tag("nav")) 
 

def generate_article(article, navbar_text, footer_text):

    generator = document_constructor() 
    text = open(article.source_location, "r").read()
    html_tree = BeautifulSoup(text, 'html.parser')
 
    generate_page_start(generator) 
    generator.append_inside_tag(tag("div", "id = \"article-wrapper\""), generate_article_wrapper, html_tree, navbar_text)
    generator.append(footer_text)
    generator.add_close_tag(tag("body")) 

    generator.append("</html>")
 
    f = open(article.filename, "w")
    f.write(generator.output)
    f.close()
    
    return article

    







##########################
##      Main code       ##
##########################


def generate_articles(article_list, sidebar_string):
    prev_article = None 
    next_article = None
    for index, article in enumerate(articles):
        if index + 1 < len(articles):
            next_article = articles[index + 1]
        else:
            next_article = None
        generate_article(article, sidebar_string, generate_footer_nav(prev_article, next_article))
        prev_article = article

def get_article_metadata(filename):
    text = open("article_sources/" + filename, "r").read()
    html_tree = BeautifulSoup(text, 'html.parser')
    article = article_data() 
    article.source_location = "article_sources/" + filename.strip()
    article.date = html_tree.find("article-creation").string.strip().split()
    article.title = html_tree.find("article-title").string.strip()
    article.topics = html_tree.find("article-topics").string.strip().split()
    article.filename = "articles/" + filename
    return article
 
dir = "article_sources/"
article_files = [f for f in listdir(dir) if isfile(join(dir, f))] 

articles = []
for file in article_files:
    articles.append(get_article_metadata(file))
articles.sort()


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
process_archive_batch(articles_by_quarter, articles_by_topic, transform_article_group_collapsible, sidebar_generator)

generate_articles(articles, sidebar_generator.output)
generate_archives(articles_by_quarter, articles_by_topic)

generate_main_page(articles)