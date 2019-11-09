#from db import db
import pandas as pd

class CountryModel(): #db.Model if wanting to reactive creating a database table
#    __tablename__ = 'country'

#    id = db.Column(db.Integer, primary_key=True)
#    start_date = db.Column(db.String(80))
#    user_id = db.Column(db.String(80))
#    items = db.relationship('UserModel', lazy='dynamic')

    country_data = pd.read_csv('country_data.csv', usecols = ['COUNTRY', 'A2 (ISO)'])
    country_codes = list(country_data['A2 (ISO)'])
    countries = list(country_data['COUNTRY'])
    city_codes = pd.read_csv('IATA_codes_cities.csv', usecols = ['code'])['code']
    cities = pd.read_csv('IATA_codes_cities.csv', usecols = ['location'])['location']

    def __init__(self, username, country):
        self.username = username
        self.country = country

    @classmethod
    def country_name_to_code(cls, country):
        country_data = pd.read_csv('country_data.csv', usecols = ['COUNTRY', 'A2 (ISO)'])
        country_codes = list(country_data['A2 (ISO)'])
        countries = list(country_data['COUNTRY'])
        try:
            for ind, i in enumerate(countries):
                if i == country:
                    return(country_codes[ind])
        except:
            return {"message":"This country does not exisit."}, 404

    @classmethod
    def code_to_country_name(cls, country_code):
        country_data = pd.read_csv('country_data.csv', usecols = ['COUNTRY', 'A2 (ISO)'])
        country_codes = list(country_data['A2 (ISO)'])
        countries = list(country_data['COUNTRY'])
        try:
            for ind, i in enumerate(country_codes):
                if i == country_code:
                    return(countries[ind]), 200
        except:
            return {"message":"This country does not exisit."}, 404

    @classmethod
    def city_to_code(cls, city):
        city_codes = pd.read_csv('IATA_codes_cities.csv', usecols = ['code'])['code']
        cities = pd.read_csv('IATA_codes_cities.csv', usecols = ['location'])['location']
        for i in range(len(cities)):
            if city == cities[i]:
                return city_codes[i]

    @classmethod   
    def code_to_city(cls, city_code):
        city_codes = pd.read_csv('IATA_codes_cities.csv', usecols = ['code'])['code']
        cities = pd.read_csv('IATA_codes_cities.csv', usecols = ['location'])['location']
        for i in range(len(city_codes)):
            if city_code == city_codes[i]:
                return cities[i]        

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