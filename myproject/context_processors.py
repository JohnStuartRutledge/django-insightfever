from django.conf import settings

def get_current_path(request):
    '''get current URL path in all templates
    '''
    return { 'current_path': request.get_full_path() }

