# gpxovertcx
# by ChatGPT and @joshcvt

This is a largely ChatGPT-written project, built after I ran a 5K in the morning in which my watch's GPS didn't get a lock before I needed to start.
Since I knew the course exactly, I could draw the route on [Mapometer](http://us.mapometer.com), export it to GPX 1.1, carefully edit the height of 
the bridge on each end (because I definitely didn't do the 10-meter drop and run along the river surface like Mapometer thought), and get a TCX download of 
inertial 
distance, time, and heart-rate data from Garmin. Then, mapping points over route? It's basically parsing reasonably well-known XML formats, then applying 
[haversines](https://en.wikipedia.org/wiki/Haversine_formula) repetitively. ChatGPT should be able to do that, right?

Well, maybe. After a few iterations of teaching, it got the parsing and logic correct. The thing it couldn't figure out for itself, though, was that the
haversine function it coughed up returned kilometers, but TCX is in meters. Score one for humans.

To actually use this regularly, one thing I'd want is to catch when the interpolated sum of the GPS track length doesn't quite match the inertial distance
(assuming you know that's correct because the race organizers measured 5K), because that would break the mapping at the end.

Of course, next time I'll try to get a GPS lock a little earlier so I don't have to.
