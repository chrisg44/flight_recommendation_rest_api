from flask_restful import Resource, reqparse
from models.country import CountryModel
from models.user import UserModel


class CountryAdd(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help="You need to be logged in."
    )
    parser.add_argument('country',
        type=str,
        required=True,
        help="A country is required!"
    )


    def put(self):

        data = CountryAdd.parser.parse_args()
        country_add = CountryModel(data['username'], data['country'])
        user = UserModel.find_by_username(country_add.username)

        if user is None:
           return {"message": "The user does not exist, please make sure you have logged in or are registered."}, 400
        else:
            setattr(user, country_add.country, 1)

        user.save_to_db()

        return {"message": '{} has been succesfully added.'.format(country_add.country)}
        




