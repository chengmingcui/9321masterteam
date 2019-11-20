import json
import jwt
import datetime
import ujson


import pandas as pd
from flask import Flask
from flask import request
from flask_restplus import Resource, Api
from flask_restplus import fields,abort
from flask_restplus import inputs
from flask_restplus import reqparse
import machine_learning as ml

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
            ujson(jwt.decode(token,SECRET_KEY))
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
        print(df_user.Username)
        print(username)
        if username in df_user["Username"].values:
            user_id = df_user[(df_user["Username"] == username)].index
            user_info = df_user.loc[user_id]
            print(df_user.loc[user_id,"Password"].values)
            print(password)
            if password == df_user.loc[user_id,"Password"].values:
                payload = {
                    "username":username,
                    "role":"admin",
                    "exp" : datetime.datetime.utcnow() + datetime.timedelta(seconds= 600)
                }

                token = jwt.encode(payload,SECRET_KEY)
                return token
            else:
                abort(400,message="password is not correct")
        else:
            abort(400,message="username is not registered")



parser = reqparse.RequestParser()
parser = reqparse.RequestParser()
parser.add_argument("UserID", required= True)

user_model = api.model("User",{
    "UserID": fields.Integer,
    "Username": fields.String,
    "Password": fields.String
})


#for user to create  a new account (username and password) , do update their account information and delete their account
#the operations do in user_accounts.csv file
@api.route("/users")
class Registration(Resource):

    @api.response(400, "Invalid username or password")
    @api.response(200,"Success registration")
    @api.doc(descrption = "User can register an account in our service.")
    @api.expect(user_model,validate = True)
    def post(self):
        user = request.json
        if ("UserID" not in user) or ("Username" not in user ) or ("Password" not in user):
            abort(400, message= "Username and Password are needed")
        #df = pd.read_csv("user_accounts.csv")
        if user["Username"] in list(df_user["Username"]):
            abort(400,message = "Username already exist, create a new one")

        #add this valid user account (username, password) into csv file
        userID = user["UserID"]
        for key in user:
            if key not in user_model.keys():
                abort(400,"Property {} is invalid".format(key))
            df_user.loc[userID,key] = user[key]

        #df.to_csv("user_accounts.csv")
        return {"message": "UserID is {} has created".format(userID)}, 200



@api.route("/users/<int:id>")
@api.param("username", "The username of an account created previously")
class UserAccountsManage(Resource):
    @requires_auth
    def get(self,id):
        #df_user = pd.read_csv("user_accounts.csv")

        if id not in df_user.index:
            abort(400,message="Username does not exist")




        user = dict(df_user.loc[id])
        return user, 200



    @api.response(400,"Invalid username or password")
    @api.response(200, "Success Update")
    @api.doc(description = "User can update its account information about username and password")
    @api.expect(user_model)
    @requires_auth
    #@api.token_required
    def put(self,id):

        #for user to update itsown user account information
        #df = pd.read_csv("user_accounts.csv")
        if id not in df_user.index:
            abort(400,message="User does not exist")

        user = request.json
        #update the user account
        #index = df.query("UserID == @UserID").index.tolist()[0] #find the index of this row containing the username

        for key in user:
            if key not in user_model.keys():
                abort(400,message = "Invalid Property {}".format(key))
            df_user.loc[id,key] = user[key]


        return {"message":"Your account updated successfully"}, 200

    @api.doc(description = "User delete an account")
    @api.response(400, "Invalid username")
    @api.response(200,"Delete successfully")
    @requires_auth
    #@api.token_required
    def delete(self, id):
        # for user delete their account

        if id not in df_user.index:
            return {"message": "Username does not exist"}, 400

        #drop the row with this username
        #row = [index for index,row in df.iterrows() if row["Username"] == username]
        df_user.drop(id, inplace = True)

        return {"message":"Account delete successfully"}, 200
houselist_parser = reqparse.RequestParser()  # initialize a request parser
# use query parameters to pass username and password, this is for check this user whether has the right to do operation in the house information which he request
# because only the owner of those house can have the right to access those house information and do operation.

order_list = ["Date", "Build Area", "Distance"]
houselist_parser.add_argument('order', choices=order_list)
houselist_parser.add_argument('ascending', type=inputs.boolean)
houselist_parser.add_argument("UserID", required= True)

@api.route('/houses')
class HousesList(Resource):
    @api.response(400, "Error: User name or password incorrect.")
    @api.response(200, "Success information retrieval.")
    @api.doc(description="User can get all houses information he or she has provided so far.")
    @api.expect(houselist_parser, validate=True)
    @requires_auth
    #@api.token_required
    def get(self):
        # Since this get operation is for retrieval all houses information of a owner has provided yet, so the
        # dataset which should be accessed is the test dataset.
        # get houses as JSON string
        args = houselist_parser.parse_args()

        order_by = args.get('order')
        ascending = args.get('ascending', False)

        userID = args.get('UserID')
        print(userID)


        if userID not in list(df["UserID"]):
                abort(400, messge = "no house information")


        user_house = df.query('UserID == @userID') #截取所有这个userID的house information

        if order_by:
            user_house.sort_values(by=order_by, inplace=True, ascending=ascending)

        json_str = user_house.to_json(orient='index')

        ds = json.loads(json_str)
        ret = []

        for idx in ds:
            house = {}
            id = int(idx)
            house['Identifier'] = id
            house["Type"] = df.loc(id, "type")
            house["Area"] = df.loc(id, "Region Name")
            house["Date"] = df.loc(id, "Date")
            house["Distance"] = df.loc(id, "Distance")
            ret.append(house)
        return ret, 200

    @api.response(201, " Success: A new house is posted successfully and predict price is returned ")
    @api.response(401, "Error: Invalidation post")
    @api.doc(description="Add a new house information, and return the predict price")
    @api.expect(house_model, validate=True)
    @requires_auth
    #@api.token_required
    def post(self):
        # since post new data for predict price, so accessing dataset here is test dataset
        # for user to provide  a new house and its details into dataset
        house = request.json  # the content that post request provide

        if "Identifier" not in house:
            return {"message": "Identifier must be provided, thank you."}, 401

        id = house["Identifier"]  # id is the Identifier of the house which a user just post

        # check the Identifier whether already exist
        if id in df.index:
            return {
                       "message": "Sorry, A house with identifier {} is already exist, please create a new identifier.".format(
                           id)}, 401

        # put the value into the dataset
        for key in house:
            if key not in house_model.keys():
                # unexpected features
                return {"message": "Property {} is invalid.".format(str(key))}, 401
            df.loc[id, key] = house[key]

        # recall the regression function to predict the new dataset, and return the dataset with predict price column

        #remove the user and password columns and send to the subset part to machine learning function
        #df1 = df.query("Identifer == @id")
        #only get a specific row information to predict price
        df1 = pd.DataFrame(df.query("Identifier == @id"),
                           columns = ["Identifier", "Distance","Badroom2","Bathroom","Car","Landsize","BuildingArea","YearBuilt","Lattitude",
                                      "Longtitude","Suburb","Street_Address","Type","Regionname"])


        #这里调用 machine_learning 的信息可能还是用问题，主要是好想表格的输入输出类型不一致。
        result = ml.machine_learning(df1) #result has price and index only

        for index,row in result.itterows():
            df.loc[index,"Price"] = result[index,"Price"]#update the houses information in csv file

        price = df.loc[id,"Price"]

        return price, 201


@api.route("/houses/<int:id>")
@api.param("id", "The house identifier")
@api.param("User", "The user name")
@api.param("Password","The password of user account")
class Houses(Resource):

    @api.response(403, "Error: User has not permission to access a house information")
    @api.response(401, "Error: House information invalid")
    @api.response(200, " Success: House information update and return new predict price successfully")
    @api.doc(description=" Update information of a house by its Identifier, and return the new predict price")
    @api.expect(house_model)
    @requires_auth
    #@api.token_required
    def put(self, id):
        # the accessing dataset is test dataset
        args = parser.parse_args()

        #我觉得可能不需要user和password作为query parameter了，因为expect model里面有user 和password
        user = args.get("UserID")
        #password = args.get("Password")


        if id not in df.index:
            api.abort(402, "House with id {} is not exist.".format(id))

        house = request.json  # covert the request to json

        #for checking the user whether has the right to access the house information
        if user is not df.loc[id,"UserID"]:
            abort(400,message = "No permission to access the house information")


        if "Identifier" in house and id != house["Identifier"]:
            return {"message": "House Identifier cannot be changed."}, 401

        # Update the house information
        for key in house:
            if key not in house_model.keys():
                return {"message": "Property {} is invalid.".format(str(key))}, 401
            df.loc[id, key] = house[key]

        #recall the regression function to predict price
        # price = regression_function(df).loc[id, "Price"]
        #price = df_price.loc[id,"Price"]
            # remove the user and password columns and send to the subset part to machine learning function
            # remove the user and password columns and send to the subset part to machine learning function
        df1 = pd.DataFrame(df, columns=["Identifier", "Distance", "Badroom2", "Bathroom", "Car", "Landsize",
                                            "BuildingArea", "YearBuilt", "Lattitude",
                                            "Longtitude", "Suburd", "Street", "Type",
                                            "Regionname"])

        result = ml.machine_learning(df1)  # result has price and index only
        df.loc[id, "Price"] = result[id, "Price"]  # update the houses information in csv file
        df.to_csv("user_houses.csv")
        price = df.loc[id, "Price"]

        return price, 200


    @api.response(403, "Error: User has not permission to access a house information")
    @api.response(402, " Error: Invalid House Identifier")
    @api.response(200, "Success: House information delete successfully")
    @api.doc(description="Delete a house and its information from dataset")
    @requires_auth
    #@api.token_required
    def delete(self, id):

        args = parser.parse_args()

        user = args.get("UserID")

        if id not in df.index:
            api.abort(402, "House with id {} is not exist".format(id))

        if df.loc[id, "User"] != user:
            return {"message": "Sorry, you has no right to access house {}".format(id)}, 403

        # delete the house from dataset
        df.drop(id, inplace=True)
        df.to_csv("user_houses.csv") #update to csv file

        return {"message": " House {} has been deleted successfully".format(id)}, 200


if __name__ == "__main__":

    df = pd.DataFrame(columns = ["Identifier", "UserID","Distance","Badroom2","Bathroom","Car","Landsize","BuildingArea","YearBuilt","Lattitude",
                                      "Longtitude","Suburb","Street","Type","Regionname","Price"])
    df.to_csv("user_houses.csv")

    # 关于house information都存在user_houses.csv file 里面
    # user (username, password) 存在user_accounts.csv file里面
    df.set_index("Identifier")

    df_user = pd.DataFrame(columns = ["UserID","Username","Password"])
    df_user.set_index("UserID")
    df_user.to_csv("user_accounts.csv") # this file is used for storing the user's username and password


    app.run(debug=True)




