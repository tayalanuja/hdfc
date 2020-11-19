$(document).ready(function () {

    $(".parentHorizontalTab").hide();
    $(".Identity").hide();
    $(".Income").hide();
    $(".Unknown").hide();

    $("#IdentityWrapper").hide();
    $("#IncomeWrapper").hide();
    $("#UnknownWrapper").hide();

    
    
    
    
    $(document).ajaxStart(function () {
        $("#wait2").css("display", "block");
    });

    $(document).ajaxComplete(function () {
        $("#wait2").css("display", "none");
    });


    var token = localStorage.getItem("token");
    var data_attrs = {
        "token": token,

    };

    console.log(JSON.stringify(data_attrs))

    var success = {
        "url": "doc_attributes",
        "headers": {
            "content-type": "application/json"
        },
        "method": "POST",
        "processData": false,
        "data": JSON.stringify(data_attrs)
    }

    $.ajax(success).done(function (data) {
        $(".parentHorizontalTab").show();

        //console.log("1",JSON.stringify(data));

        data = data['result'];
        console.log("Full data", JSON.stringify(data));
        //console.log("Income", JSON.stringify(data.Income));

        sessionStorage.setItem("doc_attributes", JSON.stringify(data));
        

        $.each(data, function (key, value) {
            console.log("Key",key);
            // console.log("value",value);
            // console.log("value PAN",value.PAN);
            // console.log("value Aadhar",value.Aadhar);
            // console.log("value DL",data.Identity.PAN);
            // console.log("Income",data.Income);
            // var keyIdentity = key.Identity.length;
            // console.log(keyIdentity)
            // if (key.Identity == undefined) {
            //     $(".Identity").show();
            //     $("#IdentityWrapper").show();

            // };

            if (key == "Identity") {
                $(".Identity").show();
                $("#IdentityWrapper").show();

         if (data.Identity.PAN != undefined) {
            //  alert("pann");
            $.each(data.Identity.PAN, function (key, value) {
                $("#job_details1").css("display", "block");
                $('#IdentityOutput1').append("<div class='row "+key+"'> <div class='col-12 col-sm-12 col-md-5 label'>"+key.replace(/_/g, " ")+"</div> <div class='col-12 col-sm-12 col-md-7'> <input type='text' class='form-control' value='"+value+"'> </div> </div> </div> </div> </div>");
                if (key == "FILE_PATH") {
                    $(".FILE_PATH").hide();
                    $(".imagePath").attr('src',value);
                };
                if (key == "DOC_TYPE") {
                    $(".title1").text(value);
                };

            });
        };
        if (data.Identity.Aadhar!= undefined) {
            // alert("Aadhar");
            $.each(data.Identity.Aadhar, function (key, value) {
                $("#job_details2").css("display", "block");
                $('#IdentityOutput2').append("<div class='row "+key+"'> <div class='col-12 col-sm-12 col-md-5 label'>"+key.replace(/_/g, " ")+"</div> <div class='col-12 col-sm-12 col-md-7'> <input type='text' class='form-control' value='"+value+"'> </div> </div> </div> </div> </div>");
                if (key == "FILE_PATH") {
                    $(".FILE_PATH").hide();
                    $(".imagePath2").attr('src',value);
                };
                if (key == "DOC_TYPE") {
                    $(".title2").text(value);
                };

            });
        };
        if (data.Identity.RC!= undefined) {

            // alert("RC");

            $.each(data.Identity.RC, function (key, value) {
                $("#job_details3").css("display", "block");

                $('#IdentityOutput3').append("<div class='row "+key+"'> <div class='col-12 col-sm-12 col-md-5 label'>"+key.replace(/_/g, " ")+"</div> <div class='col-12 col-sm-12 col-md-7'> <input type='text' class='form-control' value='"+value+"'> </div> </div> </div> </div> </div>");
                if (key == "FILE_PATH") {
                    $(".FILE_PATH").hide();
                    $(".imagePath3").attr('src',value);
                };
                if (key == "DOC_TYPE") {
                    $(".title3").text(value);
                };

            });
        };
        
        if (data.Identity.DL!= undefined) {
            // alert("DL");
            $.each(data.Identity.DL, function (key, value) {
                
                
                $("#job_details4").css("display", "block");
                $('#IdentityOutput4').append("<div class='row "+key+"'> <div class='col-12 col-sm-12 col-md-5 label'>"+key.replace(/_/g, " ")+"</div> <div class='col-12 col-sm-12 col-md-7'> <input type='text' class='form-control' value='"+value+"'> </div> </div> </div> </div> </div>");
                if (key == "FILE_PATH") {
                    $(".FILE_PATH").hide();
                    $(".imagePath4").attr('src',value);
                   

                };
                if (key == "DOC_TYPE") {
                    $(".title4").text(value);
                };

            });
        };



            };

            // console.log("data.Income", data.Income);

            if (data.Income != undefined) {
                // alert("Income");
                $.each(data.Income, function (key, value) {
                    // console.log("key", key);
                    // console.log("value", value)
                    // $("#job_details4").css("display", "block");
                    $('#FinancialStatement').append("<tr class='"+key+"'> <td class='labelFormat'> "+key.replace(/_/g, " ")+"</td> <td><input type='text' class='form-control' value='"+value+"'></td> </tr>");
                    if (key == "FILE_PATH") {
                        $(".FILE_PATH").hide();
                        $("#FinancialStatementImage").attr('src',value);
                       
    
                    };
                    if (key == "DOC_TYPE") {
                        $(".title4").text(value);
                    };
    
                });
            };



            if (key == "Income") {
                $(".Income").show();
                $("#IncomeWrapper").show();
    
            };

            if (key == "Unknown") {
                alert("Unknown Found")
                $(".Unknown").show();
                $("#UnknownWrapper").show();
            };

           
        });

    }).fail(function (data) {
        // alert("error")
  
        // window.location.assign("upload_documents.html");
        $('#error').show();
        $("#error").text("Session expired, please wait 2 min, it will redirect to login page.", data.responseJSON.message);

        if (data.responseJSON.message == "Token is invalid!") {

            setTimeout(function () {
                window.location.href = "index.html";
            }, 2000);
            sessionStorage.removeItem("token");
            sessionStorage.clear();

        };


    });

});