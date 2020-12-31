# geoutils

A small set of python utilities functions created for my Sask RM map project.

This library allows me to convert Statistics Canada boundary data from a [.zip file provided by statcan](https://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/bound-limit-eng.cfm) to geojson in order to make the data easier to work with in javascript. It also lets me assign colors to regions using 5-Color [Graph Coloring](https://en.wikipedia.org/wiki/Graph_coloring) via constraint satifaction. 

### dependancies
- geopandas 
- python-constraint