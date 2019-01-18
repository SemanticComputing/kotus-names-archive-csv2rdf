# Institute for the Languages of Finland (Kotus) Digital Names Archive CSV to RDF conversion

## Installation

pip install -r requirements.txt

## Conversion process

Using the latest CSV dump `Kotus_nadigi_testi_270418.csv` as an example source

The source CSV needs a header:

`cat Kotus_nadigi_header.csv Kotus_nadigi_testi_270418.csv > Kotus_nadigi_testi_270418_with_header.csv`

PHP script for converting the coordinates into WGS84, adds two new columns to source CSV:

`php convert_euref_to_wgs84.php`

Create place type ontology and convert the Names Archive CSV dump into RDF:

`python csv_to_rdf.py`
