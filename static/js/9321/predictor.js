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
    $.cookie("user_id", user_id, { "path": "/" });
    $.cookie("username", username, { "path": "/" });
    $.cookie("token", token, { "path": "/" });
}
function userid() {
    return parseInt($.cookie("user_id"));
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
    $.removeCookie("user_id", { path: "/" });
    $.removeCookie("username", { path: "/" })
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

load_suburb = function () {
    on_success = function (data) {
        s = '<option value="all">ALL Suburb</option>'
        for (var v in data["suburb"]) {
            s += "<option>" + data["suburb"][v] + "</option>" + "\n";
        }
        $("#Suburb").html(s)
    }

    $.getJSON("../js/9321/data.json", on_success);
}

load_feature_range = function () {
    feature_range = {};
    on_success = function (data) {
        for (var v in data["suburb"]) {
            s += "<option>" + data["suburb"][v] + "</option>" + "\n";
        }
        $("#Suburb").html(s)
            .val("")
        s = ""
        for (var v in data["street"]) {
            s += "<option>" + data["street"][v] + "</option>" + "\n";
        }
        $("#Street").html(s)
            .val("")
        s = ""
        for (var v in data["region"]) {
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
show_average_chart = function () {
    parse_graph_data_and_draw = function (data) {
        years = [];
        prices = [];
        $.each(data, function (i) {
            prices.push(data[i].Price);
            years.push(parseInt(data[i].year));
        })
        console.log(years);
        console.log(prices);
        drawChart(years, prices);
    }
    data = {};
    if ($("#Suburb").val() == "all") {
        data["graph service"] = "graph1"
    } else {

        data["graph service"] = "graph2";
        data["suburb"] = $("#Suburb").val();
    }

    data["year"] = parseInt($("#Year").val())
    data["UserID"] = userid();
    $.ajax({
        type: "GET",
        url: "/api/graphs",
        data: data,
        success: parse_graph_data_and_draw
    }

    )
    // $("#Suburb").val();

}

show_lowest_chart = function () {
    parse_graph_data_and_draw = function (data) {
        suburbs = [];
        prices = [];
        $.each(data, function (i) {
            prices.push(data[i].Price);
            suburbs.push(data[i].suburb);
        })
        // console.log(years);
        // console.log(prices);
        drawChart(suburbs, prices);
    }
    data = {};
    data["graph service"] = "graph3";
    data["distance"] = parseFloat($("#Distance").val());
    data["UserID"] = userid();
    $.ajax({
        type: "GET",
        url: "/api/graphs",
        data: data,
        success: parse_graph_data_and_draw,
        error: function (xhr, err) {
            alert(JSON.parse(xhr.responseText)["message"]);
        }
    }

    )
    // $("#Suburb").val();

}

drawChart = function (x, y) {
    var dom = document.getElementById("myChart");
    var myChart = echarts.init(dom);
    var app = {};
    option = null;
    var dataAxis = x;
    var data = y;
    var yMax = Math.max(data) * 1.2;
    var dataShadow = [];

    for (var i = 0; i < data.length; i++) {
        dataShadow.push(yMax);
    }

    option = {
        /*
        title: {
            text: '特性示例：渐变色 阴影 点击缩放',
            subtext: 'Feature Sample: Gradient Color, Shadow, Click Zoom'
        },*/
        xAxis: {
            data: dataAxis,
            axisLabel: {
                inside: true,
                textStyle: {
                    color: '#fff'
                }
            },
            axisTick: {
                show: false
            },
            axisLine: {
                show: false
            },
            z: 10
        },
        yAxis: {
            axisLine: {
                show: false
            },
            axisTick: {
                show: false
            },
            axisLabel: {
                textStyle: {
                    color: '#999'
                }
            }
        },
        dataZoom: [
            {
                type: 'inside'
            }
        ],
        series: [
            { // For shadow
                type: 'bar',
                itemStyle: {
                    normal: { color: 'rgba(0,0,0,0.05)' }
                },
                barGap: '-100%',
                barCategoryGap: '40%',
                data: dataShadow,
                animation: false
            },
            {
                type: 'bar',
                itemStyle: {
                    normal: {
                        color: new echarts.graphic.LinearGradient(
                            0, 0, 0, 1,
                            [
                                { offset: 0, color: '#83bff6' },
                                { offset: 0.5, color: '#188df0' },
                                { offset: 1, color: '#188df0' }
                            ]
                        )
                    },
                    emphasis: {
                        color: new echarts.graphic.LinearGradient(
                            0, 0, 0, 1,
                            [
                                { offset: 0, color: '#2378f7' },
                                { offset: 0.7, color: '#2378f7' },
                                { offset: 1, color: '#83bff6' }
                            ]
                        )
                    }
                },
                data: data
            }
        ]
    };

    // Enable data zoom when user click bar.
    var zoomSize = 6;
    // myChart.on('click', function (params) {
    //     console.log(dataAxis[Math.max(params.dataIndex - zoomSize / 2, 0)]);
    //     myChart.dispatchAction({
    //         type: 'dataZoom',
    //         startValue: dataAxis[Math.max(params.dataIndex - zoomSize / 2, 0)],
    //         endValue: dataAxis[Math.min(params.dataIndex + zoomSize / 2, data.length - 1)]
    //     });
    // });;
    if (option && typeof option === "object") {
        myChart.setOption(option, true);
    }
}

show_api_usage= function () {
    parse_graph_data_and_draw = function (data) {
        data2=[]
        $.each(data, function (i) {
            data2.push(
                {
                    value:data[i].Count,
                    name:data[i].Operation,
                }
            )

        })
        draw_pie_chart(data2);
    }
    data = {};
    data["graph service"] = "graph3";
    data["distance"] = parseFloat($("#Distance").val());
    data["UserID"] = userid();
    $.ajax({
        type: "GET",
        url: "/api/APIUsage",
        data: data,
        success: parse_graph_data_and_draw,
        error: function (xhr, err) {
            alert(JSON.parse(xhr.responseText)["message"]);
        }
    }

    )
    // $("#Suburb").val();

}

draw_pie_chart = function (data) {
    
    var dom = document.getElementById("myChart");
    var myChart = echarts.init(dom);
    var app = {};
    option = null;
    legend_data=[]
    $.each(data,function(i){
        legend_data.push(data[i].Operation);
    })
    option = {
        title: {
            text: 'API Usage',
            // subtext: '纯属虚构',
            x: 'center'
        },
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            x: 'center',
            y: 'bottom',
            data: legend_data,
        },
        toolbox: {
            show: true,
            feature: {
                mark: { show: true },
                dataView: { show: true, readOnly: false },
                magicType: {
                    show: true,
                    type: ['pie', 'funnel']
                },
                restore: { show: true },
                saveAsImage: { show: true }
            }
        },
        calculable: true,
        series: [

            {
                name: '',
                type: 'pie',
                radius: [50, 200],
                center: ['50%', '50%'],
                roseType: 'radius',
                data: data
            }
        ]
    };
    ;
    if (option && typeof option === "object") {
        myChart.setOption(option, true);
    }


}