    @api.route("/APIUsage")
    class APIUsage(Resource):
        @api.response(404, "Error: Not Found Information")
        @api.response(200, " Successful request ")
        @api.doc(description="The information about API usage")
        @requires_auth
        def get(self):  # show the usage info in a pie chart,every operation take a part
            df_log = pd.read_csv('log_file.csv', usecols=["ID", "UserID", "Operation", "Time"])
            df_log.set_index("ID", inplace=True)
            print("###############df_log#############################")
            operation_list = ["login", "Register", "Predict", "Get the houses list of User-predicted",
                              "Delete the prediction data",
                              "Get user Info", "Update house Info", "Update user Info",
                              "Get graph of houses price information"]
            total = df_log.shape[0]
            ret = []
            for p in operation_list:
                logs = df_log.query('Operation == @p').values
                logs_count = len(logs)
                percentage = logs_count / total
                percentage = round(percentage * 100, 2)
                logs_dict = {}
                logs_dict['Operation'] = p
                logs_dict["Count"] = logs_count
                logs_dict["Percentage"] = percentage
                ret.append(logs_dict)
            return ret, 200