$(document).ready(function () {

    var token = localStorage.getItem("token");
    var data_attrs = {
        "token": token,

    };

    var success = {
        "url": "updateprofile",
        "headers": {
            "content-type": "application/json"
        },
        "method": "POST",
        "processData": false,
        "data": JSON.stringify(data_attrs)
    }

    $.ajax(success).done(function (data) {
        // console.log(JSON.stringify(data));

        data = data['result'];
        // console.log(JSON.stringify(data));

        $("#firstname").val(data[0].firstname);
        $("#lastname").val(data[0].lastname);
        $("#password").val(data[0].password);
        $("#cpassword").val(data[0].password);
        $("#emailid").val(data[0].emailid);
        $("#phone").val(data[0].phone);
        $("#jobtitle").val(data[0].jobtitle);
        $("#companyname").val(data[0].companyname);
        $("#question").val(data[0].question);
        $('#answer').val(data[0].answer);

    }).fail(function (data) {

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




    $('#registerBtn').click(function () {

        $("#regsiterForm").validate({

            rules: {
                firstname: "required",
                lastname: "required",
                password: {
                    minlength: 5
                },
                cpassword: {
                    minlength: 5,
                    equalTo: "#password"
                },
                emailid: "required",
                phone: "required",
                companyname: "required",
                jobtitle: "required",
                question: "required",
                answer: "required"
            },
            messages: {
                firstname: "Please enter your first name",
                lastname: "Please enter your last name",
                password: {
                    required: "Enter a username",
                    minlength: "Enter at least {5} characters"
                },
                cpassword: {
                    required: "Enter a username",
                    minlength: "Enter at least {5} characters",
                    equalTo: "Please enter same password"

                },
                emailid: "Please enter your email id",
                phone: "Please enter your phone number",
                companyname: "Please enter your Company name",
                jobtitle: "Please enter your job title",
                question: "Please select your question",
                answer: "Please enter your answer"
            },

            submitHandler: function (form) {

                var data_attrs = {
                    "token": token,
                    "firstname": document.getElementById("firstname").value,
                    "lastname": document.getElementById("lastname").value,
                    "password": document.getElementById("password").value,
                    "emailid": document.getElementById("emailid").value,
                    "phone": document.getElementById("phone").value,
                    "companyname": document.getElementById("companyname").value,
                    "jobtitle": document.getElementById("jobtitle").value,
                    "question": document.getElementById("question").value,
                    "answer": document.getElementById("answer").value

                };
                console.log(JSON.stringify(data_attrs))

                var success = {
                    "url": "updateuser",
                    "headers": {
                        "content-type": "application/json"


                    },
                    "method": "POST",
                    "processData": false,
                    "data": JSON.stringify(data_attrs)
                }

                $.ajax(success).done(function (data) {

                    // console.log("Return" + JSON.stringify(data));
                    $('#success').show();
                    $("#success").text(data.message);
                    $("#regsiterForm").trigger("reset");
                    // console.log("Return" + JSON.stringify(data.message));
                    sessionStorage.removeItem("token");
                    setTimeout(function () {
                        window.location.href = "index.html";
                    }, 1500);


                }).fail(function (data) {

                    $('#error').show();

                    $("#error").text(data.statusText);
                    // console.log("Return" + JSON.stringify(data.responseJSON.message));
                    // console.log(data);
                    // console.log("show error " + data.responseText);
                    console.log("Data" + JSON.stringify(data));
                    // $("#regsiterForm").trigger("reset");
                    // console.log("Return" + JSON.parse(data.message));
                    if (data.responseJSON.message == "Token is invalid!") {
                        setTimeout(function () {
                            window.location.href = "index.html";
                        }, 2000);
                        sessionStorage.removeItem("token");
                        sessionStorage.clear();
                    };
                });
            },
        });
    });
});