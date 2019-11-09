#from db import db
import pandas as pd
from models.country import CountryModel
from amadeus import Client, ResponseError
import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re

amadeus = Client(
    client_id='GtVckBnXbACgukKbMhIrJ7yLeyd1WcEy',
    client_secret='4aKrJf3wdi97vAFe'
)

class RatingModel(): #db.Model if wanting to reactive creating a database table
#    __tablename__ = 'country'

#    id = db.Column(db.Integer, primary_key=True)
#    start_date = db.Column(db.String(80))
#    user_id = db.Column(db.String(80))
#    items = db.relationship('UserModel', lazy='dynamic')


    def __init__(self):
        pass

    @classmethod
    def best_food_cities(cls):
        try:
            return pd.read_csv('best_food_cities.csv', usecols = ['city','country','score'])
        except:
            url = 'https://www.loveexploring.com/gallerylist/69944/the-50-best-food-cities'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.findAll('h2')
            food_city = []
            food_country = []
            score = []

            for i in range(len(content)-1):
                score.append(100-i*2)
                food_city.append(re.split(">", re.split(">", content[(len(content)-1-i)].text)[0].split(',')[0])[0].split('.')[1][1:])
                try:
                    food_country.append(re.split(">", re.split(">", content[(len(content)-1-i)].text)[0].split(',')[1])[0][1:])
                except:
                    food_country.append(re.split(">", re.split(">", content[(len(content)-1-i)].text)[0].split(',')[0])[0].split('.')[1][1:])
            data = pd.DataFrame({'city':food_city,'country': food_country,'score': score})
            data.to_csv('best_food_cities.csv')
            return data


    @classmethod
    def best_nightlife_cities(cls):
        try:
            return pd.read_csv('best_nightlife_cities.csv')
        except:
            url = 'http://www.thrillophilia.com/blog/greatest-cities-in-the-world-to-party/'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.findAll('h3')
            cities = []
            scores = []
            for i in range(len(content)-2):
                scores.append(round(100 - i*(100/len(content))))
                cities.append(re.split(">", content[i].text)[0])
            data = pd.DataFrame({'cities':cities, 'scores':scores})
            data.to_csv('best_nightlife_cities.csv')
            return data

    def most_common_destinations(depart_city_code):
        data = amadeus.travel.analytics.air_traffic.traveled.get(originCityCode=depart_city_code, period='2017-07', max=50, page=50).data
        destination = []
        destination_code = []
        score = []
        for i in range(len(data)):
            destination.append(CountryModel.code_to_city(data[i]['destination']))
            destination_code.append(data[i]['destination'])
            score.append((data[i]['analytics']['flights']['score'] + data[i]['analytics']['travelers']['score'])/2)
        return pd.DataFrame({'destination': destination, 'destination_code': destination_code, 'score': score})

    '''def json(self):
        return {'start_date': self.start_date, 'end_date': self.end_date, ''}

    @classmethod
    def find_by_name(cls):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()'''