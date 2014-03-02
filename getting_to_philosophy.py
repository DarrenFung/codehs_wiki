import re
import sys
from urllib2 import urlopen
from bs4 import BeautifulSoup
from contextlib import closing

MAX_HOPS = 100

class WikipediaArticle(object):
  __WIKIPEDIA_PREFIX = "http://en.wikipedia.org"

  def __init__(self, start_link):
    super(WikipediaArticle, self).__init__()
    self.start_link = start_link

  def is_valid_article(self):
    if re.search("^http://en.wikipedia.org/wiki/[^:]+$", self.start_link):
      return True
    else:
      return False

  def print_path_to(self, max_hops, navigate_url):
    # Make sure we don't get in a loop
    visited        = {}
    number_of_hops = 0

    # /wiki/SomeArticle => http://en.wikipedia.org/wiki/SomeArticle
    def construct_link_from_shortform(short_form):
      return self.__WIKIPEDIA_PREFIX + short_form

    # Loops from the start node until it finds a valid Wikipedia article
    def get_next_wikipedia_link(start, visited):
      current_p_tag = start
      while True:
        if current_p_tag is None:
          print "Could not find path to Philosophy"
          return None
        current_p_tag  = current_p_tag.find_next('p')
        # Wikipedia article links are in the form /wiki/ArticleName
        # where there's no namespace (i.e. no colon in the article name)
        next_link_item = current_p_tag.find('a', href=re.compile("^/wiki/[^:]+$"))
        if next_link_item != None:
          next_link = construct_link_from_shortform(next_link_item['href'])
          article   = WikipediaArticle(next_link)
          if not next_link in visited.keys() and article.is_valid_article():
            return next_link

    next_link           = self.start_link
    destination_article = construct_link_from_shortform("/wiki/" + navigate_url)
    for x in range(max_hops):
      print next_link
      if next_link == destination_article:
        break
      with closing(urlopen(next_link)) as f:
        soup = BeautifulSoup(f)

        start_tag = soup.find('div', id='mw-content-text')
        next_link = get_next_wikipedia_link(start_tag, visited)

        if next_link:
          visited[next_link] = True
          number_of_hops     += 1
        else:
          print "Could not reach Philosophy from the starting node"
          return None
    print str(number_of_hops) + " hops"
    return None

if len(sys.argv) < 2:
  print "You need to supply the starting URL"
else:
  t = WikipediaArticle(sys.argv[1])
  if t.is_valid_article():
    print "Getting path to Philosophy from " + sys.argv[1]
    t.print_path_to(MAX_HOPS, "Philosophy")
  else:
    print "Invalid Wikipedia article!"
