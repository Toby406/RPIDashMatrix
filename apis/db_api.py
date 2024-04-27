from datetime import datetime, timezone
from pyhafas import HafasClient
from pyhafas.profile import DBProfile

client = HafasClient(DBProfile())

# print(client.locations("Lebibniz Universität Hannover"))

#UNi 636314
#HMarkt 636217

departures = client.departures(station='636217', date=datetime.now(), max_trips=5)

for dep in departures:
    print(dep)

def get_next_departure():
    journeys = client.journeys(636217, 636314, datetime.now())

    i = 1;
    journey = client.journey(journeys[0].id)
    #if depature was in the past get next one
    while journey.legs[0].departure < datetime.now(timezone.utc):
        journey = client.journey(journeys[i].id)
        i += 1
   
    
    abfahrt = journey.legs[0].departure
    print(journey.legs[0].departure)

    # time_until_departure = abfahrt - datetime.now(timezone.utc)

    return abfahrt
