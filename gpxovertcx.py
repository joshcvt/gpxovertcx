#!/usr/bin/env python

"""ChatGPT prompt:

ChatGPT, write me a python script that takes as input a Garmin TCX export that contains distance trackpoints 
but no latitude/longitude or elevation information and a GPX file containing a course of the same distance 
and overlays the GPX track on the TCX.

Response:

Certainly! Here's a Python script that takes a Garmin TCX export file and a GPX file as input, and overlays 
the GPX track on the TCX file by adding latitude, longitude, and elevation information to the TCX trackpoints.

Result:
gpxpy doesn't like the GPX from Mapometer.com.

New prompt:

The logic is good, but the gpxpy module doesn't like my gpx file. ElementTree believes it's valid XML. Can 
you use this same logic, but use xml.etree.ElementTree to parse the GPX instead of gpxpy?

Result:
with some debug statements (not captured), it's finding zero elements of trkpt or Trackpoint.

New prompt:

Do it with minidom instead, please.

Result:

Probably almost right, except it wants to update the nonexistent Position element instead of creating it.

New prompt:

Almost right. trackpoint.getElementsByTagName('Position')[0] returns an IndexError: list index out of 
range error. Can you check for this and add a new Position element to the trackpoint element if that happens?

Result:

It doesn't have the distances right, but it produces workable XML that imports to Smashrun.

New prompt:

This code mapped a 5010-meter course to only the first 1565 meters of the TCX inertial distance. Are you sure 
you're interpolating correctly?

Result: tries to do haversine, instead just moves us to the farthest away point of the course.

Prompt:
That got worse. It moved immediately to the geographically farthest-away point of the GPX course and stayed there for the whole length of the TCX file.
Result: looks for gpxdata:distance. doesn't have it.

Result: still fail

Prompt: you can't do 
curr_distance_elements = trackpoints[j].getElementsByTagName('extensions')[0].getElementsByTagName('gpxdata:distance')
you still don't have that gpxdata:distance. you're going to have to track the elements as you go through the loop

Result: back to jumping straight to the farthest-away point in the track


"""

from xml.dom import minidom
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1, lon1, lat2, lon2):
    # Calculate the distance between two coordinates using the Haversine formula
    # Reference: https://en.wikipedia.org/wiki/Haversine_formula

    # Convert latitude and longitude to radians
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    radius = 6371  # Radius of the Earth in kilometers
    distance = radius * c

    return distance

def overlay_gpx_on_tcx(tcx_file, gpx_file, output_file):
    # Load TCX file
    tcx_doc = minidom.parse(tcx_file)
    tcx_root = tcx_doc.documentElement

    # Load GPX file
    gpx_doc = minidom.parse(gpx_file)
    gpx_root = gpx_doc.documentElement

    # Find all trackpoints in the GPX file
    trackpoints = gpx_root.getElementsByTagName('trkpt')

    # Calculate cumulative distances in the GPX track
    cumulative_distances = [0.0]
    for i in range(1, len(trackpoints)):
        lat1 = float(trackpoints[i-1].getAttribute('lat'))
        lon1 = float(trackpoints[i-1].getAttribute('lon'))
        lat2 = float(trackpoints[i].getAttribute('lat'))
        lon2 = float(trackpoints[i].getAttribute('lon'))

        distance = haversine_distance(lat1, lon1, lat2, lon2)
        cumulative_distance = cumulative_distances[i-1] + distance
        cumulative_distances.append(cumulative_distance)

    # Iterate over TCX trackpoints
    for i, trackpoint in enumerate(tcx_root.getElementsByTagName('Trackpoint')):
        # Get time from TCX trackpoint (if available)
        time_elements = trackpoint.getElementsByTagName('Time')
        time = time_elements[0].firstChild.nodeValue if time_elements else ''

        # Calculate distance from the start of the track
        distance_elements = trackpoint.getElementsByTagName('DistanceMeters')
        distance = float(distance_elements[0].firstChild.nodeValue) if distance_elements else None

        if distance is not None:
            # Find the corresponding GPX trackpoints based on distance
            prev_trackpoint = None
            next_trackpoint = None
            prev_cumulative_distance = None
            next_cumulative_distance = None

            for j in range(len(cumulative_distances)):
                if distance <= cumulative_distances[j]:
                    prev_trackpoint = trackpoints[j-1]
                    next_trackpoint = trackpoints[j]
                    prev_cumulative_distance = cumulative_distances[j-1]
                    next_cumulative_distance = cumulative_distances[j]
                    break

            if prev_trackpoint is not None and next_trackpoint is not None:
                # Interpolate latitude, longitude, and elevation
                ratio = (distance - prev_cumulative_distance) / (next_cumulative_distance - prev_cumulative_distance)
                lat1 = float(prev_trackpoint.getAttribute('lat'))
                lon1 = float(prev_trackpoint.getAttribute('lon'))
                lat2 = float(next_trackpoint.getAttribute('lat'))
                lon2 = float(next_trackpoint.getAttribute('lon'))

                lat = lat1 + (lat2 - lat1) * ratio
                lon = lon1 + (lon2 - lon1) * ratio

                # Create latitude and longitude elements
                lat_element = tcx_doc.createElement('LatitudeDegrees')
                lat_text = tcx_doc.createTextNode(str(lat))
                lat_element.appendChild(lat_text)

                lon_element = tcx_doc.createElement('LongitudeDegrees')
                lon_text = tcx_doc.createTextNode(str(lon))
                lon_element.appendChild(lon_text)

                # Remove existing position elements from TCX trackpoint
                position_elements = trackpoint.getElementsByTagName('Position')
                for position_element in position_elements:
                    trackpoint.removeChild(position_element)

                # Add interpolated latitude and longitude to TCX trackpoint
                position_element = tcx_doc.createElement('Position')
                position_element.appendChild(lat_element)
                position_element.appendChild(lon_element)
                trackpoint.appendChild(position_element)

    # Save the modified TCX file
    with open(output_file, 'w') as f:
        f.write(tcx_doc.toprettyxml(indent='\t'))

                    
# Usage example
tcx_file = 'source.tcx'
gpx_file = 'map.gpx'
output_file = 'output.tcx'
overlay_gpx_on_tcx(tcx_file, gpx_file, output_file)
