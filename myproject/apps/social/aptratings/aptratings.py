
import re, urllib2, cookielib
from BeautifulSoup import BeautifulSoup
from datetime import datetime


now = datetime.now()


class autoViv(dict):
    """IMPLEMENTATION OF PERL-LIKE AUTO-VIVIFICATION FEATURE
    """
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


def scrapeApartmentRatings(url):
    '''Scrape ApartmentRatings.com for all ratings, comments,
    replies for a given property (as defined by the url arg)
    Ultimately return a dictionary with structured data in it
    '''
    soup = getPage(url)
    
    # Return a dictionary containing information from the home page
    home_page = scrapeHomePage(soup)
    
    # make a list of all links leading to individual comment pages
    comment_html = soup.findAll("td", {"class" : "opinTitle"})
    root = "http://www.apartmentratings.com"
    comment_links = []
    
    # get comment-title and comment-page-url and save into tuple
    for td in comment_html:
        comment_links.append((td.a.string, root + td.a.attrs[0][1]))
    
    # for each link in the list of comment page urls
    # extract all comment and response data.
    final_product = []
    for link in comment_links:
        soup = getPage(link[1])
        try:
            final_product.append(getIndividualPage(soup))
        except Exception, err:
            print(err)
            print('Extraction failed on page: %s' % link[1])
            continue
    
    # return the data
    return home_page, final_product


def scrapeHomePage(soup):
    '''Return a dictionary containing info scraped from the home page
    '''
    # get an array with two items (main rating/percentage, and sub-ratings like parking)
    ratingsbox = soup.findAll("div", {"class" : "ratingsBox"})
    
    # collect the sub-ratings
    labels  = ['overall_parking', 'overall_maintenance', 'overall_construction', 
               'overall_noise', 'overall_grounds', 'overall_safety', 
               'overall_office_staff']
    
    ratings = ratingsbox[1].findAll("div", {"class" : "ratingNumSm"})
    values  = [x.contents[0] for x in ratings]
    output  = dict(zip(labels, values))
    
    # collect the main rating & percentage
    output['recommended_by'] = ratingsbox[0].span.string
    output['total_overall_rating'] = ratingsbox[0].find("div", {"class" : "rating"}).string
    output['time_stamp'] = datetime.now()
    
    return output


def getPage(url):
    '''DESCRIBE ME
    '''
    # TODO - rotate the user agent, OR name your agent and be transparent
    #        about your app
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.12) Gecko/20080201 Firefox/2.0.0.12',
        'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
        'Accept-Language': 'en-gb,en;q=0.5',
        'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Connection'     : 'keep-alive'
    }
    
    request  = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(request)
    cookies  = cookielib.CookieJar()
    cookies.extract_cookies(response, request)
    cookie_handler   = urllib2.HTTPCookieProcessor(cookies)
    redirect_handler = urllib2.HTTPRedirectHandler()
    opener = urllib2.build_opener(redirect_handler, cookie_handler)
    
    # print response.info()
    print response.geturl()
    return BeautifulSoup(response.read())


# TODO - improve your whitespace remover
def whitespaceBegone(s):
    '''
    Remove all forms of whitespace from string
    Note - this is not the most elegant solution
    '''
    # supposedly this is a much faster solution
    # than the regexp your currently using.
    # "".join(s.split())
    rx = re.compile('(\s)') # (\s+)
    try:
        return re.sub(rx, '', s)
    except TypeError:
        return None


def getIndividualPage(soup):
    '''
    extract the ratings, comments, replies from a 
    particular properties individual comment pages.
    '''
    foo = autoViv()
    sp  = soup.find("div", {"class" : "complexContent"})
    
    #-------------------------------------------------------------------------
    # GET INDIVIDUAL POST
    post_info = sp.img.parent.contents
    post_info = sp.h2.parent.contents
    
    title = sp.find("h2").string
    if title: foo['title'] = title.strip()
    else:     foo['title'] = "untitled"
    foo['name']  = whitespaceBegone(post_info[2])[5:]
    foo['date']  = whitespaceBegone(post_info[4])[11:]
    foo['years'] = whitespaceBegone(post_info[6])[-9:]
    #foo['responses'] = int(post_info[11].b.contents[0])
    
    # THIS IS UGLY, UGLY, UGLY - FIX THIS SHIT!
    sp_txt = sp.prettify().lower()
    start  = sp_txt.find("years at this apartment:")
    stop   = sp_txt.find('<div id="image_gallery">')
    almost_done  = sp_txt[start:stop]
    user_comment = BeautifulSoup(almost_done[almost_done.rfind("</div>"):])
    
    foo['user_comment'] = ''.join(user_comment.findAll(text=True)).strip()
    
    #-------------------------------------------------------------------------
    # GET INDIVIDUAL RATINGS
    review_table = sp.find("table", {"id" : "reviewRatings"})
    ratings = sp.find("table", {"id" : "reviewRatings"}).findAll('img')
    
    stars = []
    for img in ratings:
        numero = img.attrs[0][1].split('_')
        stars.append(int(numero[0][-1:]))
    
    foo['overall']      = stars[0]
    foo['parking']      = stars[1]
    foo['maintenance']  = stars[2]
    foo['construction'] = stars[3]
    foo['noise']        = stars[4]
    foo['grounds']      = stars[5]
    foo['safety']       = stars[6]
    foo['staff']        = stars[7]
    
    #-------------------------------------------------------------------------
    # GET INDIVIDUAL REPLIES (if any)
    
    # select the relevant part of the HTML
    tables    = sp.findAll("table")[4]
    table_txt = tables.findAll(text=True)
    replies   = []
    for x in table_txt:
        if len(x) > 1:
            replies.append(x.strip().replace('\t', ''))
    
    # extract the replies into the output variable
    n = 1
    for i, item in enumerate(replies):
        if item.find("From:") != -1:
            foo['replies']['reply_'+str(n)] = (replies[i+1], replies[i+3], replies[i+4])
            n += 1
    
    # return a dictionary with structured data in it
    return(foo)




def scrapeAptratings():
    '''Scrape apartmentratings and insert its values into DB
    '''
    connect_apartment_ratings()
    
    # get data from the two scraped sites and insert it into these two dicts
    home, data = aptratings.scrapeApartmentRatings(prop.aptratings)
    
    # insert info from scraped homepage into the DB
    aptratings_query = (prop.alias, home['recommended_by'], 
        home['total_overall_rating'], home['overall_parking'],
        home['overall_maintenance'], home['overall_construction'],
        home['overall_noise'], home['overall_grounds'],
        home['overall_safety'], home['overall_office_staff'], now)
    
    cur.execute("INSERT INTO aptratings (apartment_name, recommended_by, \
        total_overall_rating, overall_parking, overall_maintenance, \
        overall_construction, overall_noise, overall_grounds, \
        overall_safety, overall_office_staff, time_stamp) \
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", aptratings_query)
    
    # get id from aptratings table of what you just inserted
    scrape_id = cur.lastrowid
    
    # query db for latest id in aptratings table
    comments_query = []
    ratings_query  = []
    replies_query  = []
    
    for i, p in enumerate(data):
        apartment_name = prop.alias
        comment_id     = i + 1
        last_edited    = datetime.strptime(p['date'], "%m/%d/%Y")
        msg            = p['user_comment']
        
        # strip out the unecessary spacer at top of comments
        if msg.startswith('&nbsp;\n \n '):
            msg = msg.replace('&nbsp;\n \n ', '')
        
        # check user_comment to see if 'last updated:' is in it
        # if it is then adjust the last_edited field to be that value
        last_updated = msg.find('last updated: ')
        if last_updated != -1:
            n = last_updated + 14 # isolate the date only
            last_edited = msg[n:]
        
        # COMMENT TABLE
        comments = (scrape_id, comment_id, p['title'], p['name'], 
                    p['years'], msg.strip(), last_edited, now)
        comments_query.append(comments)
        
        # RATINGS TABLE
        ratings = (scrape_id, comment_id, p['overall'], 
                  p['parking'], p['maintenance'], p['construction'], 
                  p['noise'], p['grounds'], p['safety'], p['staff'], now)
        ratings_query.append(ratings)
        
        # REPLIES TABLE
        try:
            replies_list = data[i]['replies'].items()
            for n, item in enumerate(replies_list):
                rpl      = item[1]
                lst_edit = datetime.strptime(rpl[1], "%m/%d/%Y")
                reply    = (scrape_id, comment_id, n, rpl[0], rpl[2], lst_edit, now)
                replies_query.append(reply)
        except:
            pass
    
    # insert comment into comments table
    cur.executemany("INSERT INTO comments (id, comment_id, comment_title, \
        comment_username, comment_years_stayed, comment_message, last_edited, time_stamp) \
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)", comments_query)
    
    # insert ratings into ratings table
    cur.executemany("INSERT INTO ratings (id, comment_id, overall_rating, \
        parking, maintenance, construction, noise, grounds, safety, office_staff, time_stamp) \
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ratings_query)
    
    # insert replies into replies table
    cur.executemany("INSERT INTO replies (id, comment_id, reply_id, \
        reply_name, reply, last_edited, time_stamp) \
        VALUES (?, ?, ?, ?, ?, ?, ?)", replies_query)
    
    closeDB()


'''
#-----------------------------------------------------------------------------
# TODO
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# MISC
#-----------------------------------------------------------------------------
def tempfile(webfile):
    # TEMPORAY FUNCTION FOR TESTING PURPOSES
    filename = webfile
    with open(filename, 'r') as f:
        return BeautifulSoup(f.read())


#x = ''.join([e for e in sp.recursiveChildGenerator() if isinstance(e, unicode)])
page_text = sp.findAll(text=True)
'''
