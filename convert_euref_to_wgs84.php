<?php

//
// Muunnosfunktiot koordinaattiprojektioille
// K�ytt�esimerkit ja testausfunktio
// ETRS89-TM35FIN, geodeettisista tasokoordinaateiksi ja takaisin
//
// L�hde: JHS 154, 6.6.2008
// http://www.jhs-suositukset.fi/web/guest/jhs/recommendations/154
//
// 2013-04-29/JeH, loukko (at) loukko (dot) net
// http://www.loukko.net/koord_proj/
// Vapaasti k�ytett�viss� ilman toimintatakuuta.
//

// Lis�t��n muunnoskirjasto
include("koord_proj.php");

$rows = array();
$file_name = "./source_data/Kotus_nadigi_testi_270418_first_2000_lines_with_header.csv";

if (($handle = fopen($file_name, "r")) !== FALSE) {
    $first = True;
    while (($row = fgetcsv($handle, 0, ",")) !== FALSE) {
	// print_r($row);
	if (count($row) <= 1) {
	   break;
	}
	else if ($row[0] == "ID" ) {
          array_push($row, "wgs84_long", "wgs84_lat");
        } else if ( $row[19] == -1 or $row[18] == -1 ) {
          array_push($row, -1, -1);
        } else {
          $conversion = koordTG($row[19], $row[18]);
          array_push($row, $conversion['pit'], $conversion['lev']);
        }
        array_push($rows, $row);
    }
    fclose($handle);
}

$fp = fopen('./source_data/Kotus_nadigi_testi_270418_first_2000_lines_with_header_with_WGS84.csv', 'w');

foreach ($rows as $row) {
    fputcsv($fp, $row);
}

fclose($fp);


// Muunnetaan tasokoordinaatit geodeettisiksi
//$muunnos = koordTG(6715706.37705, 106256.35958); // N, E
//$leveysaste = $muunnos['lev'];
//$pituusaste = $muunnos['pit'];

// Muunnetaan geodeettiset koordinaatit tasokoordinaateiksi
//$muunnos = koordGT(60.385106872, 19.848136769);	// lev, pit
//$northing = $muunnos['N'];
//$easting  = $muunnos['E'];

//echo ("Tulokset: $leveysaste, $pituusaste, $northing, $easting");
// Tulokset: 60.38510687197, 19.848136766751, 6715706.37704, 106256.3597039

//echo ("<br><br><hr><br>");

// Ajetaan testifunktio
//koord_testi();

?>
