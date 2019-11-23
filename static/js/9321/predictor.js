// for login and predict api

api_token = "jalsdncoih2o342oisdcnvsl290384cvkjwmenzoxi2361298smndclzcse";
request_add_token = function (request) {
    request.setRequestHeader(
        "API-TOKEN", "jalsdncoih2o342oisdcnvsl290384cvkjwmenzoxi2361298smndclzcse"
    );
};
set_cookie=function(user_id,username,token){
    $.cookie("user_id", user_id, {"path": "/"});
    $.cookie("username",username, {"path": "/"});
    $.cookie("token", token, {"path": "/"});
}
sign_in = function () {
    console.debug("start sign in ");
    post_authentication_token(
        $("#username").val(),
        $("#password").val(),
        function (data) {
            set_cookie(data.user_id,data.username,data.token);
            window.location.replace("/index.html")
        }
    )
}

post_authentication_token = function (username, password, on_success) {
    ret_val = "";
    $.ajax({
        type: "POST",
        url: "/api/authentication-tokens",
        data: {
            "username": username,
            "password": password
        },
        beforeSend: request_add_token,
        success: on_success,
        error: function () {
            alert("Auth Error");
        }
    });
    return ret_val;
};
logout=function(){
    clean_cookie();
    window.location.replace("/");
}
clean_cookie=function(){
    $.removeCookie("user_id",{path:"/"});
    $.removeCookie("username",{path:"/"})
}
register=function(){
    post_register(
        $("#username").val(),
        $("#password").val(),
        function(data){
            alert(data.message+"\n"+"Return to login page");
            window.location.replace("/pages/login.html");
        }
    )
}

post_register = function (username, password, on_success) {
    $.ajax({
        type: "POST",
        url: "/api/users",
        beforeSend: request_add_token,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: JSON.stringify({
            Username: username,
            Password: password
        }),
        success: on_success,
        error: function(xhr,error){
            alert(error+": "+xhr);
        }
    })
};

update_account=function(){
    post_update_account(
        $("#username").val(),
        $("#password").val(),
        function(data){
            alert(data.message);
        }
    )
}

post_update_account= function (user_id, username, password, on_success) {
    $.ajax({
        type: "POST",
        url: "/api/users/"+$.cookie("user_id"),
        beforeSend: request_add_token,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: JSON.stringify({
            Username: username,
            Password: password
        }),
        success: on_success,
        error: function(xhr,error){
            alert(error+": "+xhr);
        }
    })
}


parse_predict_data = function () {

    return {
        "Identifier": parseInt($("#Identifier").val()),
        "UserID": 0,
        "Distance": parseFloat($("#Distance").val()),
        "Bedroom": parseFloat($("#Bedroom").val()),
        "Bathroom": parseFloat($("#Bathroom").val()),
        "Car": parseFloat($("#Car").val()),
        "Landsize": parseFloat($("#Landsize").val()),
        "BuildingArea": parseFloat($("#BuildingArea").val()),
        "YearBuilt": parseFloat($("#YearBuilt").val()),
        "Lattitude": parseFloat($("#Latitude").val()),
        "Longtitude": parseFloat($("#Longitude").val()),
        "Suburb": $("#Suburb").val(),
        "Street": $("#Street").val(),
        "Type": $("#Type").val(),
        "Regionname": $("#Regionname").val()
        // "Predicted_Price": 0.0,
    };
};

predict_houses_price = function () {
    return $.ajax({
        type: "POST",
        url: "/api/houses",
        data: JSON.stringify(parse_predict_data()),
        beforeSend: request_add_token,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#PredictResultTable").prepend(
                "<tr>" +
                "<td><p>" + data.HouseID + "</p></td>" +
                "<td><p>$ " + data.price + "</p></td>" +
                "</tr>"
            );
            houseid.val(parseInt(houseid.val()) + 1);
            console.log(data);
        },
        error: function (data, error) {
            alert(error + ":" + data.message);
        }
    });
};

load_feature_range = function () {
    feature_range = {};
    on_success = function (data) {
        for (var v in  data["suburb"]) {
            s += "<option>" + data["suburb"][v] + "</option>" + "\n";
        }
        $("#Suburb").html(s);
        s = ""
        for (var v in  data["street"]) {
            s += "<option>" + data["street"][v] + "</option>" + "\n";
        }
        $("#Street").html(s);
        s = ""
        for (var v in  data["region"]) {
            s += "<option>" + data["region"][v] + "</option>" + "\n";
        }
        $("#Regionname").html(s);
    };

    $.getJSON("../js/9321/data.json", on_success);
    s = ""
}
