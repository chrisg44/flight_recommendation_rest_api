from db import db
from datetime import date, timedelta, datetime
from amadeus import Client, ResponseError

amadeus = Client(
    client_id='GtVckBnXbACgukKbMhIrJ7yLeyd1WcEy',
    client_secret='4aKrJf3wdi97vAFe'
)

class CheapestModel(db.Model):
    __tablename__ = 'cheapest'

    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.String(80))
    end_date = db.Column(db.String(80))
    origin = db.Column(db.String(80))
    destination = db.Column(db.String(80))
    # items = db.relationship('ItemModel', lazy='dynamic')  - Not required

    def __init__(self, start_date = None, end_date = None, depart_date = None, return_date=None, origin=None, destination=None): 
        self.start_date = start_date
        self.end_date = end_date
        self.depart_date = depart_date
        self.return_date = return_date
        self.origin = origin
        self.destination = destination
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def find_cheapest_single_range(self, start_date, end_date, origin, destination):
        cheapest = CheapestModel(start_date = start_date, end_date = end_date, origin = origin, destination = destination)
        sdate = datetime.strptime(cheapest.start_date, '%Y-%m-%d')   # start date
        edate = datetime.strptime(cheapest.end_date, '%Y-%m-%d')  # end date
        delta = edate - sdate       # as timedelta
        date_list = []
        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            date_list.append(str(day.date()))
        response = []
        error=None
        for date in date_list:
            try:
                single_response = amadeus.shopping.flight_offers.get(origin=cheapest.origin, destination=cheapest.destination, departureDate=date).data
            except Exception as err:
                error = err 
                return
            response += single_response  
        prices = []
        for i in range(len(response)):
            prices.append(float(response[i]['offerItems'][0]['price']['total']))  
        min_price_index = prices.index(min(prices))

        if error != None:
            return {'message': "An error has occured. '{}' .".format(error)}, 400
        else:
            return {'price':prices[min_price_index]}

    @classmethod
    def find_cheapest_return_specific(cls, depart_date, return_date, origin, destination):
        data_object = CheapestModel(depart_date = depart_date, return_date = return_date, origin = origin, destination = destination)
        error=None
        try:
            response = amadeus.shopping.flight_offers.get(origin=data_object.origin, destination=data_object.destination, departureDate=data_object.depart_date, returnDate=data_object.return_date).data
        except Exception as err:
            error = err 
        prices = []
        for i in range(len(response)):
            prices.append(float(response[i]['offerItems'][0]['price']['total']))  
        min_price_index = prices.index(min(prices))

        if error != None:
            return {'message': "An error has occured. '{}' .".format(error)}, 400
        else:
            return {'price':prices[min_price_index], 'full_data': response[min_price_index]} 

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