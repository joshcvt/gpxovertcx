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

"""

from xml.dom import minidom

def overlay_gpx_on_tcx(tcx_file, gpx_file, output_file):
    # Load TCX file
    tcx_doc = minidom.parse(tcx_file)
    tcx_root = tcx_doc.documentElement

    # Load GPX file
    gpx_doc = minidom.parse(gpx_file)
    gpx_root = gpx_doc.documentElement

    # Find all trackpoints in the GPX file
    trackpoints = gpx_root.getElementsByTagName('trkpt')

    # Iterate over TCX trackpoints
    for i, trackpoint in enumerate(tcx_root.getElementsByTagName('Trackpoint')):
        # Get time from TCX trackpoint (if available)
        time_elements = trackpoint.getElementsByTagName('Time')
        time = time_elements[0].firstChild.nodeValue if time_elements else ''

        # Calculate distance from the start of the track
        distance_elements = trackpoint.getElementsByTagName('DistanceMeters')
        distance = float(distance_elements[0].firstChild.nodeValue) if distance_elements else None

        if distance is not None:
            # Find the corresponding GPX trackpoint based on index
            if i < len(trackpoints):
                gpx_trackpoint = trackpoints[i]

                # Extract latitude, longitude, and elevation from GPX trackpoint
                lat = float(gpx_trackpoint.getAttribute('lat'))
                lon = float(gpx_trackpoint.getAttribute('lon'))
                elevation_elements = gpx_trackpoint.getElementsByTagName('ele')
                elevation = float(elevation_elements[0].firstChild.nodeValue) if elevation_elements else None

                # Create latitude, longitude, and elevation elements
                lat_element = tcx_doc.createElement('LatitudeDegrees')
                lat_text = tcx_doc.createTextNode(str(lat))
                lat_element.appendChild(lat_text)

                lon_element = tcx_doc.createElement('LongitudeDegrees')
                lon_text = tcx_doc.createTextNode(str(lon))
                lon_element.appendChild(lon_text)

                elevation_element = tcx_doc.createElement('AltitudeMeters')
                elevation_text = tcx_doc.createTextNode(str(elevation))
                elevation_element.appendChild(elevation_text)

                # Add latitude, longitude, and elevation to TCX trackpoint
                position_element = trackpoint.getElementsByTagName('Position')[0]
                position_element.appendChild(lat_element)
                position_element.appendChild(lon_element)
                trackpoint.appendChild(elevation_element)

    # Save the modified TCX file
    with open(output_file, 'w') as f:
        f.write(tcx_doc.toprettyxml(indent='\t'))

# Usage example
tcx_file = 'source.tcx'
gpx_file = 'map.gpx'
output_file = 'output.tcx'
overlay_gpx_on_tcx(tcx_file, gpx_file, output_file)
