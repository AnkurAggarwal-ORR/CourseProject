# import libraries
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import re 
import urllib
import time

# specify the url
quote_page = 'https://bmsce.ac.in/home/Computer-Science-and-Engineering-Faculty'

#create a webdriver object and set options for headless browsing
options = Options()
options.headless = True
print('here')
driver = webdriver.Chrome(executable_path='./chromedriver',options=options)
print('here1')

#uses webdriver object to execute javascript code and get dynamically loaded webcontent
def get_js_soup(url,driver):
    driver.get(url)
    res_html = driver.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(res_html,'html.parser') #beautiful soup object to be used for parsing html content
    return soup

#tidies extracted text 
def process_bio(bio):
    bio = bio.encode('ascii',errors='ignore').decode('utf-8')       #removes non-ascii characters
    bio = re.sub('\s+',' ',bio)       #repalces repeated whitespace characters with single space
    return bio


#extracts all Faculty Profile page urls from the Directory Listing Page
def scrape_dir_page(dir_url,driver):
    print ('-'*20,'Scraping directory page','-'*20)
    faculty_links = []
    #faculty_base_url = 'https://cs.illinois.edu'
    #execute js on webpage to load faculty listings on webpage and get ready to parse the loaded HTML 
    soup = get_js_soup(dir_url,driver)     
    for link_holder in soup.find_all('div',class_='col-md-9 order-2'): #get list of all <div> of class 'name'
        rel_link = link_holder.find('a')['href'] #get url
        #url returned is relative, so we need to add base url
        faculty_links.append(rel_link) 
    return faculty_links


def scrape_faculty_page(fac_url,driver):
    soup = get_js_soup(fac_url,driver)
    homepage_found = False
    bio_url = ''
    bio = ''
    profile_sec = soup.find('div',class_='container py-2')
    bio = process_bio(profile_sec.get_text(separator=' '))
    return bio_url,bio

def write_lst(lst,file_):
    with open(file_,'w') as f:
        for l in lst:
            f.write(l)
            f.write('\n')

faculty_links = scrape_dir_page(quote_page,driver)

bio_urls, bios = [],[]
tot_urls = len(faculty_links)
for i,link in enumerate(faculty_links):
    print ('-'*20,'Scraping faculty url {}/{}'.format(i+1,tot_urls),'-'*20)
    bio_url,bio = scrape_faculty_page(link,driver)
    bio_urls.append(link)
    bios.append(bio)

bio_urls_file = 'bio_urls.txt'
bios_file = 'bios.txt'
write_lst(bio_urls,bio_urls_file)
print ('-'*20,'Written to bios_urls.txt','-'*20)
write_lst(bios,bios_file)
print ('-'*20,'Written to bios.txt','-'*20)
