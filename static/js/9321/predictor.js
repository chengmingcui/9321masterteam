// for login and predict api
show_header_user_name = function () {
    $("#header_user_name").ready(function () {

        $("#header_user_name").html($.cookie("username"))
    })
}
api_token = "jalsdncoih2o342oisdcnvsl290384cvkjwmenzoxi2361298smndclzcse";
request_add_token = function (request) {
    request.setRequestHeader(
        "API-TOKEN", "jalsdncoih2o342oisdcnvsl290384cvkjwmenzoxi2361298smndclzcse"
    );
};
set_cookie = function (user_id, username, token) {
    $.cookie("user_id", user_id, {"path": "/"});
    $.cookie("username", username, {"path": "/"});
    $.cookie("token", token, {"path": "/"});
}
sign_in = function () {
    console.debug("start sign in ");
    post_authentication_token(
        $("#username").val(),
        $("#password").val(),
        function (data) {
            set_cookie(data.user_id, data.username, data.token);
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
logout = function () {
    clean_cookie();
    window.location.replace("/");
}
clean_cookie = function () {
    $.removeCookie("user_id", {path: "/"});
    $.removeCookie("username", {path: "/"})
}
register = function () {
    post_register(
        $("#username").val(),
        $("#password").val(),
        function (data) {
            alert(data.message + "\n" + "Return to login page");
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
        error: function (xhr, error) {
            alert(error + ": " + xhr);
        }
    })
};

update_account = function () {
    post_update_account(
        $("#username").val(),
        $("#password").val(),
        function (data) {
            alert(data.message);
        }
    )
}

post_update_account = function (user_id, username, password, on_success) {
    $.ajax({
        type: "POST",
        url: "/api/users/" + $.cookie("user_id"),
        beforeSend: request_add_token,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: JSON.stringify({
            Username: username,
            Password: password
        }),
        success: on_success,
        error: function (xhr, error) {
            alert(error + ": " + xhr);
        }
    })
}

col = ["Identifier", "Predicted_Price", "Distance", "Bedroom", "Bathroom", "Car", "Landsize", "BuildingArea", "YearBuilt", "Lattitude", "Longtitude", "Suburb", "Street", "Type", "Regionname"]

clear_predict_input = function () {
    $.each(col, function (i) {
        $("#" + col[i]).val("")
            .removeClass("form-control-warning");
    })
    return false;
}

parse_predict_data = function () {

    ret_val = {
        "Identifier": parseInt($("#Identifier").val()),
        "UserID": parseInt($.cookie("user_id")),
        "Distance": parseFloat($("#Distance").val()),
        "Bedroom": parseFloat($("#Bedroom").val()),
        "Bathroom": parseFloat($("#Bathroom").val()),
        "Car": parseFloat($("#Car").val()),
        "Landsize": parseFloat($("#Landsize").val()),
        "BuildingArea": parseFloat($("#BuildingArea").val()),
        "YearBuilt": parseFloat($("#YearBuilt").val()),
        "Lattitude": parseFloat($("#Lattitude").val()),
        "Longtitude": parseFloat($("#Longtitude").val()),
        "Suburb": $("#Suburb").val(),
        "Street": $("#Street").val(),
        "Type": $("#Type").val(),
        "Regionname": $("#Regionname").val()
        // "Predicted_Price": 0.0,
    };
    first = -1;
    $.each(ret_val, function (k) {
        if (ret_val[k] == null || (($.type(ret_val[k]) == "string" && ret_val[k].length == 0) || ($.type(ret_val[k]) != "string" && isNaN(ret_val[k])))) {
            if (-1 == first) {
                first = $("#" + k);
            }
            ;
            $("#" + k).addClass("form-control-warning")
        } else {
            $("#" + k).removeClass("form-control-warning")
        }
    });
    if (first != -1) {
        first.focus();
        $("body,html").animate({
            scrollTop: first.offset.top //让body的scrollTop等于pos的top，就实现了滚动
        })

        throw "Some Feature empty";
    }
    return ret_val;
};

predict_houses_price = function () {
    data = parse_predict_data();
    $.ajax({
            type: "POST",
            url: "/api/houses",
            data: JSON.stringify(data),
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
                houseid = $("#Identifier");
                houseid.val(parseInt(houseid.val()) + 1);
                console.log(data);
            },
            error: function (jqXHR, error) {
                if (jqXHR.status === 0) {
                    alert('Not connect.\n Verify Network.');
                } else if (jqXHR.status == 400) {
                    alert(JSON.parse(jqXHR.responseText).message);
                } else if (jqXHR.status == 404) {
                    alert('Requested page not found. [404]');
                } else if (jqXHR.status == 500) {
                    alert('Internal Server Error [500].');
                } else if (exception === 'parsererror') {
                    alert('Requested JSON parse failed.');
                } else if (exception === 'timeout') {
                    alert('Time out error.');
                } else if (exception === 'abort') {
                    alert('Ajax request aborted.');
                } else {
                    alert('Uncaught Error.\n' + jqXHR.responseText);
                }
            }
        }
    )
    ;
    return false;
}
;

load_suburb=function(){
    on_success = function (data) {
        for (var v in  data["suburb"]) {
            s += "<option>" + data["suburb"][v] + "</option>" + "\n";
        }
        $("#Suburb").html(s)
    }

    $.getJSON("../js/9321/data.json", on_success);
}

load_feature_range = function () {
    feature_range = {};
    on_success = function (data) {
        for (var v in  data["suburb"]) {
            s += "<option>" + data["suburb"][v] + "</option>" + "\n";
        }
        $("#Suburb").html(s)
            .val("")
        s = ""
        for (var v in  data["street"]) {
            s += "<option>" + data["street"][v] + "</option>" + "\n";
        }
        $("#Street").html(s)
            .val("")
        s = ""
        for (var v in  data["region"]) {
            s += "<option>" + data["region"][v] + "</option>" + "\n";
        }
        $("#Regionname").html(s)
            .val("")
    };

    $.getJSON("../js/9321/data.json", on_success);
    s = ""
}

get_house_table = function (user_id, on_success) {
    $.ajax({
        "type": "GET",
        url: "/api/houses",
        beforeSend: request_add_token,
        data: {
            UserID: user_id
        },
        success: on_success,
    })
}
show_house_table_head_foot = function () {
    col = ["Identifier", "Predicted_Price", "Distance", "Bedroom", "Bathroom", "Car", "Landsize", "BuildingArea", "YearBuilt", "Lattitude", "Longtitude", "Suburb", "Street", "Type", "Regionname"]
    thead = $("#simpletable> thead > tr ");
    tfoot = $("#simpletable> tfoot > tr");
    // head_row = $();
    thead.html("");
    tfoot.html("");
    for (var col_idx in col) {
        s = "<th>" + col[col_idx] + "</th>>";
        thead.append(s);
        // tfoot.append(s);
    }
}
show_house_table_data = function () {
    user_id = parseInt($.cookie("user_id"));
    col = ["Identifier", "Predicted_Price", "Distance", "Bedroom", "Bathroom", "Car", "Landsize", "BuildingArea", "YearBuilt", "Lattitude", "Longtitude", "Suburb", "Street", "Type", "Regionname"]
    tbody = $("#simpletable> tbody");
    tbody.html("");
    $.ajax({
        "type": "GET",
        url: "/api/houses",
        beforeSend: request_add_token,
        data: {
            UserID: user_id
        },
        success: function (data) {
            console.log(data);
            $.each(data, function (i) {
                new_tr = "<tr>";
                $.each(col, function (j) {
                    new_tr += ("<td>" + data[i][col[j]] + "</td>\n")
                });
                new_tr += "</tr>";
                tbody.append(new_tr);
            })
        },
        error: function (xhr, error) {
            tbody.html("<tr>There is no house<tr>");
            console.log(xhr);
            console.log(error);
        }
    })
}

// get_graph1_data()
