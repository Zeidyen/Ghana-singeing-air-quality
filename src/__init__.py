# makes src a package
from dataclasses import dataclass

# Sites in your study (edit if needed)
SITES = ["Tulaku", "James Town", "Amasaman", "Avernor"]

# Morning/Afternoon/Evening within 06:00–18:00 window
PERIOD_BOUNDS = [
    ("morning",   6, 10),
    ("afternoon",10, 14),
    ("evening",  14, 18),
]

TZ = "Africa/Accra"

POLLUTANTS = ["PM25", "PM10", "CO", "SO2", "VOCs"]
CLIMATE    = ["AT", "RH"]
