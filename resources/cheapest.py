from flask_restful import Resource, reqparse
from models.cheapest import CheapestModel
from datetime import date, timedelta, datetime
from amadeus import Client, ResponseError

amadeus = Client(
    client_id='GtVckBnXbACgukKbMhIrJ7yLeyd1WcEy',
    client_secret='4aKrJf3wdi97vAFe'
)

class Cheapest(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('start_date',
#        type=datetime,
        required=True,
        help="A start date is required!"
    )
    parser.add_argument('end_date',
#        type=int,
        required=True,
        help="An end date is required."
    )
    parser.add_argument('origin',
        type=str,
        required=True,
        help="An origin is required!"
    )
    parser.add_argument('destination',
        type=str,
        required=True,
        help="A destination is required."
    )

    def post(self):
        data = Cheapest.parser.parse_args()
        cheapest = CheapestModel.find_cheapest_single_range(**data)
        return cheapest

        




