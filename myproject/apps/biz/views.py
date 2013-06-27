from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, render, redirect
from django.template import RequestContext
from django.forms.models import inlineformset_factory

import logging

from myproject.apps.biz.models import Business, Website, WebsiteTypes
from myproject.apps.biz.forms import BusinessForm, WebsiteForm

log = logging.getLogger(__name__)


# TODO
# Convert everything in this app to Class Based Views 
# Consider using the DetailView for displyaing the properties obj


#@permission_required('clientprops.view_details')
@login_required(login_url=settings.LOGIN_URL)
def biz_details(request, biz_id, template='biz/biz_detail.html'):
    ''' Individual businesses profile page. From here you can easily 
    view information or access reports relevant to a particular business.
    '''
    biz = get_object_or_404(Business, pk=biz_id)
    context = {
        'page_name': 'biz_details',
        'biz': biz,
        }
    return render(request, template, context)


@login_required(login_url=settings.LOGIN_URL)
def biz_new(request, template_name='biz/biz_create.html'):
    ''' Page for clients to create a new business.
    '''
    # check to see if a business is already associated with this user
    # and if it is then redirect to that businesses page
    biz_list = Business.objects.filter(members__exact=request.user.id)
    if biz_list:
        return redirect('biz_details', biz_id=biz_list[0].id)
    
    if request.method == 'POST':
        form = BusinessForm(request.POST)
        
        if form.is_valid():
            biz = form.save()
            biz.members.add(request.user.id)
            biz.save()
            messages.success(request, _('Your business has been created.'),
                                                        fail_silently=True)
            return redirect('biz_details', biz_id=biz.id)
    else:
        # render the business form
        form = BusinessForm()
    
    context = {
        'user_id': request.user.id,
        'form':    form,
        }
    return render(request, template_name, context)


#@permission_required('clientprops.view_details')
@login_required(login_url=settings.LOGIN_URL)
def biz_edit(request, biz_id, template_name='biz/biz_edit.html'):
    ''' Page that renders the current businesses Information form. 
    Clients can set their relevant info via the forms provided.
    '''
    biz  = get_object_or_404(Business, pk=biz_id)
    form = BusinessForm(request.POST or None, instance=biz)
    
    if form.is_valid():
        biz = form.save(commit=False)
        biz.members.add(request.user.id)
        biz.save()
        messages.success(request, _('Your business was edited successfully.'),
                                                          fail_silently=True)
        return redirect('biz_details', biz_id=biz_id)
    
    context = {
        'page_name' : 'biz_edit',
        'user_id'   : request.user.id, 
        'biz_id'    : biz_id,
        'form'      : form,
        'biz'       : biz,
        }
    return render(request, template_name, context)


@login_required(login_url=settings.LOGIN_URL)
def biz_websites(request, biz_id, template_name='biz/biz_websites.html'):
    ''' Return a list of websites relevant to the current Business.
    Examples include a homepg, blog, news outlet, and competitor sites.
    '''
    biz        = Business.objects.get(pk=biz_id)
    sites      = Website.objects.filter(business=biz_id)
    site_types = WebsiteTypes.objects.all()
    
    context = {
        'page_name' : 'biz_websites',
        'biz_id'    : biz_id,
        'biz'       : biz,
        }
    if not sites:
        context['NO_SITES'] = 'nope'
        forms_to_add = site_types.count()
    else:
        site_count   = sites.count()
        forms_to_add = site_types.count() - sites.count()
    
    WebsiteFormSet = inlineformset_factory(Business, Website, 
                     extra=forms_to_add, exclude=['tags'])
    
    if request.method == 'POST':
        formset = WebsiteFormSet(request.POST, instance=biz)
        if formset.is_valid():
            formset.save()
            messages.success(request, 
               _('Your Websites were successfully saved.'), fail_silently=True)
    else:
        formset = WebsiteFormSet(instance=biz)
    
    context['formset'] = formset
    return render(request, template_name, context)


@login_required(login_url=settings.LOGIN_URL)
def biz_route(request):
    """ Redirect to the proper page when django-social-auth finishes
    authenticating the user via Open-auth2. 
    This function exists because inserting a dynamic biz_id into 
    django-social-auth's SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL variable 
    via the settings.py file will not work.
    """
    # TODO
    # check the 3 referer URLS to see which type it is. Possibilities are:
    #   1. they just finished authenticating via oauth2
    #   2. they disconnected an account by hitting the disconnect button
    #   3. an error occured and you need to pass it to the Message() function
    try:
        referer_url = request.META['HTTP_REFERER']
    except KeyError:
        log.info('KeyError: request.META["REFERER"] no referer exists')
        referer_url = '/dashboard/'
    return redirect(referer_url)


@login_required(login_url=settings.LOGIN_URL)
def biz_done(request, biz_id, template_name='biz/social_auth/done.html'):
    """ Login complete view, for after successfully logging in using oauth2
    """
    biz = get_object_or_404(Business, pk=biz_id)
    context = {
        'biz'       : biz,
        'last_login': request.session.get('social_auth_last_login_backend'),
    }
    return render(request, template_name, context)



def biz_roldex(request):
    ''' Redirect to the dashboard
    '''
    return redirect('/dashboard/')


