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

"""

import xml.etree.ElementTree as ET
from gpxpy import parse

def overlay_gpx_on_tcx(tcx_file, gpx_file, output_file):
    # Load TCX file
    tcx_tree = ET.parse(tcx_file)
    tcx_root = tcx_tree.getroot()

    # Load GPX file
    gpx_data = parse(gpx_file)
    gpx_track = gpx_data.tracks[0]
    gpx_segments = gpx_track.segments

    # Iterate over TCX trackpoints
    for trackpoint in tcx_root.findall('.//Trackpoint'):
        # Get time from TCX trackpoint (if available)
        time_element = trackpoint.find('.//Time')
        time = time_element.text if time_element is not None else ''

        # Calculate distance from the start of the track
        distance_element = trackpoint.find('.//DistanceMeters')
        distance = float(distance_element.text) if distance_element is not None else None

        if distance is not None:
            # Find the corresponding GPX trackpoint based on distance
            for segment in gpx_segments:
                for i in range(len(segment.points) - 1):
                    point1 = segment.points[i]
                    point2 = segment.points[i + 1]
                    segment_distance = point2.distance_2d(point1)

                    if distance <= segment_distance:
                        # Interpolate latitude, longitude, and elevation
                        segment_ratio = distance / segment_distance
                        lat = point1.latitude + (point2.latitude - point1.latitude) * segment_ratio
                        lon = point1.longitude + (point2.longitude - point1.longitude) * segment_ratio
                        elevation = point1.elevation + (point2.elevation - point1.elevation) * segment_ratio

                        # Add latitude, longitude, and elevation to TCX trackpoint
                        lat_element = ET.SubElement(trackpoint, 'Position/LatitudeDegrees')
                        lat_element.text = str(lat)
                        lon_element = ET.SubElement(trackpoint, 'Position/LongitudeDegrees')
                        lon_element.text = str(lon)
                        elevation_element = ET.SubElement(trackpoint, 'AltitudeMeters')
                        elevation_element.text = str(elevation)

                        break  # Exit the loop once the GPX trackpoint is found and processed
                    else:
                        distance -= segment_distance

    # Save the modified TCX file
    tcx_tree.write(output_file)

# Usage example
tcx_file = 'source.tcx'
gpx_file = 'map.gpx'
output_file = 'output.tcx'
overlay_gpx_on_tcx(tcx_file, gpx_file, output_file)
