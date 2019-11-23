// for login and predict api

api_token = "jalsdncoih2o342oisdcnvsl290384cvkjwmenzoxi2361298smndclzcse";
request_add_token = function (request) {
    request.setRequestHeader(
        "API-TOKEN", "jalsdncoih2o342oisdcnvsl290384cvkjwmenzoxi2361298smndclzcse"
    );
};
sign_in = function () {
    console.debug("start sign in ");
    post_authentication_token(
        $("#username").val(),
        $("#password").val(),
        function () {
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
        fail: function () {
            alert("Auth Error");
        }
    });
    return ret_val;
};

parse_parse_data=function(){

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
        "Type":$("#Type").val(),
        "Regionname":$("#Regionname").val(),
        "Predicted_Price":0.0,
    };
};

predict = function () {
    post_houses_predict(parse_parse_data(),function (data) {
        console.log(data);
    })
}

post_houses_predict = function (data, on_success) {
    $.ajax({
        type: "POST",
        url: "/api/houses",
        data: data,
        beforeSend: request_add_token,
        success: on_success,
    });
};

load_feature_range = function () {
    feature_range = {};
    on_success=function(data){
        for (var  v in  data["suburb"]){
            s+="<option>"+data["suburb"][v]+"</option>"+"\n";
        }
        $("#Suburb").html(s);
        s=""
        for (var  v in  data["street"]){
            s+="<option>"+data["street"][v]+"</option>"+"\n";
        }
        $("#Street").html(s);
        s=""
        for (var  v in  data["region"]){
            s+="<option>"+data["region"][v]+"</option>"+"\n";
        }
        $("#Regionname").html(s);
    };

    $.getJSON("../js/9321/data.json", on_success);
    s=""
}
