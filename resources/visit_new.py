from flask_restful import Resource, reqparse
from models.user import UserModel
from models.cheapest import CheapestModel
from models.visit_new import VisitNewModel
from datetime import date, timedelta, datetime
from amadeus import Client, ResponseError
import json

amadeus = Client(
    client_id='GtVckBnXbACgukKbMhIrJ7yLeyd1WcEy',
    client_secret='4aKrJf3wdi97vAFe'
)

class VisitNew(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
#        type=int,
        required=True,
        help="An username is required."
    )
    parser.add_argument('depart_date',
#        type=datetime,
        required=True,
        help="A departure date is required!"
    )
    parser.add_argument('return_date',
#        type=int,
        required=True,
        help="An return date is required."
    )
    parser.add_argument('location',
#        type=int,
        required=True,
        help="Your departure location is required."
    )
    parser.add_argument('preference',
#        type=int,
        required=True,
        help="Your prefered destination type is required."
    )
    parser.add_argument('top',
#        type=int,
        required=True,
        help="The number of results is requested is required."
    )

    def post(self):
        data = VisitNew.parser.parse_args()

        user = UserModel.find_by_username(data['username'])
        visited = VisitNewModel.countries_visted(user.username)
        visit_new_object = VisitNewModel(data['username'], data['depart_date'], data['return_date'], data['location'], visited, data['preference'], data['top'])
        
        if visit_new_object.preference == 'None':
            depart_airport_code, depart_city_code, poss_destinations = VisitNewModel.visit_new_country(visit_new_object.depart_date, visit_new_object.return_date, visit_new_object.visited, visit_new_object.location, visit_new_object.top)
            return {"message":list(poss_destinations['countries'])[:10]}

        if visit_new_object.preference == 'popular':
            prices, destinations, full_data = VisitNewModel.visit_most_popular(visit_new_object.depart_date, visit_new_object.return_date, visit_new_object.visited, visit_new_object.location, visit_new_object.top)
            return {"destinations":destinations, "prices": prices}

        if visit_new_object.preference == 'food':
            prices, destinations, full_data = VisitNewModel.visit_best_food(visit_new_object.depart_date, visit_new_object.return_date, visit_new_object.visited, visit_new_object.location, visit_new_object.top)
            return {"destinations":destinations, "prices": prices}

        if visit_new_object.preference == 'nightlife':
            prices, destinations, full_data = VisitNewModel.visit_best_nightlife(visit_new_object.depart_date, visit_new_object.return_date, visit_new_object.visited, visit_new_object.location, visit_new_object.top)
            return {"destinations":destinations, "prices": prices}

        if visit_new_object.preference == 'description':
            prices, destinations, full_data = VisitNewModel.visit_best_party(visit_new_object.depart_date, visit_new_object.return_date, visit_new_object.visited, visit_new_object.location, visit_new_object.top)
            return {"destinations":destinations, "prices": prices}
        
        else:
            return {"message":"Preference incorrectly set"}



        '''data = Cheapest.parser.parse_args()
        vist = VisitNewCountryModel.find_cheapest(**data)
        return cheapest'''


        ''' Steps:
        Get countries already visited
        Identify countries that can be visited
        Get prices for dates
        Build in logic (less than 10days shorthaul, less than 5 days very short haul)

        '''



        




