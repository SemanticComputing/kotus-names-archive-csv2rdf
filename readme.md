# Institute for the Languages of Finland (Kotus) Digital Names CSV to RDF conversion

## Installation

pip install -r requirements.txt

## Conversion process

using `Kotus_Nadigi_050318.csv` as an example source

`cat header.csv Kotus_Nadigi_050318.csv > nimiarkisto.csv`

`php convert_euref_to_wgs84.php`

`python csv_to_rdf.py nimiarkisto_with_wsg84.csv output KOTUS`
