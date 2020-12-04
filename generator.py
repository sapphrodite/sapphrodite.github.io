from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join



pages_source_dir = "sources/pages/"
article_source_dir = "sources/articles/"
archive_source_dir = "sources/archive/"
pages_dest_dir = "pages/"
article_dest_dir = "articles/"
archive_dest_dir = "archive/"

class article_data:
    date = []
    title = ""
    topics = []
    filename = ""
    description = ""
    source_location = ""

    def __lt__ (self, b):
        for i in range(3):
            if self.date[i] > b.date[i]: 
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


###########################################################pages_source_dirpages_source_dir############################
##      Header code - generates the contents of the <head> tag and site header       ## 
#######################################################################################

# Inserts HTML file metadata
def insert_file_header(title, description, generator):
    generator.append("<meta charset=\"UTF-8\">")
    generator.append("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
    if description != "":
        generator.append("<meta name=\"description\" content=\"" + description + "\">")
    generator.append("<link rel=\"stylesheet\" href=\"/theme.css\">")
    generator.append("<title>" + title + " - Caroline's Development Blog </title>")

# Inserts HTML for the site navigation bar
def insert_navmenu(generator):  
    generator.add_open_tag(tag("ul")) 
    generator.append("<li> <a class = \"modlink\" href=\"/" + archive_dest_dir + "\"> Archives </a>") 
    generator.append("<li> <a class = \"modlink\" href=\"https://github.com/sapphrodite\"> GitHub </a>")
    generator.append("<li> <a class = \"modlink\" rel=\"author\" href=/" + pages_dest_dir + "about.html> About </a>")  
    generator.add_close_tag(tag("ul"))
   

def insert_site_header(generator):
    generator.append("<a class = \"modlink\" href=\"/\"> Caroline's Development Blog </a>")  
    generator.append_inside_tag(tag("nav", "id = \"navmenu\""), insert_navmenu)

def generate_page_start(title, description, generator):
    generator.append("<!DOCTYPE html>")
    generator.append("<html lang=\"en\">")
    generator.append_inside_tag(tag("head"), insert_file_header, title, description)

    generator.add_open_tag(tag("body"))
    generator.append_inside_tag(tag("header", "id = \"site-header\""), insert_site_header)

######################################################################################
##      Archive code - generates groups of articles, sorted by date and topic       ##
######################################################################################

def append_article_preview(article, generator):
    text = open(article.source_location, "r").read()
    html_tree = BeautifulSoup(text, 'html.parser')
    generate_metadata_header(article, generator) 
    intro = html_tree.find("intro")
    process_children(intro, generator)
    generator.append("<a class = \"readmore modlink\" href = \"/" + article.filename + "\"> Read More... </a>")
 
def generate_topic_page(article_group, cat_name):
    generator = document_constructor()
    title = "Blog Archives: " + cat_name
    generate_page_start(title, "", generator)


    generator.add_open_tag(tag("main", "id = \"archive-main\""))

    generator.append("<h1 class = \"page-header\">" + title +  "</h1>")
    generator.add_open_tag(tag("nav", "class = \"toc\""))
    generator.append_inside_tag(tag("ol"), generate_article_lis, article_group)
    generator.add_close_tag(tag("nav"))
    
    for article in article_group:
        generator.append_inside_tag(tag("section", "id = \"" + article.title.replace(" ", "-") + "\""), append_article_preview, article)
    generator.add_close_tag(tag("main"))
         

    f = open(archive_dest_dir + cat_name.replace(" ", "_") + ".html", "w")
    f.write(generator.output)
    f.close()
 
def generate_archives_index(articles_by_quarter, articles_by_topic ): 
    generator = document_constructor()
    generate_page_start("Blog Archives", "", generator)
 
    generator.add_open_tag(tag("main", "id = \"index-main\""))
    generator.append("<h2> Blog Archives </h2>")


    process_archive_batch(articles_by_quarter, articles_by_topic, generate_section_div_archive, generator)

    f = open(archive_dest_dir + "index.html", "w")
    f.write(generator.output)
    f.close() 

def generate_batch_topicpages(article_batch): 
    for name in article_batch: 
        generate_topic_page(article_batch[name], name)  

def generate_archives(articles_by_quarter, articles_by_topic):
    generate_archives_index(articles_by_quarter, articles_by_topic)
    generate_batch_topicpages(articles_by_topic)
    generate_batch_topicpages(articles_by_quarter)
    
    


def generate_main_page(article_list, sidebar_string):  
    # love 2 hardcode, i'll fix this when i have at least 5 articles
    top5 = article_list[:2]

    generator = document_constructor()
    generate_page_start("Main Page", "", generator)

  
    generator.add_open_tag(tag("main", "id = \"article-main\""))  
    generator.append("""<p> </p>""")
    generator.append("<h1> Recent Articles </h1>") 
    for article in top5:
        generator.append_inside_tag(tag("section", "class = \"article-preview\""), append_article_preview, article)
    generator.add_close_tag(tag("main"))
         
    generator.add_open_tag(tag("nav", "id = \"article-nav\""))
    generator.append(sidebar_string)
    generator.add_close_tag(tag("nav")) 

    generator.add_close_tag(tag("body")) 

    generator.append("</html>")

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
def generate_section_div_archive(article_batch, sect_name, generator):
    id = sect_name.replace(" ", "-")
    generator.append("<span class = \"navlist-label\" id = \"" + id + "\">" + sect_name + "</span>")
    generator.append_inside_tag(tag("ul", "class = \"article-group-archive\""), 
            generate_articlegroups_li, article_batch, transform_article_group_archives) 

def generate_section_div_collapsible(article_batch, sect_name, generator):
    id = sect_name.replace(" ", "-")
    generator.append("<span class = \"navlist-label\" id = \"" + id + "\">" + sect_name + "</span>")
    generator.append_inside_tag(tag("ul", "aria-labelledby = \"" + id + "\" class = \"article-group-sidebar\""), 
            generate_articlegroups_li, article_batch, transform_article_group_collapsible) 

# Processes high-level display for archive groups - whether it generates the main page, archive index or sidebar depends on `function`
def process_archive_batch(articles_by_quarter, articles_by_topic, function, generator ):  
    generator.append_inside_tag(tag("div", "class = \"sidebar-sect\""), function, articles_by_quarter, "Articles by Quarter")
    generator.append_inside_tag(tag("div", "class = \"sidebar-sect\""), function, articles_by_topic, "Articles by Topic")



# Output an article group as a collapsible menu - pass this into the batch processor to generate a sidebar
def transform_article_group_collapsible(article_group, cat_name, generator):  
    def impl(generator):
        generator.append("<summary>" + cat_name + "</summary>")
        generator.append_inside_tag(tag("ul", "class = \"menu-content\""), generate_article_lis, article_group)

    generator.append_inside_tag(tag("details"), impl)

# Output an article group as a link to that topic page - pass this into the batch processor to generate the archives
def transform_article_group_archives(article_group, cat_name, generator):
    generator.append("<a href = /" + archive_dest_dir  + cat_name.replace(" ", "_") + ".html>" +  cat_name + "</a>")  


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
        string += "<a class = \"modlink\" href = /" + archive_dest_dir + topic + ".html>" + topic + "</a>"
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
    sptag = tag("span", "class = \"metadata-span\"")
    
    if article_data.title != "":
        generator.append("<h1 class = \"page-header\"> " + article_data.title + " </h1>")
    if article_data.date != "":
        generator.append_inside_tag(sptag, generate_pretty_date, article_data) 
    if article_data.topics != "":
        generator.append_inside_tag(sptag, generate_topic_links, article_data.topics) 


def generate_metadata_header(article_data, generator):
    generate_data_display( article_data, generator)
  
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

def process_attributes(tag):
    attr_string = ""
    for attr in tag.attrs:
        attr_string += attr + " = \"" 
        for attr_val in tag.attrs.get(attr):
            attr_string += attr_val
        attr_string += "\""
    return attr_string

def process_tag(html_tag, generator): 
    generator.append_inside_tag(tag(html_tag.name.strip(), process_attributes(html_tag)), process_children, html_tag)  

# Recursively parse the children of this tag and add them to the string 
def process_children(html_tag, generator): 
    for child in html_tag.children: 
        if isinstance(child, str):
            generator.append(child.strip())
            continue

        if child.name.strip() == "table":
            generator.append_inside_tag(tag("div", "class = \"table-overflow\""), process_tag, child)
        else:  
            process_tag(child, generator)

# Processes a section and turns it into a text string
def process_section(section, generator):  
    generator.append("<h2>"  + section["id"] + "</h2>")
    process_children(section, generator)  

def generate_article_body(html_tree, article_data, generator):
    section_list = [] 
    for section in html_tree.find_all("section"):
        section_list.append(section["id"]) 

    generator.add_open_tag(tag("article"))
    generator.append_inside_tag(tag("header", "class = \"metadata\""), generate_metadata_header, article_data)

    header_content = html_tree.find("intro")  
    generator.add_open_tag(tag("section"))

    generator.append("<h2> Introduction </h2>")
    process_children(header_content, generator) 
    generator.append_inside_tag(tag("nav", "class = \"toc\""), generate_toc, section_list) 
    generator.add_close_tag(tag("section"))

    for section in html_tree.find_all("section"):
       generator.append_inside_tag(tag("section", "id = \"" + section["id"].replace(" ", "_") + "\""), process_section, section)  
    generator.add_close_tag(tag("article"))

 

def generate_article(article, navbar_text, footer_text):

    generator = document_constructor() 
    text = open(article.source_location, "r").read()
    html_tree = BeautifulSoup(text, 'html.parser')
 
    generate_page_start(article.title, article.description, generator)  
    generator.append_inside_tag(tag("main", "id = \"article-main\""), generate_article_body, html_tree, article) 
    
    generator.add_open_tag(tag("nav", "id = \"article-nav\""))
    generator.append(navbar_text)
    generator.add_close_tag(tag("nav")) 

    generator.append(footer_text) 
    generator.add_close_tag(tag("body")) 

    generator.append("</html>")
 
    f = open(article.filename, "w")
    f.write(generator.output)
    f.close()
    
    return article

    


def generate_static_page(article):

    generator = document_constructor() 
    text = open(article.source_location, "r").read()
    html_tree = BeautifulSoup(text, 'html.parser')
 
    generate_page_start(article.title, article.description, generator) 
    generator.append_inside_tag(tag("main", "id = \"index-main\""), process_children, html_tree.find("section")) 
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
    for index, article in enumerate(article_list):
        if index + 1 < len(article_list):
            next_article = article_list[index + 1]
        else:
            next_article = None
        generate_article(article, sidebar_string, generate_footer_nav(next_article, prev_article))
        prev_article = article

def get_article_metadata(filename, in_directory, out_directory):
    text = open(in_directory + filename, "r").read()
    html_tree = BeautifulSoup(text, 'html.parser')
    article = article_data() 
    article.source_location = in_directory + filename.strip()
    date = html_tree.find("article-creation")
    topics = html_tree.find("article-topics")
    article.title = html_tree.find("article-title").string
    if date != None:
	    article.date = date.string.strip().split()  
    if topics != None:
	    article.topics = topics.string.strip().split()
    article.filename = out_directory + filename
    return article
 
article_files = [f for f in listdir(article_source_dir) if isfile(join(article_source_dir, f))] 

articles = []
for file in article_files:
    articles.append(get_article_metadata(file, article_source_dir, article_dest_dir))
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

 

process_archive_batch(articles_by_quarter, articles_by_topic, generate_section_div_collapsible, sidebar_generator)

generate_articles(articles, sidebar_generator.output)
generate_archives(articles_by_quarter, articles_by_topic)

generate_main_page(articles, sidebar_generator.output)
 
static_files = [f for f in listdir(pages_source_dir) if isfile(join(pages_source_dir, f))] 
 
for file in static_files:
    generate_static_page(get_article_metadata(file, pages_source_dir, pages_dest_dir)) 
