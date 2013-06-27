from django import test
from django.conf import settings
from django.template import Template, Context
from django.contrib.auth.models import User
from myproject.apps.biz.models import Business, Website, WebsiteTypes


class BizViewsTestCase(test.TestCase):
    ''' Tests for the biz module
    '''
    
    def setUp(self):
        '''Create fake users
        '''
        self.user  = User.objects.create_user('bob', 'bob@bob.com', 'bob')
        self.user2 = Users.objects.create_user('jim', 'jim@jim.com', 'jim')
    
    def assert_renders(self, tmpl, context, value):
        ''' This checks if the rendered template == some value
        '''
        tmpl = Template(tmpl)
        self.assertEqual(tmpl.render(context), value)
    
    def test_business(self):
        ''' Get the index business page
        '''
        rs = self.client.get('/business/')
        self.assertEqual(rs.status_code, 302)
    
    def test_detail(self):
        ''' Get the details page for a business
        '''
        rs = self.client.get('/business/1/')
        self.assertEqual(rs.status_code, 200)
    
    def test_edit(self):
        ''' Get the edit form page for a business
        '''
        biz_1 = Business.objects.create(
                biz_name  = 'Test Biz',
                biz_info  = 'Test biz info',
                biz_email = 'testbiz@gmail.com',
                biz_phone = '512-797-6262',
                address_1 = '4401 Green Cliffs Rd.',
                address_2 = '',
                city      = 'Austin',
                state     = 'TX',
                zipcode   = '78746',
        )
        rs = self.client.get('/business/1/edit/')
        self.assertEqual(rs.status_code, 200)
    
    def test_roldex(self):
        ''' Get the roldex page for admins
        '''
        pass



