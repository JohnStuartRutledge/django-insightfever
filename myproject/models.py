from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db import models


class TimeStamp(models.Model):
    ''' Abstract model for holding timestamp information
    '''
    created_on = models.DateTimeField(auto_now_add=True, editable=False, null=True)
    created_by = models.ForeignKey(User, db_column="created_by", 
                                   related_name="%(app_label)s_%(class)s_created_by")
    updated_on = models.DateTimeField(null=True)
    updated_by = models.ForeignKey(User, db_column="updated_by", null=True,
                                   related_name="%(app_label)s_%(class)s_updated_by")

    class Meta:
        abstract = True


class FeverBase(models.Model):
    ''' Abstract base class for holding common reusable fields
    '''
    def get_fields(self):
        '''Method for easily printing out all the 
        field names and values of a object instance'''
        foo = {}
        ls  = self._meta.fields + self._meta.many_to_many
        for field in ls:
            try: foo[field.name] = field.value_to_string(self)
            except AttributeError: foo[field.name] = field
        return foo
    
    def get_fields_and_properties(self):
        ''' Method for returning a dict of fields and their properties
        see the following link for another, possibly superior technique:
        http://stackoverflow.com/questions/2170228/django-iterate-over-model-instance-field-names-and-values-in-template

        How to use it:
            instance = MyModel()
            print get_fields_and_properties(MyModel, instance)
        '''
        klass = self.__class__
        field_names    = [f.name for f in klass._meta.fields]
        property_names = [name for name in dir(klass) if isinstance(getattr(klass, name), property)]
        return dict((name, getattr(self, name)) for name in field_names + property_names)
    
    class Meta:
        abstract = True

