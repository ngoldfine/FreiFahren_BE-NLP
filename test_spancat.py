from test_cases import test_cases
import json
from fuzzywuzzy import process
from NER.spancat import M2
from tabulate import tabulate
from NER.ner_lstm import M1
from main import extract_ticket_inspector_info

import warnings
warnings.filterwarnings("ignore")

for test in test_cases:
    message = test[0]
    station = test[1]
    line = test[2]
    direction = test[3]

   
    p_station_spancat = M2.getStation(message)
    p_direction_spancat = M2.getDirection(message)
    p_line_spancat = M2.getLine(message)

    p_station_ner = M1.get_one_station(message)
    p_line_ner = M1.get_line(message)

    p_info_fuzzy = extract_ticket_inspector_info(message)
    
    if p_info_fuzzy is None:
        p_station_fuzzy = None
        p_line_fuzzy = None
        p_direction_fuzzy = None
    else:
        p_station_fuzzy = p_info_fuzzy.get("station") 
        p_line_fuzzy = p_info_fuzzy.get("line") 
        p_direction_fuzzy = p_info_fuzzy.get("direction") 

    print(f"Test case: {message} ")
    table = []
    table.append(["Station", "Predicted Station (Spancat)", "Line", "Predicted Line (Spancat)", "Direction", "Predicted Direction (Spancat)"])
    table.append([station, p_station_spancat, line, p_line_spancat, direction, p_direction_spancat])

    print(tabulate(table, headers="firstrow", tablefmt="grid"))

    print("\n")

    table_ner = []
    table_ner.append(["Station (NER)", "Predicted Station (NER)", "Line (NER)", "Predicted Line (NER)"])
    table_ner.append([station, p_station_ner, line, p_line_ner])

    print(tabulate(table_ner, headers="firstrow", tablefmt="grid"))
    print("\n")

    table_fuzzy = []
    table_fuzzy.append(["Station ", "Predicted Station (Fuzzy)", "Line ", "Predicted Line (Fuzzy)", "Direction ", "Predicted Direction (Fuzzy)"])
    table_fuzzy.append([station, p_station_fuzzy, line, p_line_fuzzy, direction, p_direction_fuzzy])

    print(tabulate(table_fuzzy, headers="firstrow", tablefmt="grid"))


    print("\n\n\n\n")

