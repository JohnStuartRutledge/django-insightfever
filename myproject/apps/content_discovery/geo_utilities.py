'''
This file contains functions that help you perform geographic proximity
matches to help find places of interest that can be used as content
on clients social media pages.

In order to make the distance function available to SQLLite we use the
connection_create signal and the connection.create_function
'''

from django.dispatch import reciever
from django.db import models
from math import sin, cos, acos, radians


def distance(p1_lat,p1_long,p2_lat,p2_long):
    ''' Calculates the distance between p1 and p2 given their 
    longitude and latitude, using the spherical law of cosines
    '''
    # multiplier = 6371 # for kilometers
    multiplier = 3959 # for miles
    return ( multiplier *
    acos(
        cos(radians(p1_lat)) *
        cos(radians(p2_lat)) *
        cos(radians(p2_long) - radians(p1_long)) +
        sin(radians(p1_lat)) * sin(radians(p2_lat))
        )
    )


@receiver(connection_created)
def setup_proximity_func(connection, **kwargs):
    ''' Add the proximity function to sqlite
    '''
    connection.connection.create_function("distance", 4, distance)


class LocationManager(models.Manager):
    ''' Location model manager used to do proximity queries
    '''
    def within(self,location,distance):
        ''' Finds locations within <distance> miles of <location>
        '''
        subquery  = 'distance(%(latitude)s,%(longitude)s,latitude,longitude) ' % location.__dict__
        condition = 'proximity < %s' % distance
        order     = 'proximity'
        return self.extra(select={'proximity':subquery},
                          where=[condition]).order_by(order)


class Location(models.Model):
    ''' Location model
    ''' 
    objects   = LocationManager()
    name      = models.CharField()
    latitude  = models.FloatField()
    longitude = models.FloatField()



# EXAMPLE USE OF CODE

# add some locations
Location(name='Tiergarten', latitude=52.525498, longitude=13.34274).save()
Location(name='Hasenheide', latitude=52.487907, longitude=13.415851).save()
Location(name='Mauerpark' , latitude=52.523405, longitude=13.4114).save()

park = Location.objects.get(name='Mauerpark')

# get parks within 2 km of Mauerpark
Location.objects.within(park, distance=2)

