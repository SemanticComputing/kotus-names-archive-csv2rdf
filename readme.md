# Institute for the Languages of Finland (Kotus) Digital Names Archive CSV to RDF conversion

## Installation

pip install -r requirements.txt

## Conversion process

using `Kotus_Nadigi_050318.csv` as an example source

The source CSV needs a header:

`cat header.csv Kotus_Nadigi_050318.csv > nimiarkisto.csv`

PHP script for converting the coordinates into WGS84, adds two new columns to source CSV:

`php convert_euref_to_wgs84.php`

Create place type ontology and convert the Names Archive CSV dump into RDF:

`python csv_to_rdf.py`
