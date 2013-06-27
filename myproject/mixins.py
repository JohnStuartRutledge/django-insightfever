from django.contrib.auth.decorators import login_required, permission_required
from django.http import (HttpResponse, HttpResponseForbidden, HttpResponseRedirect)
from django.core.exceptions import ImproperlyConfigured
from django.utils.decorators import method_decorator
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.views.generic import CreateView
from django.utils.http import urlquote
from django.conf import settings
from django.utils import simplejson as json
from django.core import serializers


#-----------------------------------------------------------------------------
# CUSTOM MIXINS
#-----------------------------------------------------------------------------
# many of the mixins here are taken from (now the django-braces module):
# http://brack3t.com/our-custom-mixins.html

class CreateAndRedirectToEditView(CreateView):
    """ Subclass of CreateView which redirects to the edit view.
    Requires property `success_url_name` to be set to a
    reversible url that uses the objects pk.
    """
    success_url_name = None

    def get_success_url(self):
        # First we check for a name to be provided on the view object.
        # If one is, we reverse it and finish running the method,
        # otherwise we raise a configuration error.
        if self.success_url_name:
            self.success_url = reverse(self.success_url_name,
                kwargs={'pk': self.object.pk})
            return super(CreateAndRedirectToEditView, self).get_success_url()

        raise ImproperlyConfigured(
            "No URL to reverse. Provide a success_url_name.")


class LoginRequiredMixin(object):
    """ View mixin which verifies that the user is authenticated.
    Saves you from having to write a dispatch method for every
    new class based view you want authentication protection on.

    NOTE: Of all mixins you add to a view, this should be added 1st.
    """
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)



class PermissionRequiredMixin(object):
    """ View mixin to verify the logged in user has the specified permission.

    Class Settings
    `permission_required` - the permission to check for.
    `login_url`           - the login url of site
    `redirect_field_name` - defaults to "next"
    `raise_exception`     - defaults to False - raise 403 if set to True

    EXAMPLE USE:

        class SomeView(PermissionRequiredMixin, ListView):
            ...
            # required
            permission_required = "app.permission"

            # optional
            login_url = "/signup/"
            redirect_field_name = "hollaback"
            raise_exception = True
            ...
    """
    login_url           = settings.LOGIN_URL
    permission_required = None
    raise_exception     = False
    redirect_field_name = REDIRECT_FIELD_NAME

    def dispatch(self, request, *args, **kwargs):
        # Verify class settings
        if self.permission_required == None or len(
            self.permission_required.split(".")) != 2:
            raise ImproperlyConfigured("'PermissionRequiredMixin' requires "
                "'permission_required' attribute to be set.")

        has_permission = request.user.has_perm(self.permission_required)

        if not has_permission:
            if self.raise_exception:
                return HttpResponseForbidden()
            else:
                path = urlquote(request.get_full_path())
                tup = self.login_url, self.redirect_field_name, path
                return HttpResponseRedirect("%s?%s=%s" % tup)

        return super(PermissionRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class SuperuserRequiredMixin(object):
    '''A permission based mixin that that requires
    one be a Super User in order to access content
    '''
    login_url           = settings.LOGIN_URL
    raise_exception     = False
    redirect_field_name = REDIRECT_FIELD_NAME

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            if self.raise_exception:
                return HttpResponseForbidden()
            else:
                path = urlquote(request.get_full_path())
                tup = self.login_url, self.redirect_field_name, path
                return HttpResponseRedirect("%s?%s=%s" % tup)

        return super(SuperuserRequiredMixin, self).dispatch(
            request, *args, **kwargs)



class UserFormKwargsMixin(object):
    """ Mixin that automates the process of overloading the get_form_kwargs
    method by putting the request.user into the forms kwargs.

    NOTE: to use this mixin you must pop() the user out from the kwargs
    dict in the super of your form's __init__ method, otherwise the form
    will get an unexpected kwarg and will go Chernobyl on your ass.

    EXAMPLE USE:

    class SomeForm(forms.ModelForm):
        class Meta:
            model = SomeModel

        def __init__(self, *args, **kwargs):
            self.user = kwargs.pop("user", None)
            super(SomeForm, self).__init__(*args, **kwargs)

            if self.user.is_superuser:
                # Allow them to do something awesome.

    class SomeSecretView(LoginRequiredMixin, UserFormKwargsMixin, TemplateView):
        form_class    = SomeForm
        model         = SomeModel
        template_name = "path/to/template.html"
    """
    def get_form_kwargs(self, **kwargs):
        kwargs = super(UserFormKwargsMixin, self).get_form_kwargs(**kwargs)
        kwargs.update({"user": self.request.user})
        return kwargs


class UserKwargModelFormMixin(object):
    """ Generic model form mixin for popping user out of the kwargs and
    attaching it to the instance.

    This mixin must precede forms.ModelForm/forms.Form. The form is not
    expecting these kwargs to be passed in, so they must be poppped off before
    anything else is done.

    EXAMPLE USE:
    class UserForm(UserKwargModelFormMixin, forms.ModelForm):
        class Meta:
            model = User

        def __init__(self, *args, **kwargs):
            super(UserForm, self).__init__(*args, **kwargs):

            if not self.user.is_superuser:
                del self.fields["group"]
    """
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(UserKwargModelFormMixin, self).__init__(*args, **kwargs)



class SuccessURLRedirectListMixin(object):
    """ Mixin that sets the success url to the list view of a given app
    Set success_list_url as a class attribute of your CBV and don't worry
    about overloading the get_success_url.

    This is only to be used for redirecting to a list page. If you need
    to reverse the url with kwargs, this is not the mixin to use.

    EXAMPLE USE:
    # urls.py
    url(r"^users/$", UserListView.as_view(), name="cms_users_list"),

    # views.py
    class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin,
                            SuccessURLRedirectListMixin, CreateView):
        form_class          = UserForm
        model               = User
        permission_required = "auth.add_user"
        success_list_url    = "cms_users_list"
        ...
    """
    success_list_url = None

    def get_success_url(self):
        return reverse(self.success_list_url)



class SetHeadlineMixin(object):
    """ Mixin that allows you to set a static headline via a static property
    on the View, or programmatically by overloading the get_headline method.
    This is helpful for if you need to frequently reusue generic templates.
    EXAMPLE USE:

    # STATIC EXAMPLE
    class HeadlineView(SetHeadlineMixin, TemplateView):
        headline      = "This is our headline"
        template_name = "path/to/template.html"

    # DYNAMIC EXAMPLE
    from datetime import date

    class HeadlineView(SetHeadlineMixin, TemplateView):
        template_name = "path/to/template.html"

        def get_headline(self):
            return u"This is our headline for %s" % date.today().isoformat()

    # use {{ headline }} in your template to show the generated headline
    """
    headline = None

    def get_context_data(self, **kwargs):
        kwargs = super(SetHeadlineMixin, self).get_context_data(**kwargs)
        kwargs.update({"headline": self.get_headline()})
        return kwargs

    def get_headline(self):
        if self.headline is None:
            raise ImproperlyConfigured(u"%(cls)s is missing a headline. Define "
                u"%(cls)s.headline, or override "
                u"%(cls)s.get_headline()." % {"cls": self.__class__.__name__ })
        return self.headline


class SelectRelatedMixin(object):
    """ Mixin allows you to provide a tuple or list of related models to
    perform a select_related on.
    """
    select_related = None  # Default related fields to none

    def get_queryset(self):
        if self.select_related is None:  # If no fields were provided,
                                         # raise a configuration error
            raise ImproperlyConfigured(u"%(cls)s is missing the select_related "
                "property. This must be a tuple or list." % {
                    "cls": self.__class__.__name__})

        if not isinstance(self.select_related, (tuple, list)):
            # If the select_related argument is *not* a tuple or list,
            # raise a configuration error.
            raise ImproperlyConfigured(u"%(cls)s's select_related property "
                "must be a tuple or list." % {"cls": self.__class__.__name__})

        # Get the current queryset of the view
        queryset = super(SelectRelatedMixin, self).get_queryset()

        # Return the queryset with a comma-joined argument to `select_related`.
        return queryset.select_related(
            ", ".join(self.select_related)
        )


class StaffuserRequiredMixin(object):
    """ Mixin allows you to require a user with `is_staff` set to True.
    """
    login_url = settings.LOGIN_URL  # LOGIN_URL from project settings
    raise_exception = False  # Default whether to raise an exception to none
    redirect_field_name = REDIRECT_FIELD_NAME  # Set by django.contrib.auth

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:  # If the request's user is not staff,
            if self.raise_exception:  # *and* if an exception was desired
                return HttpResponseForbidden()  # return a forbidden response
            else:
                # otherwise, redirect the user to the login page.
                # Also, handily, sets the GET `next` argument for
                # future redirects.
                path = urlquote(request.get_full_path())
                tup = self.login_url, self.redirect_field_name, path
                return HttpResponseRedirect("%s?%s=%s" % tup)

        return super(StaffuserRequiredMixin, self).dispatch(request,
            *args, **kwargs)


class JSONResponseMixin(object):
    """ Mixin that allows you to easily serialize simple data 
    such as a dict or Django models.
    """
    def render_json_response(self, context_dict):
        """ Limited serialization for shipping plain data.
        Do not use for models or other complex or custom objects.
        """
        ctx = json.dumps(context_dict)
        return HttpResponse(ctx, content_type="application/json")

    def render_json_object_response(self, objects, **kwargs):
        """ Serializes objects using Django's builtin JSON serializer.
        Additional kwargs can be used the same way for
        django.core.serializers.serialize.
        """
        json_data = serializers.serialize("json", objects, **kwargs)
        return HttpResponse(json_data, content_type="application/json")


class AjaxResponseMixin(object):
    """ Mixin allows you to define alternative methods for ajax requests. Similar
    to the normal get, post, and put methods, you can use get_ajax, post_ajax,
    and put_ajax.
    """
    def dispatch(self, request, *args, **kwargs):
        request_method = request.method.lower()

        if request.is_ajax() and request_method in self.http_method_names:
            handler = getattr(self, '%s_ajax' % request_method,
                self.http_method_not_allowed)
            self.request = request
            self.args = args
            self.kwargs = kwargs
            return handler(request, *args, **kwargs)

        return super(AjaxResponseMixin, self).dispatch(request, *args, **kwargs)


class AttrContext(object):
    ''' Convenience class for creating context items
    NOTE - do not use this in production
    '''
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    def __str__(self):
        return "\n".join(["%s: %s" % (k,v) for k,v in self.dict().iteritems()])

    def dict(self):
        return self.__dict__

    def update(self, data):
        for k, v in data.iteritems():
            setattr(self, k, v)
