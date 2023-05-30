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
"""

import xml.etree.ElementTree as ET

def overlay_gpx_on_tcx(tcx_file, gpx_file, output_file):
    # Load TCX file
    tcx_tree = ET.parse(tcx_file)
    tcx_root = tcx_tree.getroot()

    # Load GPX file
    gpx_tree = ET.parse(gpx_file)
    gpx_root = gpx_tree.getroot()

    # Find all trackpoints in the GPX file
    trackpoints = gpx_root.findall('.//trkpt')

    # Iterate over TCX trackpoints
    for i, trackpoint in enumerate(tcx_root.findall('.//Trackpoint')):
        # Get time from TCX trackpoint (if available)
        time_element = trackpoint.find('.//Time')
        time = time_element.text if time_element is not None else ''

        # Calculate distance from the start of the track
        distance_element = trackpoint.find('.//DistanceMeters')
        distance = float(distance_element.text) if distance_element is not None else None

        if distance is not None:
            # Find the corresponding GPX trackpoint based on index
            if i < len(trackpoints):
                gpx_trackpoint = trackpoints[i]

                # Extract latitude, longitude, and elevation from GPX trackpoint
                lat = float(gpx_trackpoint.attrib['lat'])
                lon = float(gpx_trackpoint.attrib['lon'])
                elevation_element = gpx_trackpoint.find('ele')
                elevation = float(elevation_element.text) if elevation_element is not None else None

                # Add latitude, longitude, and elevation to TCX trackpoint
                lat_element = ET.SubElement(trackpoint, 'Position/LatitudeDegrees')
                lat_element.text = str(lat)
                lon_element = ET.SubElement(trackpoint, 'Position/LongitudeDegrees')
                lon_element.text = str(lon)
                elevation_element = ET.SubElement(trackpoint, 'AltitudeMeters')
                elevation_element.text = str(elevation)

    # Save the modified TCX file
    tcx_tree.write(output_file)

# Usage example
tcx_file = 'source.tcx'
gpx_file = 'map.gpx'
output_file = 'output.tcx'
overlay_gpx_on_tcx(tcx_file, gpx_file, output_file)
