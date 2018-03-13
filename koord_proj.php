<?php

//
// Muunnosfunktiot koordinaattiprojektioille
// ETRS89-TM35FIN, geodeettisista tasokoordinaateiksi ja takaisin
//
// Lähde: JHS 154, 6.6.2008
// http://www.jhs-suositukset.fi/web/guest/jhs/recommendations/154
//
// 2013-04-29/JeH, loukko (at) loukko (dot) net
// http://www.loukko.net/koord_proj/
// Vapaasti käytettävissä ilman toimintatakuuta.
//

//
// Muuntaa desimaalimuotoiset leveys- ja pituusasteet ETRS-TM35FIN -muotoisiksi tasokoordinaateiksi
//
// koordGT(60.385106872, 19.848136769) --> array(2) { ["N"]=> float(106256.3597039) ["E"]=> float(6715706.37704) }

function koordGT($lev_aste, $pit_aste) {
	
	// Vakiot
	$f = 1 / 298.257222101;				// Ellipsoidin litistyssuhde
	$a = 6378137;									// Isoakselin puolikas
	$lambda_nolla = 0.471238898;	// Keskimeridiaani (rad), 27 astetta
	$k_nolla = 0.9996;						// Mittakaavakerroin
	$E_nolla = 500000;						// Itäkoordinaatti
	
	// Kaavat
	
	// Muunnetaan astemuotoisesta radiaaneiksi
	$fii = deg2rad($lev_aste);
	$lambda = deg2rad($pit_aste);
	
	$n = $f / (2-$f);
	$A1 = ($a/(1+$n)) * (1 + (pow($n, 2)/4) + (pow($n, 4)/64));
	$e_toiseen = (2 * $f) - pow($f, 2);
	$e_pilkku_toiseen = $e_toiseen / (1 - $e_toiseen);
	$h1_pilkku = (1/2)*$n - (2/3)*pow($n, 2) + (5/16)*pow($n, 3) + (41/180)*pow($n, 4);
	$h2_pilkku = (13/48)*pow($n, 2) - (3/5)*pow($n, 3) + (557/1440)*pow($n, 4);
	$h3_pilkku =(61/240)*pow($n, 3) - (103/140)*pow($n, 4);
	$h4_pilkku = (49561/161280)*pow($n, 4);
	$Q_pilkku = asinh( tan($fii));
	$Q_2pilkku = atanh(sqrt($e_toiseen) * sin($fii));
	$Q = $Q_pilkku - sqrt($e_toiseen) * $Q_2pilkku;
	$l = $lambda - $lambda_nolla;
	$beeta = atan(sinh($Q));
	$eeta_pilkku = atanh(cos($beeta) * sin($l));
	$zeeta_pilkku = asin(sin($beeta)/(1/cosh($eeta_pilkku)));
	$zeeta1 = $h1_pilkku * sin( 2 * $zeeta_pilkku) * cosh( 2 * $eeta_pilkku);
	$zeeta2 = $h2_pilkku * sin( 4 * $zeeta_pilkku) * cosh( 4 * $eeta_pilkku);
	$zeeta3 = $h3_pilkku * sin( 6 * $zeeta_pilkku) * cosh( 6 * $eeta_pilkku);
	$zeeta4 = $h4_pilkku * sin( 8 * $zeeta_pilkku) * cosh( 8 * $eeta_pilkku);
	$eeta1 = $h1_pilkku * cos( 2 * $zeeta_pilkku) * sinh( 2 * $eeta_pilkku);
	$eeta2 = $h2_pilkku * cos( 4 * $zeeta_pilkku) * sinh( 4 * $eeta_pilkku);
	$eeta3 = $h3_pilkku * cos( 6 * $zeeta_pilkku) * sinh( 6 * $eeta_pilkku);
	$eeta4 = $h4_pilkku * cos( 8 * $zeeta_pilkku) * sinh( 8 * $eeta_pilkku);
	$zeeta = $zeeta_pilkku + $zeeta1 + $zeeta2 + $zeeta3 + $zeeta4;
	$eeta = $eeta_pilkku + $eeta1 + $eeta2 + $eeta3 + $eeta4;
	
	// Tulos tasokoordinaatteina
	$N = $A1 * $zeeta * $k_nolla;
	$E = $A1 * $eeta * $k_nolla + $E_nolla;

	$array = array ('N' => $N, 'E' => $E);
	return $array;
}


// koordTG 
//
// Muuntaa ETRS-TM35FIN -muotoiset tasokoordinaatit desimaalimuotoisiksi leveys- ja pituusasteiksi
//
// koordTG(106256.35958, 6715706.37705) --> array(2) { ["lev"]=> float(60.38510687197) ["pit"]=> float(19.848136766751) }

function koordTG($N, $E) {

	// Vakiot	
	$f = 1 / 298.257222101;				// Ellipsoidin litistyssuhde
	$a = 6378137;									// Isoakselin puolikas
	$lambda_nolla = 0.471238898;	// Keskimeridiaani (rad), 27 astetta
	$k_nolla = 0.9996;						// Mittakaavakerroin
	$E_nolla = 500000;						// Itäkoordinaatti
	
	// Kaavat
	$n = $f / (2-$f);
	$A1 = ($a/(1+$n)) * (1 + (pow($n, 2)/4) + (pow($n, 4)/64));
	$e_toiseen = (2 * $f) - pow($f, 2);
	$h1 = (1/2)*$n - (2/3)*pow($n, 2) + (37/96)*pow($n, 3) - (1/360)*pow($n, 4);
	$h2 = (1/48)*pow($n, 2) + (1/15)*pow($n, 3) - (437/1440)*pow($n, 4);
	$h3 =(17/480)*pow($n, 3) - (37/840)*pow($n, 4);
	$h4 = (4397/161280)*pow($n, 4);
	$zeeta = $N / ($A1 * $k_nolla);
	$eeta = ($E - $E_nolla) / ($A1 * $k_nolla);
	$zeeta1_pilkku = $h1 * sin( 2 * $zeeta) * cosh( 2 * $eeta);
	$zeeta2_pilkku = $h2 * sin( 4 * $zeeta) * cosh( 4 * $eeta);
	$zeeta3_pilkku = $h3 * sin( 6 * $zeeta) * cosh( 6 * $eeta);
	$zeeta4_pilkku = $h4 * sin( 8 * $zeeta) * cosh( 8 * $eeta);
	$eeta1_pilkku = $h1 * cos( 2 * $zeeta) * sinh( 2 * $eeta);
	$eeta2_pilkku = $h2 * cos( 4 * $zeeta) * sinh( 4 * $eeta);
	$eeta3_pilkku = $h3 * cos( 6 * $zeeta) * sinh( 6 * $eeta);
	$eeta4_pilkku = $h4 * cos( 8 * $zeeta) * sinh( 8 * $eeta);
	$zeeta_pilkku = $zeeta - ($zeeta1_pilkku + $zeeta2_pilkku + $zeeta3_pilkku + $zeeta4_pilkku);
	$eeta_pilkku = $eeta - ($eeta1_pilkku + $eeta2_pilkku + $eeta3_pilkku + $eeta4_pilkku);
	$beeta = asin((1/cosh($eeta_pilkku)*sin($zeeta_pilkku)));
	$l = asin(tanh($eeta_pilkku)/(cos($beeta)));
	$Q = asinh(tan($beeta));
	$Q_pilkku = $Q + sqrt($e_toiseen) * atanh(sqrt($e_toiseen) * tanh($Q));
	
	for ($kierros = 1; $kierros < 5; $kierros++) {
		$Q_pilkku = $Q + sqrt($e_toiseen) * atanh(sqrt($e_toiseen) * tanh($Q_pilkku));
	}
	
	// Tulos radiaaneina
	$fii = atan(sinh($Q_pilkku));
	$lambda = $lambda_nolla + $l;

	// Tulos asteina
	$fii = rad2deg($fii);
	$lambda = rad2deg($lambda);

	$array = array ('lev' => $fii, 'pit' => $lambda);
	return $array;
	
}

// koord_testi
//
// Testataan funktioiden toimivuus ja tarkkuus
//

function koord_testi() {
		
	//
	// Geodeettisista tasokoordinaateiksi
	//
																				// Piste G4 (Geta)
	$fii    = 60 + 23/60 +  6.38474/3600;	// 60 astetta, 23 minuuttia, 06,38474 sekuntia
	$lambda = 19 + 50/60 + 53.29237/3600;	// 19 astetta, 50 minuuttia, 53.29237 sekuntia
	
	// Koordinaatit radiaaneina
	$fii_r    = deg2rad($fii);
	$lambda_r = deg2rad($lambda);
	
	// Muunnos
	$t_koord = koordGT($fii, $lambda);
	
	// Ero esimerkin laskettuihin arvoihin
	$N_ero = ($t_koord['N'] - 6715706.37708)*1000;
	$E_ero = ($t_koord['E'] - 106256.35961)*1000;
	
	
	
	//
	// Tasokoordinaateiksi geodeettisiksi koordinaateiksi
	//
	
	// Pisteen tasokoordinaatit
	$N = 6715706.37705;
	$E = 106256.35958;
		
	// Muunnos
	$g_koord = koordTG($N, $E);
	
	// Muunnoksen tulos
	$lev = $g_koord['lev'];
	$pit = $g_koord['pit'];
	
	// Tulos radiaaneina
	$lev_r = deg2rad($lev);
	$pit_r = deg2rad($pit);
	
	// Ero radiaaneina
	$lev_ero_r = ($lev_r - 1.053918934084532);
	$pit_ero_r = ($pit_r - 0.346415337004409);
	
	// Ero asteina
	$lev_ero_d = ($lev - rad2deg(1.053918934084532));
	$pit_ero_d = ($pit - rad2deg(0.346415337004409));
	
	// Eroarvio millimetreinä
	// http://www.maanmittauslaitos.fi/kartat/koordinaatit/3d-koordinaatistot/suorakulmaiset-maantieteelliset-koordinaatistot
	// Leveysaste ~ 111.5 km, pituusaste Keski-Suomessa ~ 14 km
	
	$lev_ero_m = ($lev_ero_d * 111.5 * 1000 * 1000);
	$pit_ero_m = ($pit_ero_d * 14 * 1000 * 1000);
	
	
	// Näytetään tulokset
	echo <<<HERE

<h2>Geodeettisista tasokoordinaateiksi</h2>

<b>Geodeettiset koordinaatit (lev, pit)</b><br>
$fii, $lambda (deg)<br>
$fii_r, $lambda_r (rad)<br>
<br>
<b>Tasokoordinaatit (N, E)</b><br>
{$t_koord['E']}, {$t_koord['N']} (m)<br>
<br>
<b>Esimerkin lasketut arvot (N, E)</b><br>
106256.35961, 6715706.37708 (m)<br>
<br>
<b>Ero laskettuihin arvoihin (N, E)</b><br>
$N_ero, $E_ero (millimetriä)<br>


<h2>Tasokoordinaateiksi geodeettisiksi koordinaateiksi</h2>

<b>Tasokoordinaatit (N, E)</b><br>
$N, $E (m)<br>
<br>
<b>Geodeettiset koordinaatit (lev, pit)</b><br>
$lev, $pit (deg)<br>
$lev_r, $pit_r (rad)<br>
<br>
<b>Esimerkin lasketut arvot (lev, pit)</b><br>
1.053918934084532, 0.346415337004409 (rad)<br>
<br>
<b>Ero laskettuihin arvoihin (lev, pit)</b><br>
$lev_ero_r, $pit_ero_r (rad)<br>
$lev_ero_d, $pit_ero_d (deg)<br>
$lev_ero_m, $pit_ero_m (millimetriä)<br>
<br>
Kirjoitushetkellä GT-muunnoksen virheet olivat -0.018 ja 0.121 mm, ja TG-muunnoksen virheet 0 
ja -3.847 x 10<sup>-11</sup> rad. <br>
<small>(PHP Version 5.3.2-1ubuntu4.9, Linux ubuntu 2.6.32-32-generic #62-Ubuntu SMP Wed Apr 20 21:54:21 UTC 2011 i686)</small><br>
<br>
Epätarkkuudet johtuvat ohjelmointiympäristöjen ja käyttöjärjestelmien matemaattisista ominaisuuksista. <br>
Jos arvoissa on karkeita virheitä, koodi voi olla epäyhteensopivaa käyttöympäristöön (&pi; = 3.00), tai koodissa on virhe.<br>

HERE;

}



?>