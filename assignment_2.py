import json
import ujson
import jwt
import datetime
import re
import time

import pandas as pd
from flask import Flask
from flask import request
from flask_restplus import Resource, Api
from flask_restplus import fields, abort
from flask_restplus import inputs
from flask_restplus import reqparse
import machine_learning as ml
import Data_for_graph as dg
from flask import redirect
# assume the dataset which API is going to access is named mel_data.csv

# the API has two operations get and post for houses_price/id
# the API has get list of house_prices
app = Flask(__name__,static_url_path="/")
api = Api(
    app,
    doc="/api",
    default_label="api",
    prefix="/api",
          authorizations={"Token-Based": {
              "type": "apiKey",
              "name": "API-TOKEN",
              "in": "header"
          }
          },
          security="Token-Based",
          default="Houses",  # the namespace
          title="Melbourne House price dataset",  # the documentation title
          description="This API aims to predict the house price in Melbourne Australia.\n Once you provide some details about your house, a predict price of your"
                      + "house would be provided to you immediately !",
          version="1.0"
          )

# different with the test dataset schema, where it adds columns "Identifier", "User" and "Password"
# those three columns values do not contribute to predict price.
house_model = api.model('House', {
    "Identifier": fields.Integer,
    "UserID": fields.Integer,
    "Distance": fields.Float,
    "Bedroom": fields.Float,
    "Bathroom": fields.Float,
    "Car": fields.Float,
    "Landsize": fields.Float,
    "BuildingArea": fields.Float,
    "YearBuilt": fields.Float,
    "Lattitude": fields.Float,
    "Longtitude": fields.Float,
    "Suburb": fields.String,  # 这些flag开头的fields,都需要用户选择
    "Street": fields.String,
    "Type": fields.String,
    "Regionname": fields.String

})

user_model = api.model("User", {
    "Username": fields.String,
    "Password": fields.String
})

auth_parser = reqparse.RequestParser()
auth_parser.add_argument('username', required=True)
auth_parser.add_argument('password', required=True)
SECRET_KEY = "jalsdncoih2o342oisdcnvsl290384cvkjwmenzoxi2361298smndclzcse"


def requires_auth(f):
    def decorated(*args, **kwargs):
        token = request.headers.get("API-TOKEN")
        if not token:
            abort(401, 'Authentication token is missing')
        try:
            ujson.dumps(jwt.decode(token, SECRET_KEY))
        except Exception as e:
            abort(401, message=e)

        return f(*args, **kwargs)

    return decorated


@api.route('/authentication-tokens')
class Authentication(Resource):
    @api.response(200, 'Successful')
    @api.doc(description="Generates a authentication token")
    @api.expect(auth_parser, validate=True)
    def post(self):
        df_log = pd.read_csv("log_file.csv",usecols=["ID","UserID", "Operation", "Time"])
        df_log.set_index(["ID"], inplace = True)
        print(df_log.to_string())
        get_time = time.asctime(time.localtime(time.time()))
        df_user = pd.read_csv("user_accounts.csv", usecols=["UserID", "Username", "Password"])
        df_user.set_index(["UserID"], inplace=True)

        args = auth_parser.parse_args()
        # user_data = pd.read_csv("user_accounts.csv", usecols=["UserID", "Username", "Password"])
        if not args:
            abort(400, message="username and password needed")
        username = args.get("username")
        password = args.get("password")

        print(df_user["Username"])
        print(username)
        if username in df_user["Username"].values:
            user_id = df_user[(df_user["Username"] == username)].index
            # user_info = user_data.loc[user_id]
            print(df_user.loc[user_id, "Password"].values)
            print(password)
            if df_log.empty:
                last_index = 0
            else:
                # last_file = df_log.tail(1)
                # last_index = int(last_file["ID"].values) + 1
                last_index = df_log.index[-1]+1 # index for new record
                print("last_index is ",last_index)
            logID = last_index
            df_log.loc[logID, "ID"] = last_index
            df_log.loc[logID, "UserID"] = user_id
            df_log.loc[logID, "Operation"] = "login"
            df_log.loc[logID, "Time"] = get_time
            df_log.to_csv("log_file.csv")
            if password == df_user.loc[user_id, "Password"].values:
                payload = {
                    "username": username,
                    "role": "admin",
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=600)
                }

                token = jwt.encode(payload, SECRET_KEY)
                return token
            else:
                abort(400, message="password is not correct")

        else:
            abort(400, message="username is not registered")


# for user to create  a new account (username and password) , do update their account information and delete their account
# the operations do in user_accounts.csv file
@api.route("/users")
class Registration(Resource):

    @api.response(400, "Invalid username or password")
    @api.response(200, "Success registration")
    @api.doc(descrption="User can register an account in our service.")
    @api.expect(user_model, validate=True)
    def post(self):
        df_log = pd.read_csv("log_file.csv", usecols=["ID", "UserID", "Operation", "Time"])
        df_log.set_index(["ID"], inplace = True)
        print(df_log.to_string())

        get_time = time.asctime(time.localtime(time.time()))

        df_user = pd.read_csv("user_accounts.csv", usecols=["UserID", "Username", "Password"])
        df_user.set_index(["UserID"], inplace=True)

        user = request.json

        # if ("UserID" not in user) or ("Username" not in user ) or ("Password" not in user):
        #     abort(400, message= "Username and Password are needed")
        if ("Username" not in user) or ("Password" not in user):
            abort(400, message="Username and Password are needed")

        print(list(df_user["Username"]))

        if user["Username"] in list(df_user["Username"]):
            abort(400, message="Username already exist, create a new one")

        # last_user = df_user.tail(1)
        #
        # print(int(last_user["UserID"].values))
        # print(last_user.index)
        # last_index = int(last_user["UserID"].values) + 1

        last_index = df_user.index[-1]+1
        # add this valid user account (username, password) into csv file
        userID = last_index  # user["UserID"]
        pw = user["Password"]
        if not (re.search('.*[A-Z]+.*', pw) or re.search('.*[a-z]+.*', pw)):
            abort(400, message="Password should not onlu figure")
        for key in user:
            if key not in user_model.keys():
                abort(400, "Property {} is invalid".format(key))
            df_user.loc[userID, key] = user[key]
        #df_user.loc[userID, "UserID"] = last_index
        print(df_user.to_string())
        # print(userID)
        # print(df_user)

        # user_data.set_index("UserID")
        df_user.to_csv("user_accounts.csv")

        if df_log.empty:
            last_index = 0
        else:
            # last_file = df_log.tail(1)
            # print(int(last_file["ID"].values))
            # print(last_file.index)
            # last_index = int(last_file["ID"].values) + 1
            last_index = df_log.index[-1]+1
        logID = last_index
        df_log.loc[logID,"ID"] = last_index
        df_log.loc[logID,"UserID"] = userID
        df_log.loc[logID, "Operation"] = "Register"
        df_log.loc[logID,"Time"] = get_time
        print(df_log.to_string())
        df_log.to_csv("log_file.csv")
        # df.to_csv("user_accounts.csv")
        return {"message": "UserID is {} has created".format(userID)}, 200


parser1 = reqparse.RequestParser()
parser1.add_argument("graph service", required=True, choices=["graph1", "graph2", "graph3"])

suburb_list = ["Reservoir", "Richmond", "Brunswick", "Bentleigh East", "Coburg", "Essendon", "Preston", "Hawthorn",
               "Yarraville", "Glenroy", "Glen Iris", "Pascoe Vale",
               "Moonee Ponds", "St Kilda", "Kew", "Carnegie", "Footscray", "South Yarra", "Brighton", "Northcote",
               "Balwyn North", "Elwood", "Port Melbourne",
               "Ascot Vale", "Newport", "Brighton East", "Thornbury", "Brunswick West", "Camberwell", "Malvern East",
               "Prahran", "Bentleigh", "Keilor East",
               "Maribyrnong", "Kensington", "Surrey Hills", "Doncaster", "Balwyn", "Hawthorn East", "Hampton",
               "West Footscray", "Williamstown", "Fawkner", "Sunshine West",
               "Templestowe Lower", "Maidstone", "Ormond", "Ivanhoe", "Armadale", "Brunswick East", "Sunshine",
               "North Melbourne", "South Melbourne", "Elsternwick",
               "Toorak", "Collingwood", "Burwood", "Fitzroy North", "Moorabbin", "Heidelberg Heights", "Ashburton",
               "Murrumbeena", "Airport West", "Seddon",
               "Abbotsford", "Craigieburn", "Niddrie", "Hadfield", "Flemington", "Oak Park", "Malvern", "Fitzroy",
               "Altona", "Albert Park", "Melbourne", "Bulleen",
               "Werribee", "Box Hill", "Strathmore", "Ashwood", "Coburg North", "Altona North", "Fairfield",
               "Braybrook", "Avondale Heights", "Windsor", "Epping",
               "Watsonia", "Oakleigh South", "Canterbury", "Rosanna", "Oakleigh", "Aberfeldie", "Sunshine North",
               "Heidelberg West", "Clifton Hill", "Caulfield South",
               "Kingsville", "Hughesdale", "Chadstone", "Sunbury", "Mount Waverley", "Mill Park", "Heidelberg",
               "Southbank", "Albion", "Glen Waverley", "Kew East",
               "Viewbank", "Cheltenham", "Carlton", "West Melbourne", "Caulfield North", "Lalor", "Greensborough",
               "Gowanbrae", "Eaglemont", "Middle Park", "Spotswood",
               "Bundoora", "Doncaster East", "Jacana", "Croydon", "Sandringham", "Mont Albert", "Yallambie",
               "Alphington", "Mitcham", "Mulgrave", "Hoppers Crossing", "Balaclava",
               "Ivanhoe East", "Carlton North", "Meadow Heights", "South Morang", "Keilor Park", "Cremorne",
               "St Albans", "Parkdale", "Essendon West", "Dingley Village",
               "Mentone", "Hampton East", "Ferntree Gully", "Thomastown", "South Kingsville", "Eltham", "Seaford",
               "Essendon North", "Hillside", "Highett", "Wantirna South",
               "Greenvale", "Bayswater", "Point Cook", "Melton", "Parkville", "Ringwood East", "Broadmeadows",
               "Templestowe", "Williamstown North", "Frankston South",
               "Roxburgh Park", "Melton South", "Blackburn", "Boronia", "Kealba", "Nunawading", "Frankston",
               "Eltham North", "Vermont", "Donvale", "Mordialloc", "Glen Huntly",
               "Forest Hill", "Keilor Downs", "Carrum Downs", "Ringwood", "Tarneit", "Noble Park", "Berwick", "Clayton",
               "Tullamarine", "Heathmont", "Dandenong North",
               "Rowville", "Oakleigh East", "East Melbourne", "Blackburn South", "Keysborough", "Taylors Hill",
               "Melton West", "Edithvale", "Bellfield", "Montmorency",
               "Travancore", "Caroline Springs", "Burwood East", "Mooroolbark", "Kingsbury", "Wheelers Hill",
               "Blackburn North", "Gladstone Park", "Keilor", "Beaumaris",
               "Taylors Lakes", "Gisborne", "Scoresby", "Burnley", "Briar Hill", "Brooklyn", "Westmeadows",
               "Kings Park", "Vermont South", "Croydon North", "Bayswater North",
               "Deer Park", "Diamond Creek", "Delahey", "Frankston North", "Carrum", "Caulfield", "Gardenvale",
               "Black Rock", "Bonbeach", "Doveton", "Chelsea Heights", "Sydenham",
               "Endeavour Hills", "Watsonia North", "Kurunjang", "Cairnlea", "Clayton South", "Huntingdale",
               "Aspendale", "Wollert", "Chelsea", "Mernda", "Kilsyth", "Dandenong",
               "Wyndham Vale", "Clarinda", "Ripponlea", "Strathmore Heights", "Altona Meadows", "Ringwood North",
               "Coolaroo", "Springvale", "Burnside Heights", "Ardeer",
               "Caulfield East", "Narre Warren", "Croydon Hills", "Doreen", "Seaholme", "St Helena", "Hampton Park",
               "Pakenham", "Mount Evelyn", "Wantirna", "Princes Hill",
               "Notting Hill", "Albanvale", "Truganina", "Langwarrin", "North Warrandyte", "Dallas", "Riddells Creek",
               "Waterways", "Yarra Glen", "Sandhurst", "Hurstbridge",
               "McKinnon", "Williams Landing", "Diggers Rest", "The Basin", "Cranbourne North", "Healesville",
               "Springvale South", "Hallam", "Beaconsfield Upper", "Wallan",
               "Skye", "Montrose", "Deepdene", "Knoxfield", "Emerald", "Plumpton", "Campbellfield", "Cranbourne",
               "Brookfield", "Seabrook", "Whittlesea", "Beaconsfield",
               "Lower Plenty", "Burnside", "Kooyong", "Warrandyte", "Derrimut", "Chirnside Park"]
parser1.add_argument("suburb", choices=suburb_list)
parser1.add_argument('year', type=float)
parser1.add_argument("distance", type=float)
parser1.add_argument("UserID", required = True, type = int)

df_street = pd.read_csv("streetFlat.csv", usecols=["street"])
street_list = list(df_street["street"])

df_region = pd.read_csv("regionFlat.csv", usecols=["Region"])
region_list = list(df_region["Region"])

df_type = pd.read_csv("typeFlat.csv", usecols=["Type"])
type_list = list(df_type["Type"])

@api.route('/graphs')
# @api.doc(decsription="Graph1: please submit year\nGrapg2: please submit suburb name and year\nGraph3: please submit distance.")
class Graph(Resource):
    @api.param("year", "The year when houses built")
    @api.param("suburb", "The suburb name in Melbourne")
    @api.param("distance", "The distance from house to CBD")
    @api.param("graph service",
               "Graph1 : present the average house prices in the time range [input_year - 5, input_year +5],please submit year\n"
               + "Graph2 : present the average house prices in a particular suburb in time range [input_year-5, input_year +5],please submit suburb name and year\n"
               + "Graph3 : present the top 5 lowest house prices suburb and distance less than the input distance,please submit distance."
               )
    @api.param("UserID")
    @api.expect(parser1, validate=True)
    @api.response(400, "Error: Invalid input")
    @api.response(200, "Success")
    @api.response(404, "Error: Not Found Information")
    @requires_auth
    # @api.expect(parser1, validate=True)
    def get(self):
        df_user = pd.read_csv("user_accounts.csv", usecols=["UserID", "Username", "Password"])
        df_user.set_index(["UserID"], inplace=True)

        args = parser1.parse_args()
        id = args.get("UserID")

        if id not in df_user.index:
            abort(404, message="User {} does not exist".format(id))

        df_log = pd.read_csv("log_file.csv", usecols=["ID", "UserID", "Operation", "Time"])
        df_log.set_index(["ID"], inplace=True)
        print(df_log.to_string())
        # df_log.set_index(["ID"], inplace = True)
        get_time = time.asctime(time.localtime(time.time()))
        if df_log.empty:
            last_index = 0
        else:
            last_index = df_log.index[-1] + 1
        logID = last_index
        # df_log.loc[logID, "ID"] = last_index
        df_log.loc[logID, "UserID"] = id
        df_log.loc[logID, "Operation"] = "Get graph of houses price information"
        df_log.loc[logID, "Time"] = get_time
        print(df_log.to_string())
        df_log.to_csv("log_file.csv")


        graph_service = args.get("graph service")
        if graph_service == "graph1":
            if "year" not in args:
                abort(400, message="year is required")
            year = args.get("year")
            if year <= 999:
                abort(400, message="Invalid year value")
            graph_df = dg.graph1(year)  # the dataframe of the graph to point
        elif graph_service == "graph2":
            if ("suburb" not in args) or ("year" not in args):
                abort(400, message="year and suburb must required")
            year = args.get("year")
            suburb = args.get("suburb")
            if year <= 999:
                abort(400, message="Invalid year value")
            print(year)
            print(type(year))
            print(suburb)
            print(type(suburb))
            # suburb = str(suburb)

            graph_df = dg.graph2(suburb, year)
        else:
            if "distance" not in args:
                abort(400, message="Distance is required")
            distance = args.get("distance")
            graph_df = dg.graph3(distance)

        if graph_df.empty:
            abort(400, message="Input is invalid")

        print(graph_df.to_string())
        graph_json = graph_df.to_json(orient='index')
        graph = json.loads(graph_json)
        ret = []
        for idx in graph:
            g = graph[idx]
            g["year"] = idx
            ret.append(g)

        return ret, 200




@api.route("/users/<int:id>")
#@api.param("username", "The username of an account created previously")
class UserAccountsManage(Resource):

    @api.response(404,"Error: Not Found Information")
    @api.response(200, "Success information retrieval.")
    @requires_auth

    def get(self,id):

        #according to username to give the user account information without password
        df_user = pd.read_csv("user_accounts.csv", usecols=["UserID", "Username", "Password"])
        df_user.set_index(["UserID"], inplace= True)

        if id not in df_user.index:
            abort(404, message="User {} does not exist".format(id))
        df_log = pd.read_csv("log_file.csv", usecols=["ID", "UserID", "Operation", "Time"])
        df_log.set_index(["ID"], inplace = True)
        print(df_log.to_string())
        # df_log.set_index(["ID"], inplace = True)
        get_time = time.asctime(time.localtime(time.time()))
        if df_log.empty:
            last_index = 0
        else:
            last_index = df_log.index[-1]+1
        logID = last_index
        #df_log.loc[logID, "ID"] = last_index
        df_log.loc[logID, "UserID"] = id
        df_log.loc[logID, "Operation"] = "Get user Info"
        df_log.loc[logID, "Time"] = get_time
        print(df_log.to_string())
        df_log.to_csv("log_file.csv")

        user = {"UserID": id, "Username": df_user.loc[id,"Username"]}
        print(user)
        return user, 200

    @api.response(404, "Error: Not Found Information")
    @api.response(400, "Error: Invalidate request")
    @api.response(200, "Success Update")
    @api.response(403, "Error: No Right to access data")
    @api.doc(description="User can update its account information about username and password")
    @api.expect(user_model)
    @requires_auth
    def put(self, id):
        get_time = time.asctime(time.localtime(time.time()))
        df_user = pd.read_csv("user_accounts.csv", usecols=["UserID", "Username", "Password"])
        df_user.set_index(["UserID"], inplace=True)
        # for user to update its own user account i # df = pd.read_csv("user_accounts.csv")

        if id not in df_user.index:
            abort(404, message="User {} does not exist".format(id))

        # if df_user.loc[id,"Username"] != username or df_user.loc[id,"Password"] != password:
        #     abort(403, message= "No permission to access account{}".format(id))

        df_log = pd.read_csv("log_file.csv", usecols=["ID", "UserID", "Operation", "Time"])
        df_log.set_index(["ID"], inplace=True)
        print(df_log.to_string())
        if df_log.empty:
            last_index = 0
        else:
            # last_file = df_log.tail(1)
            # print(int(last_file["ID"].values))
            # print(last_file.index)
            # last_index = int(last_file["ID"].values) + 1
            last_index = df_log.index[-1] + 1
        logID = last_index
        #df_log.loc[logID, "ID"] = last_index
        df_log.loc[logID, "UserID"] = id
        df_log.loc[logID, "Operation"] = "Update user Info"
        df_log.loc[logID, "Time"] = get_time
        print(df_log.to_string())
        df_log.to_csv("log_file.csv")

        user = request.json
        # update the user account
        # index = df.query("UserID == @UserID").index.tolist()[0] #find the index of this row containing the username

        for key in user:
            if key not in user_model.keys():
                abort(400, message="Invalid Property {}".format(key))
            df_user.loc[id, key] = user[key]


        df_user.to_csv("user_accounts.csv")



        return {"message": "Your account updated successfully"}, 200

    # @api.doc(description="User delete an account")
    # @api.response(404, "Error: Not Found Information")
    # @api.response(200, " Successful request ")
    # @requires_auth
    # # @api.token_required
    # def delete(self, id):
    #     # for user delete their account
    #     df_user = pd.read_csv("user_accounts.csv", usecols=["UserID", "Username", "Password"])
    #     df_user.set_index(["UserID"], inplace=True)
    #
    #     if id not in df_user.index:
    #         abort(404, message="User {} does not exist".format(id))
    #
    #     # drop the row with this username
    #     # row = [index for index,row in df.iterrows() if row["Username"] == username]
    #     df_user.drop(id, inplace=True)
    #     df_user.to_csv("user_accounts.csv")
    #
    #     df_log = pd.read_csv("log_file.csv", usecols=["ID", "UserID", "Operation", "Time"])
    #     df_log.set_index(["ID"], inplace = True)
    #     print(df_log.to_string())
    #     get_time = time.asctime(time.localtime(time.time()))
    #     if df_log.empty:
    #         last_index = 0
    #     else:
    #         # last_file = df_log.tail(1)
    #         # print(int(last_file["ID"].values))
    #         # print(last_file.index)
    #         # last_index = int(last_file["ID"].values) + 1
    #         last_index = df_log.index[-1]+1
    #     logID = last_index
    #     #df_log.loc[logID, "ID"] = last_index
    #     df_log.loc[logID, "UserID"] = id
    #     df_log.loc[logID, "Operation"] = "Delete user Info"
    #     df_log.loc[logID, "Time"] = get_time
    #     print(df_log.to_string())
    #     df_log.to_csv("log_file.csv")
    #
    #
    #     return {"message": "Account delete successfully"}, 200


parser = reqparse.RequestParser()  # initialize a request parser
# use query parameters to pass username and password, this is for check this user whether has the right to do operation in the house information which he request
# because only the owner of those house can have the right to access those house information and do operation.

order_list = ["Distance", "Landsize", "BuildingArea", "YearBuilt"]
parser.add_argument('order', choices=order_list)
parser.add_argument('ascending', type=inputs.boolean)
parser.add_argument("UserID", required=True, type=int)


@api.route('/houses')
class HousesList(Resource):
    #@api.response(400, "Error: User name or password incorrect.")
    @api.response(404,"Error: Not Found Information")
    @api.response(200, "Success information retrieval.")
    @api.doc(description="User can get all houses information he or she has provided so far.")
    @api.expect(parser, validate=True)
    @requires_auth
    # @api.token_required
    def get(self):
        # Since this get operation is for retrieval all houses information of a owner has provided yet, so the
        # dataset which should be accessed is the test dataset.
        # get houses as JSON string
        # read information from csv file
        df = pd.read_csv("user_houses.csv",
                         usecols=["Identifier", "UserID", "Distance", "Bedroom", "Bathroom", "Car", "Landsize",
                                  "BuildingArea", "YearBuilt", "Lattitude",
                                  "Longtitude", "Suburb", "Street", "Type", "Regionname", "Predicted_Price"])
        df.set_index(["Identifier"], inplace=True)

        args = parser.parse_args()
        order = args.get('order')
        ascending = args.get('ascending', False)

        userID = args.get('UserID')


        if userID not in list(df["UserID"]):
            api.abort(404, "No house information")


        house_price_info = df.query('UserID == @userID')  # 截取所有这个userID的house information

        df_log = pd.read_csv("log_file.csv", usecols=["ID", "UserID", "Operation", "Time"])
        df_log.set_index(["ID"], inplace=True)
        print(df_log.to_string())
        get_time = time.asctime(time.localtime(time.time()))
        if df_log.empty:
            last_index = 0
        else:
            # last_file = df_log.tail(1)
            # print(int(last_file["ID"].values))
            # print(last_file.index)
            # last_index = int(last_file["ID"].values) + 1
            last_index = df_log.index[-1] + 1
        logID = last_index
        #df_log.loc[logID, "ID"] = last_index
        df_log.loc[logID, "UserID"] = userID
        df_log.loc[logID, "Operation"] = "Get the houses list of User-predicted"
        df_log.loc[logID, "Time"] = get_time
        print(df_log.to_string())
        df_log.to_csv("log_file.csv")

        if order:
            house_price_info.sort_values(by=order, inplace=True, ascending=ascending)

        json_str = house_price_info.to_json(orient='index')

        print(house_price_info.to_string())
        print(json_str)

        ds = json.loads(json_str) # ds is dict
        print(type(ds))
        # print("\nds")
        # print(ds)
        ret = []
        # print("\nds list")
        # for idx in ds:
        #     print(idx)
        #
        for idx in ds:
            house = ds[idx]
            house["Identifier"] = idx
            ret.append(house)

        print(ret)


        return ret,200

    @api.response(200, " Successful request ")
    @api.response(400, "Error: Invalidate request")
    @api.doc(description="Add a new house information, and return the predict price")
    @api.expect(house_model, validate=True)
    @requires_auth
    # @api.token_required
    def post(self):
        #read information from csv file
        df = pd.read_csv("user_houses.csv",
                         usecols=["Identifier", "UserID", "Distance", "Bedroom", "Bathroom", "Car", "Landsize",
                                  "BuildingArea", "YearBuilt", "Lattitude",
                                  "Longtitude", "Suburb", "Street", "Type", "Regionname", "Predicted_Price"])
        df.set_index(["Identifier"], inplace = True)
        print("###################df####################")
        print(df.to_string())
        # since post new data for predict price, so accessing dataset here is test dataset
        # for user to provide  a new house and its details into dataset
        house = request.json  # the content that post request provide
        df_log = pd.read_csv("log_file.csv", usecols=["ID", "UserID", "Operation", "Time"])
        df_log.set_index(["ID"], inplace = True)
        print(df_log.to_string())
        get_time = time.asctime(time.localtime(time.time()))
        if df_log.empty:
            last_index = 0
        else:
            # last_file = df_log.tail(1)
            # print(int(last_file["ID"].values))
            # print(last_file.index)
            last_index = df_log.index[-1] + 1
        logID = last_index
        #df_log.loc[logID, "ID"] = last_index
        df_log.loc[logID, "UserID"] = house["UserID"]
        df_log.loc[logID, "Operation"] = "Predict"
        df_log.loc[logID, "Time"] = get_time
        print(df_log.to_string())
        df_log.to_csv("log_file.csv")
        if "Identifier" not in house:
            return {"message": "Identifier is missing."}, 400

        id = house["Identifier"]  # id is the Identifier of the house which a user just post

        # check the Identifier whether already exist
        if id in df.index:
            return {
                       "message": "Sorry, A house with identifier {} is already exist, please create a new identifier.".format(
                           id)}, 400

        # put the value into the dataset
        df_predicted = pd.DataFrame(
            columns=["Identifier", "UserID", "Distance", "Bedroom", "Bathroom", "Car", "Landsize", "BuildingArea",
                     "YearBuilt", "Lattitude",
                     "Longtitude", "Suburb", "Street", "Type", "Regionname"])

        #print("在预测price之前的df;")
        print(df.to_string())
        for key in house:
            if str(key) == "Identifier":
                continue
            if key not in house_model.keys():
                # unexpected features
                return {"message": "Property {} is invalid.".format(str(key))}, 400
            if key == "Suburb":  # whe  suburb part, check the input string whether valid or not
                if house[key] not in suburb_list:
                    return {"message": "Property {}'s value is invalid".format(str(key))}, 400
            if key == "Street":
                if house[key] not in street_list:
                    return {"message": "Property {}'s value is invalid".format(str(key))}, 400
            if key == "Type":
                if house[key] not in type_list:
                    return {"message": "Property {}'s value is invalid".format(str(key))}, 400
            if key == "Regionname":
                if house[key] not in region_list:
                    return {"message": "Property {}'s value is invalid".format(str(key))}, 400

            df_predicted.loc[0, key] = house[key]
            df.loc[id, key] = house[key]

        # recall the regression function to predict the new dataset, and return the dataset with predict price column

        # remove the user and password columns and send to the subset part to machine learning function
        # df1 = df.query("Identifer == @id")
        # only get a specific row information to predict price
        #print("在预测price之前的df;")
        print(df.to_string())
        # 这里调用 machine_learning 的信息可能还是用问题，主要是好想表格的输入输出类型不一致。

        df1 = ml.data_processing(df_predicted)
        result = ml.machine_learning(df1)  # result has price and index only

        print("*************result********************")
        print(result.to_string())
        price = result.loc[0, "Price"]

        df.loc[id, "Predicted_Price"] = price

        print("##############final df is ##############")
        print(df.to_string())
        df.to_csv('user_houses.csv')





        # 样品输出
        return {"message": "The house {} information has been posted and predict price is {}".format(id, price)}, 200


@api.route("/houses/<int:id>")
@api.param("id", "The house identifier")
@api.param("UserID", "The user ID",type= int)
# @api.param("Password","The password of user account")
class Houses(Resource):

    @api.response(403, "Error: No Right to access data")
    @api.response(400, "Error: Invalidate request")
    @api.response(404,"Error: Not Found Information")
    @api.response(200, " Successful request ")
    @api.doc(description=" Update information of a house by its Identifier, and return the new predict price")
    @api.expect(house_model)
    @requires_auth
    # @api.token_required
    def put(self, id):

        df = pd.read_csv("user_houses.csv",
                         usecols=["Identifier", "UserID", "Distance", "Bedroom", "Bathroom", "Car", "Landsize",
                                  "BuildingArea", "YearBuilt", "Lattitude",
                                  "Longtitude", "Suburb", "Street", "Type", "Regionname", "Predicted_Price"])


        df.set_index(["Identifier"], inplace= True)
        print(df.to_string())
        print(df.index)
        # the accessing dataset is test dataset
        args = parser.parse_args()

        # 我觉得可能不需要user和password作为query parameter了，因为expect model里面有user 和password
        user = float(args.get("UserID"))
        # password = args.get("Password")
        print(id)
        print(df.index)
        if id not in df.index:
            print("************************************************")
            api.abort(404, "House with id {} is not exist.".format(id))

        house = request.json  # covert the request to json

        df_log = pd.read_csv("log_file.csv", usecols=["ID", "UserID", "Operation", "Time"])
        df_log.set_index(["ID"], inplace=True)
        print(df_log.to_string())
        get_time = time.asctime(time.localtime(time.time()))
        if df_log.empty:
            last_index = 0
        else:
            # last_file = df_log.tail(1)
            # print(int(last_file["ID"].values))
            # print(last_file.index)
            last_index = df_log.index[-1] + 1
        logID = last_index
        #df_log.loc[logID, "ID"] = last_index
        df_log.loc[logID, "UserID"] = int(df.loc[id, "UserID"])
        df_log.loc[logID, "Operation"] = "Update house Info"
        df_log.loc[logID, "Time"] = get_time
        print(df_log.to_string())
        df_log.to_csv("log_file.csv")


        # for checking the user whether has the right to access the house information
        print("################User ID ###############")
        print(df.loc[id,"UserID"])
        if df.loc[id,"UserID"]- user != 0:
            api.abort(403, "message: Sorry, you has no right to access house {}".format(id))

        #
        # if user is not  df.loc[id, "UserID"]:
        #     abort(400, message="No permission to access the house information")
        print("没有更新房子信息之前的：")
        print(df.to_string())
        if "Identifier" in house and id != house["Identifier"]:
            return {"message": "House Identifier cannot be changed."}, 400

        df_predicted = pd.DataFrame(
            columns=["Identifier", "UserID", "Distance", "Bedroom", "Bathroom", "Car", "Landsize", "BuildingArea",
                     "YearBuilt", "Lattitude",
                     "Longtitude", "Suburb", "Street", "Type", "Regionname"])
        # Update the house information
        # Update the house information
        for key in house:
            if str(key) == "Identifier":
                continue
            if key not in house_model.keys():
                return {"message": "Property {} is invalid.".format(str(key))}, 400
            if key == "Suburb":  # whe  suburb part, check the input string whether valid or not
                if house[key] not in suburb_list:
                    return {"message": "Property {}'s value is invalid".format(str(key))}, 400
            if key == "Street":
                if house[key] not in street_list:
                    return {"message": "Property {}'s value is invalid".format(str(key))}, 400
            if key == "Type":
                if house[key] not in type_list:
                    return {"message": "Property {}'s value is invalid".format(str(key))}, 400
            if key == "Regionname":
                if house[key] not in region_list:
                    return {"message": "Property {}'s value is invalid".format(str(key))}, 400

            df.loc[id, key] = house[key]
            if str(key) != "Price":
                df_predicted.loc[0,key] = house[key]
        print("更新房子信息之后的：")
        print(df.to_string())
        # recall the regression function to predict price
        # price = regression_function(df).loc[id, "Price"]
        # price = df_price.loc[id,"Price"]
        # remove the user and password columns and send to the subset part to machine learning function
        # remove the user and password columns and send to the subset part to machine learning function
        print("##############df_predicted#############")
        print(df_predicted.to_string())
        df1 = ml.data_processing(df_predicted)
        result = ml.machine_learning(df1)  # result has price and index only
        # df.loc[id, "Price"] = result[id, "Price"]  # update the houses information in csv file
        # df.to_csv("user_houses.csv")
        print("#############reuslt####################")
        print(result.to_string())
        price = result.loc[0, "Price"]
        df.loc[id, "Predicted_Price"] = price
        print("############final df#############")
        print(df.to_string())
        df.to_csv('user_houses.csv')

        # return price, 200
        return {"message": "House {} information has been updated and predict price {}".format(id, price)}, 200

    @api.response(403, "Error: No Right to access data ")
    @api.response(404,"Error: Not Found Information")
    @api.response(200, " Successful request ")
    @api.doc(description="Delete a house and its information from dataset")
    @requires_auth
    # @api.token_required
    def delete(self, id):

        df = pd.read_csv("user_houses.csv",
                         usecols=["Identifier", "UserID", "Distance", "Bedroom", "Bathroom", "Car", "Landsize",
                                  "BuildingArea", "YearBuilt", "Lattitude",
                                  "Longtitude", "Suburb", "Street", "Type", "Regionname", "Predicted_Price"])


        df.set_index(["Identifier"], inplace=True)
        print(df.to_string())

        args = parser.parse_args()

        user = args.get("UserID")
        df_log = pd.read_csv("log_file.csv", usecols=["ID", "UserID", "Operation", "Time"])
        df_log.set_index(["ID"], inplace = True)
        print(df_log.to_string())
        get_time = time.asctime(time.localtime(time.time()))
        if df_log.empty:
            last_index = 0
        else:
            # last_file = df_log.tail(1)
            # print(int(last_file["ID"].values))
            # print(last_file.index)
            last_index = df_log.index[-1] + 1
        logID = last_index
        #df_log.loc[logID, "ID"] = last_index
        df_log.loc[logID, "UserID"] = user
        df_log.loc[logID, "Operation"] = "Delete the prediction data"
        df_log.loc[logID, "Time"] = get_time
        print(df_log.to_string())
        df_log.to_csv("log_file.csv")
        print(type(df.index))
        print(list(df.index))
        print(id)
        print(type(id))

        if id not in df.index:
            print("############################################")
            #api.abort(402, "House {} is not exist".format(id))
            api.abort(404, "House {} doesn't exist".format(id))

        if df.loc[id, "UserID"] != user:
            api.abort(403, "message: Sorry, you has no right to access house {}".format(id))

        print("***************************************")
        # delete the house from dataset
        df.drop(index=id, inplace=True)
        df.to_csv('user_houses.csv')

        return {"message": " House {} has been deleted successfully".format(id)}, 200
log_parser = reqparse.RequestParser()  # initialize a request parser
# use query parameters to pass username and password, this is for check this user whether has the right to do operation in the house information which he request
# because only the owner of those house can have the right to access those house information and do operation.

operation_list = ["login", "Register", "Predict", "Get the houses list of User-predicted","Delete the prediction data",
                  "Get user Info","Update house Info","Update user Info","Get graph of houses price information"]
log_parser.add_argument('operation', choices=operation_list)
@api.route("/APIUsage")
class APIUsage(Resource):
    @api.response(404, "Error: Not Found Information")
    @api.response(200, " Successful request ")
    @api.doc(description="The information about API usage")
    @api.expect(log_parser,validate=True)
    @requires_auth
    def get(self):   #show the usage info in a pie chart,every operation take a part
        args = log_parser.parse_args()
        log_operation = args.get("operation")
        df_log = pd.read_csv('log_file.csv',usecols=["ID", "UserID", "Operation", "Time"])
        df_log.set_index("ID", inplace=True)
        print("###############df_log#############################")
        print(df_log.to_string())
        print(log_operation)
        print(df_log["Operation"])
        if log_operation in df_log["Operation"].values:
            logs = df_log.query('Operation == @log_operation')
            log_json = logs.to_json(orient='index')
            log = json.loads(log_json)
            ret = []
            for idx in log:
                log_info = log[idx]
                log_info["ID"] = idx
                ret.append(log_info)

            return ret,200
        else:
            api.abort(404, "Operation {} doesn't exist".format(log_operation))

# for front end
@app.route("/")
def index():
    return redirect("/index.html",code=302)


if __name__ == "__main__":
    # df = pd.read_csv("user_houses.csv",
    #                  usecols=["Identifier", "UserID", "Distance", "Badroom2", "Bathroom", "Car", "Landsize",
    #                           "BuildingArea", "YearBuilt", "Lattitude",
    #                           "Longtitude", "Suburb", "Street", "Type", "Regionname", "Predicted_Price"])
    # # df = pd.DataFrame(
    # #     columns=["Identifier", "UserID", "Distance", "Badroom2", "Bathroom", "Car", "Landsize", "BuildingArea",
    # #              "YearBuilt", "Lattitude",
    # #              "Longtitude", "Suburb", "Street", "Type", "Regionname","Predicted_Price"])
    # df.set_index("Identifier")

    # df = pd.read_csv("user_houses.csv", usecols = ["Identifier", "UserID","Distance","Badroom2", "Bathroom","Car","Landsize","BuildingArea","YearBuilt",
    #                                                "Lattitude","Longtitude","Suburb","Street","Type","Regionname"])
    # 关于house information都存在user_houses.csv file 里面
    # user (username, password) 存在user_accounts.csv file里面

    # df_user = pd.DataFrame(columns = ["UserID","Username","Password"])
    # df_user = pd.DataFrame(columns=["Username", "Password"])
    # df_user.set_index("UserID")
    # df_user = pd.read_csv("user_accounts.csv", usecols=["UserID", "Username", "Password"])
    # df_user.set_index("UserID")
    # this file is used for storing the user's username and password
    app.run(debug=True, host="0.0.0.0")