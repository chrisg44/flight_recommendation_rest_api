from db import db
from datetime import date, timedelta, datetime
from models.cheapest import CheapestModel
from models.user import UserModel
from models.country import CountryModel
from models.ratings import RatingModel
import pandas as pd
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re
from amadeus import Client, ResponseError

amadeus = Client(
    client_id='GtVckBnXbACgukKbMhIrJ7yLeyd1WcEy',
    client_secret='4aKrJf3wdi97vAFe'
)

google_api_key = 'AIzaSyCu0V_tOd96ibeXE62Y1ENTOvQ8PeR_rHM'

class VisitNewModel(db.Model):
    __tablename__ = 'visit_new_country'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    depart_date = db.Column(db.String(80))
    return_date = db.Column(db.String(80))
    location = db.Column(db.String(80))
    countries_visited = db.Column(db.String(1000))
    # items = db.relationship('ItemModel', lazy='dynamic')  - Not required

    def __init__(self, username, depart_date, return_date, location, visited, preference, top):
        self.username = username
        self.depart_date = depart_date
        self.return_date = return_date
        self.location = location
        self.visited = visited
        self.preference = preference
        self.top = top
        db.session.add(self)
        db.session.commit()
    


    @classmethod
    def visit_new_country(cls, depart_date, return_date, visited, location):
        
        depart_airport_code, depart_city_code, poss_destinations = cls.destinations(location)
        poss_destinations['country_codes'] = None
        for i in range(len(poss_destinations)):
            poss_destinations['country_codes'][i] = CountryModel.country_name_to_code(poss_destinations['countries'][i])
        #poss_destinations = poss_destinations[~poss_destinations['country_codes'].isin(visited)]
        poss_destinations['flight_times_hours'] = poss_destinations['flight_times_hours'].astype(int, copy=False)
        
        trip_duration = (datetime.strptime(return_date, '%Y-%m-%d') - datetime.strptime(depart_date, '%Y-%m-%d')).days
        
        short_long_split = 6 # the length of flight making it short or long haul
        short_long_trip = 6 # the length of trip making it a short or long trip
        
        if trip_duration < short_long_trip:
            poss_destinations = poss_destinations[poss_destinations['flight_times_hours'] < short_long_split]
            
        return depart_airport_code, depart_city_code, poss_destinations

    @classmethod
    def destinations(cls, location):

            response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(location, google_api_key))
            resp_json_payload = response.json()
            longitude = resp_json_payload['results'][0]['geometry']['location']['lng']
            latitude = resp_json_payload['results'][0]['geometry']['location']['lat']

            response = amadeus.reference_data.locations.airports.get(longitude=longitude, latitude=latitude, radius = 150).data

            airport_code = response[0]['iataCode']
            city_code = response[0]['address']['cityCode']

            url = 'https://www.flightsfrom.com/'+airport_code+'/destinations'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.findAll('li')

            countries = []
            airport_codes = []
            cities = []
            flight_times = []
            flight_times_hours = []
            for i in range(len(content)):
                countries.append(content[i]['data-country'])
                airport_codes.append(content[i]['data-iata'])
                cities.append(content[i]['data-name'])
                flight_times.append(re.split("\n", content[i].text)[9])
                flight_times_hours.append(re.split("h", re.split("\n", content[i].text)[9])[0][1:])
            dataframe = pd.DataFrame({'countries':countries,'airport_codes':airport_codes, 'cities':cities,'flight_times':flight_times, 'flight_times_hours':flight_times_hours})
            return airport_code, city_code, dataframe

    @classmethod
    def visit_most_popular(cls, depart_date, return_date, visited, location, top):
        depart_airport_code, depart_city_code, possible_countries = cls.visit_new_country(depart_date, return_date, visited, location)
        popular_destinations = RatingModel.most_common_destinations(depart_city_code)
        popular_not_visited = possible_countries[possible_countries['cities'].isin(list(popular_destinations['destination']))]
        prices = []
        full_data = []
        destinations = []
        for i in popular_not_visited['airport_codes'][:int(top)]:
            data = CheapestModel.find_cheapest_return_specific(depart_date, return_date, depart_airport_code, i)
            prices.append(data['price'])
            full_data.append(data['full_data'])
            destinations.append(data['full_data']['offerItems'][0]['services'][0]['segments'][0]['flightSegment']['arrival']['iataCode'])
            
        return prices, destinations, full_data
    
    @classmethod  
    def visit_best_party(cls, depart_date, return_date, visited, location, top):
        depart_airport_code, depart_city_code, possible_countries = cls.visit_new_country(depart_date, return_date, visited, location)
        best_party_cities_list = RatingModel.best_party_cities()
        party_not_visited = possible_countries[possible_countries['cities'].isin(list(best_party_cities_list['cities']))]
        prices = []
        full_data = []
        destinations = []
        for i in party_not_visited['airport_codes'][:int(top)]:
            data = CheapestModel.find_cheapest_return_specific(depart_date, return_date, depart_airport_code, i)
            prices.append(data['price'])
            full_data.append(data['full_data'])
            destinations.append(data['full_data']['offerItems'][0]['services'][0]['segments'][-1]['flightSegment']['arrival']['iataCode'])

        return prices, destinations, full_data


    @classmethod
    def visit_best_food(cls, depart_date, return_date, visited, location, top):
        depart_airport_code, depart_city_code, possible_countries = cls.visit_new_country(depart_date, return_date, visited, location)
        best_food_cities_list = RatingModel.best_food_cities()
        food_not_visited = possible_countries[possible_countries['cities'].isin(list(best_food_cities_list['city']))]
        prices = []
        full_data = []
        destinations = []
        for i in food_not_visited['airport_codes'][:int(top)]:
            data = CheapestModel.find_cheapest_return_specific(depart_date, return_date, depart_airport_code, i)
            prices.append(data['price'])
            full_data.append(data['full_data'])
            destinations.append(data['full_data']['offerItems'][0]['services'][0]['segments'][0]['flightSegment']['arrival']['iataCode'])

        return prices, destinations, full_data 


    @classmethod
    def countries_visted(cls, username):
        user = UserModel.find_by_username(username)
        visited = []
        country_data = pd.read_csv('country_data.csv', usecols = ['COUNTRY', 'A2 (ISO)'])
        country_codes = list(country_data['A2 (ISO)'])
        #WARNING Indonesia ISO code ID is renamed IA
        visited.append(user.AF)
        visited.append(user.AL)
        visited.append(user.DZ)
        visited.append(user.AS)
        visited.append(user.AD)
        visited.append(user.AO)
        visited.append(user.AI)
        visited.append(user.AQ)
        visited.append(user.AG)
        visited.append(user.AR)
        visited.append(user.AM)
        visited.append(user.AW)
        visited.append(user.AU)
        visited.append(user.AT)
        visited.append(user.AZ)
        visited.append(user.BS)
        visited.append(user.BH)
        visited.append(user.BD)
        visited.append(user.BB)
        visited.append(user.BY)
        visited.append(user.BE)
        visited.append(user.BZ)
        visited.append(user.BJ)
        visited.append(user.BM)
        visited.append(user.BT)
        visited.append(user.BO)
        visited.append(user.BQ)
        visited.append(user.BA)
        visited.append(user.BW)
        visited.append(user.BV)
        visited.append(user.BR)
        visited.append(user.IO)
        visited.append(user.BN)
        visited.append(user.BG)
        visited.append(user.BF)
        visited.append(user.BI)
        visited.append(user.KH)
        visited.append(user.CM)
        visited.append(user.CA)
        visited.append(user.CV)
        visited.append(user.KY)
        visited.append(user.CF)
        visited.append(user.TD)
        visited.append(user.CL)
        visited.append(user.CN)
        visited.append(user.CX)
        visited.append(user.CC)
        visited.append(user.CO)
        visited.append(user.KM)
        visited.append(user.CG)
        visited.append(user.CD)
        visited.append(user.CK)
        visited.append(user.CR)
        visited.append(user.HR)
        visited.append(user.CU)
        visited.append(user.CW)
        visited.append(user.CY)
        visited.append(user.CZ)
        visited.append(user.CI)
        visited.append(user.DK)
        visited.append(user.DJ)
        visited.append(user.DM)
        visited.append(user.DO)
        visited.append(user.EC)
        visited.append(user.EG)
        visited.append(user.SV)
        visited.append(user.GQ)
        visited.append(user.ER)
        visited.append(user.EE)
        visited.append(user.ET)
        visited.append(user.FK)
        visited.append(user.FO)
        visited.append(user.FJ)
        visited.append(user.FI)
        visited.append(user.FR)
        visited.append(user.GF)
        visited.append(user.PF)
        visited.append(user.TF)
        visited.append(user.GA)
        visited.append(user.GM)
        visited.append(user.GE)
        visited.append(user.DE)
        visited.append(user.GH)
        visited.append(user.GI)
        visited.append(user.GR)
        visited.append(user.GL)
        visited.append(user.GD)
        visited.append(user.GP)
        visited.append(user.GU)
        visited.append(user.GT)
        visited.append(user.GG)
        visited.append(user.GN)
        visited.append(user.GW)
        visited.append(user.GY)
        visited.append(user.HT)
        visited.append(user.HM)
        visited.append(user.VA)
        visited.append(user.HN)
        visited.append(user.HK)
        visited.append(user.HU)
        visited.append(user.IS)
        visited.append(user.IN)
        visited.append(user.IA)
        visited.append(user.IR)
        visited.append(user.IQ)
        visited.append(user.IE)
        visited.append(user.IM)
        visited.append(user.IL)
        visited.append(user.IT)
        visited.append(user.JM)
        visited.append(user.JP)
        visited.append(user.JE)
        visited.append(user.JO)
        visited.append(user.KZ)
        visited.append(user.KE)
        visited.append(user.KI)
        visited.append(user.KP)
        visited.append(user.KR)
        visited.append(user.KW)
        visited.append(user.KG)
        visited.append(user.LA)
        visited.append(user.LV)
        visited.append(user.LB)
        visited.append(user.LS)
        visited.append(user.LR)
        visited.append(user.LY)
        visited.append(user.LI)
        visited.append(user.LT)
        visited.append(user.LU)
        visited.append(user.MO)
        visited.append(user.MK)
        visited.append(user.MG)
        visited.append(user.MW)
        visited.append(user.MY)
        visited.append(user.MV)
        visited.append(user.ML)
        visited.append(user.MT)
        visited.append(user.MH)
        visited.append(user.MQ)
        visited.append(user.MR)
        visited.append(user.MU)
        visited.append(user.YT)
        visited.append(user.MX)
        visited.append(user.FM)
        visited.append(user.MD)
        visited.append(user.MC)
        visited.append(user.MN)
        visited.append(user.ME)
        visited.append(user.MS)
        visited.append(user.MA)
        visited.append(user.MZ)
        visited.append(user.MM)
        visited.append(user.NA)
        visited.append(user.NR)
        visited.append(user.NP)
        visited.append(user.NL)
        visited.append(user.NC)
        visited.append(user.NZ)
        visited.append(user.NI)
        visited.append(user.NE)
        visited.append(user.NG)
        visited.append(user.NU)
        visited.append(user.NF)
        visited.append(user.MP)
        visited.append(user.NO)
        visited.append(user.OM)
        visited.append(user.PK)
        visited.append(user.PW)
        visited.append(user.PS)
        visited.append(user.PA)
        visited.append(user.PG)
        visited.append(user.PY)
        visited.append(user.PE)
        visited.append(user.PH)
        visited.append(user.PN)
        visited.append(user.PL)
        visited.append(user.PT)
        visited.append(user.PR)
        visited.append(user.QA)
        visited.append(user.RO)
        visited.append(user.RU)
        visited.append(user.RW)
        visited.append(user.RE)
        visited.append(user.BL)
        visited.append(user.SH)
        visited.append(user.KN)
        visited.append(user.LC)
        visited.append(user.MF)
        visited.append(user.PM)
        visited.append(user.VC)
        visited.append(user.WS)
        visited.append(user.SM)
        visited.append(user.ST)
        visited.append(user.SA)
        visited.append(user.SN)
        visited.append(user.RS)
        visited.append(user.SC)
        visited.append(user.SL)
        visited.append(user.SG)
        visited.append(user.SX)
        visited.append(user.SK)
        visited.append(user.SI)
        visited.append(user.SB)
        visited.append(user.SO)
        visited.append(user.ZA)
        visited.append(user.GS)
        visited.append(user.SS)
        visited.append(user.ES)
        visited.append(user.LK)
        visited.append(user.SD)
        visited.append(user.SR)
        visited.append(user.SJ)
        visited.append(user.SZ)
        visited.append(user.SE)
        visited.append(user.CH)
        visited.append(user.SY)
        visited.append(user.TW)
        visited.append(user.TJ)
        visited.append(user.TZ)
        visited.append(user.TH)
        visited.append(user.TL)
        visited.append(user.TG)
        visited.append(user.TK)
        visited.append(user.TO)
        visited.append(user.TT)
        visited.append(user.TN)
        visited.append(user.TR)
        visited.append(user.TM)
        visited.append(user.TC)
        visited.append(user.TV)
        visited.append(user.UG)
        visited.append(user.UA)
        visited.append(user.AE)
        visited.append(user.GB)
        visited.append(user.US)
        visited.append(user.UM)
        visited.append(user.UY)
        visited.append(user.UZ)
        visited.append(user.VU)
        visited.append(user.VE)
        visited.append(user.VN)
        visited.append(user.VG)
        visited.append(user.VI)
        visited.append(user.WF)
        visited.append(user.EH)
        visited.append(user.YE)
        visited.append(user.ZM)
        visited.append(user.ZW)

        visited_codes = []
        for ind, i in enumerate(visited):
            if i == '1':
                visited_codes.append(country_codes[ind])

        return visited_codes

    '''def json(self):
        return {'start_date': self.start_date, 'end_date': self.end_date, ''}

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()''' 