#!/usr/bin/env python
import os
import sys
from django.core import management

if __name__ == "__main__":
    #project = os.path.basename(os.path.dirname(__file__))
    #os.environ['DJANGO_SETTINGS_MODULE'] = '{}.settings'.format(project)
    sys.path.append(os.path.join(os.getcwd(), 'myproject/apps'))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    management.execute_from_command_line(sys.argv)

    #from django.core.management import execute_from_command_line
    #execute_from_command_line(sys.argv)
