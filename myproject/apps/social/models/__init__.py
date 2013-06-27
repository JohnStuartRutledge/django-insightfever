'''
This file imports the models.py files from the various other
social apps directories and instantiates them within this
/models folder. This has the effect of tricking python into
thinking that all the seperate models.py files are really
one single models.py file whose full path is:
    myproject.apps.social.models

Models are associated with the 'social' app by declaring
    app_label = 'social'
within the Meta class of each model


NOTE - if you have custom SQL or fixtures they have to be 
placed inside the models/ directory not in your app dir as 
indicated by the documentation.

For more on how this hack works, and for future reference
when this hack enevitably causes some kind of error, 
look at the info in these sites:
https://code.djangoproject.com/ticket/10985
http://groups.google.com/group/django-users/browse_thread/thread/3266a22af6c39437/90eee86aa3e6f732


'''
from myproject.apps.social.facebook.models import *
from myproject.apps.social.aptratings.models import *
from myproject.apps.social.yelp.models import *
#from myproject.apps.social.craigslist.models import *
#from myproject.apps.social.linkedin.models import *
#from myproject.apps.social.twitter.models import *

from myproject.apps.social.posts.models import *

'''
def get_file_path(instance, filename):
    return os.path.join('userprofiles', str(instance.created_by.id), filename)

'''