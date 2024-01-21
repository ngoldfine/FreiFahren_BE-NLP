"""

"""

import unittest
from main import find_station, find_line, ubahn_lines, sbahn_lines

class TestFindStationAndLineFunction(unittest.TestCase):
    def test_find_station_and_line(self):
        test_cases = [
            ("heinrich-heine zwei blauwesten", "Heinrich-Heine-Straße", None),
            ("U6 Schumacher-Platz 2 Controller merhingdam", "Schumacherplatz", "U6"),
            ("2x Hellblau U8 Hermannplatz Richtung Wittenau am Bahnsteig", "Hermannplatz", "U8"),
            ("U8 pankstrasse 2 Blau veste", "Pankstraße", "U8"),
            ("2 Kontrolleure U9 Richtung Osloer Straße", "Osloer Straße", "U9"),
            ("Und zwei Cops oben am Bahnsteig der SBahn", None, None),
            ("U 8 Heinrich Heine str", "Heinrich-Heine-Straße", "U8"),
            ("Friedrichstrasse bei der u6 waren gerade zwei mit bos westen", "Friedrichstraße", "U6"),
            ("2personen dunkel blaue weste", None, None),
            ("U2 Ernst Reuter Platz", "Ernst-Reuter-Platz", "U2"),
            ("U9 4 (oder mehr) blauwesten auf Gleis Spichernstraße", "Spichernstraße", "U9"),
            ("Zwei Stück Richtung Osloer", None, None),
            ("Jetzt Zoo in der Bahn richtung Steglitz!", "Zoologischer Garten", None),
            ("U6 Mehringdamm -> hallesches Tor gerade ausgestiegen. 2 Kontrolleure in schwarz, glaube ich. :", "Hallesches Tor", None),
            ("S Alexanderplatz west direction at least one ticket checker with a white puffer jacket on the platform", "Alexanderplatz", None),
            ("u6 leopoldplatz towards alt mariendorf 2 people with 2 cops", "Leopoldplatz", "U6"),
            ("u6 paradestraße ausgestiegen.", "Paradestraße", "U6"),
            ("M10 towards turmstr. two guys with no uniform", None, None),
            ("U boddinstrasse. 5 security's / 3 cops", "Boddinstraße", None),
            ("Gerade S Tiergarten Richtung zoo", "Tiergarten", None),
            ("Walther Schreiber Platz U9 Richtung Rathaus Steglitz Kontrolletis", "Walther-Schreiber-Platz", "U9"),
            ("2 in schwarz S tempelhof", "Tempelhof", None),
            ("Grad ausgestiegen s41", None, None),
            ("S7, 2 männlich gelesene in zivil grad Friedrichstraße mit jemandem ausgestiegen", "Friedrichstraße", "S7"),
            ("Ring zwischen S Tempelhof und S Hermannstraße", "Tempelhof", None),
            ("U2 Märkisches Museum richting ruhleben 3 Männer mit B.O.S Jacken", "Märkisches Museum", "U2"),
            ("Ring Bahn Hohenzollerndamm vor 2 Minuten eine Person alleine", "Hohenzollerndamm", None),
            ("S1 Richtung Spindersfeld, männlich gelesen gerade bei hermannstraße geht durch die Bahn", "Hermannstraße", "S1"),
            ("S1 nach spindlersfelde war ein am hermannplatz oder vorher", "Hermannplatz", "S1"),
            ("U8 Wittenau sind U Jannowitzbrücke raus", "Jannowitzbrücke", "U8"),
            ("messe nord grad raus", "Messe Nord", None),
            ("3x weiblich jetzt westkreuz ina s41", "Westkreuz", "S41"),
            ("Kontrolle in s42 jetzt Treptower Park", "Treptower Park", "S42"),
            ("Kontrolle auf der Strecke u9", None, "U9"),
            ("BOS Alex u8 on the platform", "Alexanderplatz", "U8"),
            ("A lot of bvg and cops, outside, at Hermanplatz", "Hermannplatz", None),
            ("3x m gelesen 1x w gelesen am hermannplatz Gleis u8 Richtung hermannstraße blaue bos jacken", "Hermannplatz", "U8"),
            ("S42 greiswalder strasse2 Männer 1 frau", "Greifswalder Straße", "S42"),
            ("Ring zwischen Hohenzollerndamm und Halensee. 3x weiblich gelesen, davon 1x weiße Jacke, 1x schwarz glänzende Jacke", "Hohenzollerndamm", None),
            ("2 Kontrolleure read male black outfits black beards in S8 to Ostkreuz, now Storkower Str got off at Storkower Straße", "Storkower Straße", "S8"), 
            ("S41 gleich Tempelhof. Ein Typ, eine Frau. Beide schwarze Kapuzenjacke. Er mit North Face Mütze schwarz, Sie mit langen blonden Haaren", "Tempelhof", "S41"),
            ("U6 steigen gerade Wedding ein Richtung alt mariendorf im hinteren Teil der Bahn 3m blaue Jacken", "Wedding", "U6"),
            ("Kontrolleur m gelesen S2 Frohnau jetzt Halensee In zivil, schwarze Jacke, schwarze Haare, braune Ledertasche", "Halensee", "S2"),
            ("Jannowitzbrücke U8", "Jannowitzbrücke", "U8"),
            ("S42 Tempelhof ein Mann und eine Frau mit langen blonden Haaren.", "Tempelhof", "S42"),
            ("S41 tempelhof", "Tempelhof", "S41"),
            ("U6 Friedrichstrasse direction north, K.Schumacher platz, 3 mannlich gelesen mit B.O.B. jackets", "Friedrichstraße", "U6"),
            ("2 männer S42 Treptower park", "Treptower Park", "S42"),
            ("S41 in Storkowerstr Richtung Ostkreuz", "Storkower Straße", "S41"),
            ("2 civil controllis in s 41 to landsberger", None, "S41"),
            ("Three female kontrolettis in the S42 soon to be Bundesplatz", "Bundesplatz", "S42"),
            ("S45 Flughafen BER", "Flughafen BER", "S45"),
            ("Sind jetzt jungfeenheide. 1 x mal männlich und 1x mal weiblich gelesen komplett in schwarz", "Jungfernheide", None),
            ("S8 Ostkreuz", "Ostkreuz", "S8"),
            ("Controller in S7 Richtung Alexanderplatz Was just checked in jannowitzbrucke", "Jannowitzbrücke", "S7"),
            ("S42 Landsberger Alle, 2m, schwarze Jacke, schwarze Mütze. 2 m mit Gelber Weste begleiten.", "Landsberger Allee", "S42"),
            ("3 Kontrolleure s Greifswalder", "Greifswalder Straße", None),
            ("S8 Greifswalder Straße", "Greifswalder Straße", "S8"),
            ("S41 Ringbahn Landsberger allee big group of kontrolettis", "Landsberger Allee", "S41"),
            ("Ring 41-> Landsberger Allee, glaube mehrere männer die auch Minderjährige hochnehmen", "Landsberger Allee", "S41"),
            ("S42, 3x agressiv männlich, gerade Schönhauser ausgestiegen", "Schönhauser Allee", "S42"),
            ("Ring s42  approaching geundbrunnen civil control", "Gesundbrunnen", "S42"),
            ("5 Kontrolleure S8 to Birkenwerder", "Birkenwerder", "S8"),
            ("U8 heinrrich heinest blue vest at platform", "Heinrich-Heine-Straße", "U8"),
            ("Friedrichstraße", "Friedrichstraße", None),
            ("Spichernstraße U3 am Bahnsteig eine Person männl gelesen, komplett schwarz angezogen mit braunem undercut, ca 30 Jahre.. wirkt aber sehr nett weil er grad jemand erklärt wie er das Ticket einer anderen Person nachreichen kann", "Spichernstraße", "U3"),
            ("2x Blauwesten u8 Heinrich Heine straße Richtung Hermannstraße", "Heinrich-Heine-Straße", "U8"),
            ("Bitte hier keine Fragen, ob diese oder jene Linie gerade frei ist, sondern stattdessen die Suchfunktion (das Lupensymbol) nutzen. Danke! Nachricht gelöscht.", None, None),
            ("Two men wearing normal clothes in M5, checking tickets, just got off at alexanderplatz", "Alexanderplatz", None),
            ("U1 at hallesches tor towards warschauer str.  2 maybe 3 blue wests giving fines", "Hallesches Tor", "U1"),
            ("Wenn mein Infopost über die Demo am Sonntag Nachmittag gegen Rechts als Spam gewertet wird (über die ja auch im Bild der Gruppe informiert wird) würde ich mir eine kurze Rückmeldung von euch darüber wünschen", None, None),
            ("No basically this is the decision of the admins who run this group because we share certain values and leftist politics. If you happen to dislike actions against fascists, it's you who might not belong in this group. Like Spam.", None, None),
            ("S41 Treptower Park, 2 Männer", "Treptower Park", "S41"),
            ("U1 hallesches tor in der bahn richtung westen", "Hallesches Tor", "U1"),
            ("s7 nach Ahrensfelde 3 Männer schwarze jacken hackescher markt ausgestiegen", "Hackescher Markt", None),
            ("Ring S41 Sonnenallee Richtung Neukölln", "Sonnenallee", "S41"),
            ("U6 friedrichstr", "Friedrichstraße", "U6"),
            ("S42 two guys at frankfurterallee", "Frankfurter Allee", "S42"),
            ("Alexanderplatz an Gleis der u8 hellblaue westen", "Alexanderplatz", "U8"),
            ("4x männlich gelesen S42 aktuell Landsbegwr immer noch im Zug", "Landsberger Allee", "S42"),
            ("Alexanderplatz sbahn platform", "Alexanderplatz", None),
            ("41 wedding. Grun mantel", "Wedding", "S41"),
            ("Ostbahnhof 8 Bundesbullen stehen an der Bahnsteigkante. Alle mit gelben Westen. Keine Ahnung ob die eingestiegen sind.", "Ostbahnhof", None),
            ("Ostkreuz 6 Polizisten kontrollieren Ausweise willkürlich", "Ostkreuz", None),
            ("U6 Unter den Linden", "Unter den Linden", "U6"),
            ("unter den Linden, U6, Richtung Tegel, eine m gelesene Person mit blauer wrtse", "Unter den Linden", "U6"),
            ("U6 Richtung alt Mariendorf Stadtmitte eingestiegen 2 blauwesten m gelesen", "Stadtmitte", "U6"),
            ("U8 Hermannstr, just saw police + BVG going downstairs from the street", "Hermannstraße", "U8"),
            ("U8 Hermannstraße", "Hermannstraße", "U8"),
            ("S42 Hermanstraße , 2x schwarze Jacken", "Hermannstraße", "S42"),
            ("S25 S Hennigsdorf a least 2Pers.", "Hennigsdorf", "S25"),
            ("3 Blauwesten Ubhf Heinrich Heine Str", "Heinrich-Heine-Straße", None),
            ("U3 freie Universität stehen blau Westen. Sie werden wohl die nächste Bahn in die Innenstadt nehmen", "Freie Universität", "U3"),
            ("U8 rosenthaler Richtung hermanstr", "Rosenthaler Platz", "U8"),
            ("M27 Pankstr Richtung Jungfernheide", "Pankstraße", None),
            ("U2 From Alex to Ruhleben now bunch of them in a wagon", "Alexanderplatz", "U2"),
            ("3 mänlich gelesene 2 mit gelben westen 1 mit blauer bos weste alex u8 richtung wittenau", "Alexanderplatz", "U8"),
            ("About to get off s8 Prenzlauer Allee", "Prenzlauer Allee", "S8"),
            ("M29 two men, to Halensee", None, None),
            ("s47 nach spindlerfeld s tempelhof eingestiegen 2 in zivil", "Tempelhof", "S47"),
        ]

        for text, expected_station, expected_line in test_cases:
            with self.subTest(text=text):
                station = find_station(text)
                line = find_line(text, ubahn_lines + sbahn_lines)
                self.assertEqual(station, expected_station, f"Failed at '{text}': Expected station {expected_station}, found {station}")
                self.assertEqual(line, expected_line, f"Failed at '{text}': Expected line {expected_line}, found {line}")

if __name__ == '__main__':
    unittest.main()
    #print the percentage of passed tests
    total_tests = 0
    failed_tests = 0
    for test in unittest.TestResult().failures:
        total_tests += 1
        failed_tests += 1
    print(f'{round((100 - (failed_tests / total_tests) * 100), 2)}% of tests passed')