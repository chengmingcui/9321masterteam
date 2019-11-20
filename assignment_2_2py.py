import json
import jwt
import datetime

import pandas as pd
from flask import Flask
from flask import request
from flask_restplus import Resource, Api
from flask_restplus import fields,abort
from flask_restplus import inputs
from flask_restplus import reqparse

# assume the dataset which API is going to access is named mel_data.csv

# the API has two operations get and post for houses_price/id
# the API has get list of house_prices
app = Flask(__name__)
api = Api(app,
        authorizations= {"Token-Based":{
                                "type":"apiKey",
                                "name":"API-TOKEN",
                                "in":"header"
                            }
          },
          security = "Token-Based",
          default= "Houses", # the namespace
          title = "Melbourne House price dataset" ,# the documentation title
          description = "This API aims to predict the house price in Melbourne Australia. Once you provide some details about your house, a predict price of your"
                        +"house would be provided to you immediately !",
          version = "1.0"
          )

# the temporary model, not the final one, since I don't know yet what details of a house, the house owner has to provide.
house_model = api.model('House',{
    "Identifier" : fields.Integer,
    "Address" : fields.String,
    "Rooms" : fields.Integer,
    "Type": fields.String,
    "Date": fields.Date,
    "Distance": fields.Float,
    "Postcode": fields.String,
    "Bedroom": fields.Integer,
    "Bathroom": fields.Integer,
    "Land size": fields.Float,
    "Build Area": fields.Integer,
    "Region Name": fields.String,
    "User": fields.String,
    "Password":fields.String
})

parser = reqparse.RequestParser() # initialize a request parser
#use query parameters to pass username and password
parser.add_argument('User') # python3 中默认的类型是字符串
parser.add_argument('Password')
order_list = ["Date","Build Area","Distance"]
parser.add_argument('order', choices=order_list)
parser.add_argument('ascending', type=inputs.boolean)
auth_parser = reqparse.RequestParser()
auth_parser.add_argument('username', required = True)
auth_parser.add_argument('password', required = True)
SECRET_KEY = "jalsdncoih2o342oisdcnvsl290384cvkjwmenzoxi2361298smndclzcse"
def requires_auth(f):
    def decorated(*args, **kwargs):
        token = request.headers.get("API-TOKEN")
        if not token:
            abort(401,'Authentication token is missing')
        try:
            jwt.decode(token,SECRET_KEY)
        except Exception as e:
            abort(401,message=e)

        return f(*args, **kwargs)
    return decorated

@api.route('/authentication-tokens')
class Authentication(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Generates a authentication token")
    @api.expect(auth_parser,validate=True)
    def post(self):
        args = auth_parser.parse_args()
        if not args:
            abort(400,message="username and password needed")
        username = args.get("username")
        password = args.get("password")
        if username in df["User"]:
            user_info = df.loc('df["user"] == @username')
            if password == user_info["password"]:
                payload = {
                    "username":username,
                    "role":"admin",
                    "exp" : datetime.datetime.utcnow() + datetime.timedelta(seconds= 60)
                }

                token = jwt.encode(payload,SECRET_KEY)
                return token
            else:
                abort(400,message="password is not correct")
        else:
            abort(400,message="username is not registered")

@api.route('/houses')
class HousesList(Resource):
    @api.response(200, 'Successful')
    @api.response(400, 'Validation Error')
    @api.doc(description="Get all house list that a user predicted")
    @requires_auth
    def get(self):
        # get houses as JSON string
        args =parser.parse_args()

        order_by = args.get('order')
        ascending = args.get('ascending', False)
        user = args.get('User')
        pw = args.get('Password')
        if user in df["User"]:
            user_info = df.loc('df["user"] == @username')
            if user_info["Password"] != pw:
                return {"message": "password is not right"},400
        else:
            return {"message": "user is not found"},400

        user_house = df.query('User == @user')

        if order_by:
            user_house.sort_values(by=order_by,inplace=True, ascending=ascending)

        json_str = user_house.to_json(orient='index')

        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            house = {}
            id = int(idx)
            house['Identifier'] = id
            house["Type"] = df.loc(id,"type")
            house["Area"] = df.loc(id,"Region Name")
            house["Date"] = df.loc(id,"Date")
            house["Distance"] = df.loc(id,"Distance")
            ret.append(house)
        return ret



@api.route("houses/<int:id>")
@api.param("id", "The house identifier")
class Houses(Resource):

    @api.response(201," Success: A new house is posted successfully")
    @api.response(401, "Error: Invalidation post")
    @api.doc(description = "Add a new house information into dataset")
    @api.expect(house_model,validate = True)
    @requires_auth
    def post(self):
        # for user to provide  a new house and its details into dataset
        house = request.json # the content that post request provide

        if "Identifier" not in house:
            return {"message": "Identifier must be provided, thank you."}, 401

        id = house["Identifier"] #id is the Identifier of the house which a user just post

        #check the Identifier wether already exist
        if id in df.index:
            return {"message": "Sorry, A house with identifier {} is already exist, please create a new identifier.".format(id)}, 401

        #put the value into the dataset
        for key in house:
            if key not in house_model.keys():
                # unexpected features
                return {"message": "Property {} is invalid.".format(str(key))}, 401
            df.loc[id,key] = house[key]
        return {"message": "Your house information is submitted."}, 201

    @api.reponse(403,"Error: User has not permission to access a house information")
    @api.response(401,"Error: House information invalid")
    @api.response(200," Success: House information update successfully")
    @api.doc(description = " Update information of a house by its Identifier")
    @api.expect(house_model)
    @requires_auth
    def put(self,id):

        args = parser.parse_args()

        user = args.get("User")
        password = args.get("Password")

        if id not in df.index:
            api.abort(402, "House with id {} is not exist.".format(id))

        house = request.json #covert the request to json

        if "Identifier" in house and (user != house["User"] or password != house["Password"]):
            return {"message": "Sorry, you has no right to access house {}".format(id)}, 403

        if "Identifier" in house and id != house["Identifier"]:
            return {"message": "House Identifier cannot be changed."}, 401

        #Update the house information
        for key in house:
            if key not in house_model.keys():
                return {"message": "Property {} is invalid.".format(str(key))}, 401
            df.loc[id,key] = house[key]

        return {"message":"House {} has been updated successfully.".format(id)}, 200

    @api.reponse(403, "Error: User has not permission to access a house information")
    @api.response(402," Error: Invalid House Identifier")
    @api.response(200, "Success: House information delete successfully")
    @api.doc(description = "Delete a house and its information from dataset")
    @requires_auth
    def delete(self,id):

        args = parser.parse_args()

        user = args.get("User")
        password = args.get("Password")

        if id not in df.index:
            api.abort(402, "House with id {} is not exist".format(id) )

        if df.loc[id,"User"] != user or df.loc[id,"Password"] != password:
            return {"message":"Sorry, you has no right to access house {}".format(id)}, 403

        #delete the house from dataset
        df.drop(id, inplace = True)
        return {"message":" House {} has been deleted successfully".format(id)}, 200





if __name__ =="__main__":
    csv_file = "mel_data.csv" # the csv file is temporary decided, I think we need three dataset, one is for training , one for testing,
    #but another one must be the user can access and to post and get information.
    # 我觉得这个user access dataset， 必须要求提供user的ID 和password， 然后dataset 里面也要有column的名字就做provider, 和一列password，
    #因为user虽然可以access 这个dataset， 但是只能delete 他自己的houses的information, update , 看自己的house的predicted price。 所以每个house
    #需要记录user的ID和password。
    df = pd.read_csv (csv_file)
    Identifier = []
    for index, row in df.iterrows():
        Identifier.append(int(index))

    df.insert(0,"Identifier", Identifier,)
    for index, row in df.iterrows():
        print(row["Identifier"])

    df.set_index("Identifier", inplace = True)

    app.run(debug = True)
