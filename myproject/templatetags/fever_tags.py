from django import template
from django.template import Context
from django.template.loader import get_template

register = template.Library()

@register.filter()
def field_type(field):
    '''
    Returns the name of a form field. Useful if you don't know
    ahead of time what the field type will be, and you want to
    react dynamically based on the fields type. AN EXAMPLE USE:

        {% if not field|field_type ="DateField" %}
            <span>Whatever</span>
        {%endif%}
    '''
    return field.field.__class__.__name__


@register.filter
def as_bootstrap(form):
    template = get_template("bootstrap/form.html")
    ctx = Context({"form": form})
    return template.render(ctx)

@register.filter(name="dir")
def dirr(item):
    return dir(item)
