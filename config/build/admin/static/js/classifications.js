$(document).ready(function () {
    sessionStorage.removeItem("file_path")
    sessionStorage.removeItem("table_coords");
    sessionStorage.removeItem("table_data");
    
    $(document).ajaxStart(function () {
        $("#wait2").css("display", "block");
    });

    $(document).ajaxComplete(function () {
        $("#wait2").css("display", "none");
    });

    $(".imagePlaceholer").hide();

    var token = localStorage.getItem("token");
    var password = sessionStorage.getItem("password");


        var data_attrs = {
        "token": token,
        "password": password,
        // "file_path":sessionStorage.getItem("file_path")

    };

    var success2 = {
        "url": "check_password",
        "headers": {
            "content-type": "application/json"
        },
        "method": "POST",
        "processData": false,
        "data": JSON.stringify(data_attrs)
    }

    $("#showPopup").hide();
    $.ajax(success2).done(function (data) {
        // alert(JSON.stringify(data));
        sessionStorage.setItem("file_path", data.file_path);
        console.log("check password done",data.result)
        if(data.result === true){
            // alert("next api hit")
            doc_attributes(data);
            
        }else{
            // alert("password popup");
            $('#myModal').modal('show');
            $("#showPopup").show();
        }

    }).fail(function (data) {
        console.log("check password error",data)
    });
    
    // var token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwdWJsaWNfaWQiOiJiYWxhamkuaW1hZ2VAZ21haWwuY29tIiwiZXhwIjoxNTU4NDEyNTkyfQ.QnSYNZiy03dgkCG4Jh1JkwCdtRZNteCNjl8s467JJKY";



    $('#getpasswordBtn').click(function () {
        $('#popupMessage').show();
        setTimeout(function(){ 
            $('#myModal').modal('hide');
            $('.modal-backdrop').hide();
            
         }, 1500);


        
       
        // validate signup form on keyup and submit
        $("#getPasswordForm").validate({

            rules: {
                password: "required"
            },
            messages: {
                password: "Please enter your password"


            },

            submitHandler: function (form) {

                var data_attrs = {

                    "password": document.getElementById("password").value,
                    "token": token,
                    "file_path":sessionStorage.getItem("file_path")

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

                    // console.log("readable_status", data.readable_status);
                    // sessionStorage.setItem("readable_status", readable_status);
                    // sessionStorage.setItem("reduced_percentage", reduced_percentage);
                    
                    doc_attributes_function(data);
                }).fail(function (data) {
  
                    
                });

            },


        });

    });



    function doc_attributes(data){

        var data_attrs = {
            "token": token,
            "password": password,
            "file_path":sessionStorage.getItem("file_path")
    
        };
        // alert("HI");
        $("#wait3").css("display", "block");

    console.log(JSON.stringify(data_attrs));

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
       
        doc_attributes_function(data);
        // alert("Hi");



    }).fail(function (data) {
        console.log("data", data)
        $(".imagePlaceholer").show();

        if (data.responseJSON.message == "Not successful!") {

        };

        if (data.responseJSON.message == "Token is invalid!") {

        $('#error').show();
        $("#error").text("Session expired, It will redirect to login page.", data.responseJSON.message);

            setTimeout(function () {
                window.location.href = "index.html";
            }, 2000);
            sessionStorage.removeItem("token");
            sessionStorage.clear();

        };


    });

};

function doc_attributes_function(data){

    
    $("#wait2").css("display", "none");
    $("#wait3").css("display", "none");
    $(".imagePlaceholer").show();
    console.log("data", data);

    var imageHeight = data['height']+5;
    var imagewidth = data['width'];
    var readable_status = data['readable_status'];
    var reduced_percentage = data['reduced_percentage'];
    
    // var imagewidth = data['width'];
    data = data['response'];
    var No_Quotes_string= eval(data);
    console.log("No_Quotes_string", No_Quotes_string)
    console.log("bank name", No_Quotes_string[0].bank_name)
    sessionStorage.setItem("bank_name", No_Quotes_string[0].bank_name);
    sessionStorage.setItem("readable_status", readable_status);
    sessionStorage.setItem("reduced_percentage", reduced_percentage);


    var counter11 = 1
 
    $.each(No_Quotes_string, function (obj, key, i) {

console.log("key.table_data.top", key.table_data[0].top);
     var section = $("<div class='items"+obj+"' style='position:relative; margin:50px 0px; border-bottom:2px solid #ccc; height:" + imageHeight+"px;width:" + imagewidth+"px' />");
     $(section).append("<div class='images'> <img src='" + key.corrected_imageName + "' /> <input  name='item"+ obj+".readable_status' value='"+ readable_status +" ' /> <input  name='item"+ obj+".reduced_percentage' value='"+ reduced_percentage +" ' />  <input  name='item"+ obj+".bankname' value='"+ key.bank_name +" ' /> <input  name='item"+ obj+".documentType' value='"+ key.documentType +"' /> <input   name='item"+ obj+".corrected_imageName' value='"+ key.corrected_imageName +" ' /> </div>");
     
     var table = $("<div class='table'/>");
 
     $.each(key.table_data, function(rowIndex, key, object, value) {

         console.log("rowIndex + key", rowIndex)
 
         if(rowIndex == 0 ){

             var row = $("<div class='DemoOuter"+obj+" demo' style='left:"+ key.left+"px;top:"+ key.top+"px;width:" +key.width+"px;height:"+ key.height+"px"+ " '> <input    class='height' id='height' name='item"+ obj+".table_data"+ obj+".height' value='"+ key.height +" ' /> <input    class='width' id='width' name='item"+ obj+".table_data"+ obj+".width' value='"+ key.width +" ' /> <input    class='left' id='left' name='item"+ obj+".table_data"+ obj+".left' value='"+ key.left +" ' /> <input   class='top' id='top' name='item"+ obj+".table_data"+ obj+".top' value='"+ key.top +" ' /> </div>");
             $(function () {
 
                $(".DemoOuter"+obj+"")
                    .draggable({
                       containment: $(".items"+obj+""),
                        drag: function (event) {
                            o = $(this).offset();
                            p = $(this).position();
                            $(this).children(".left").val(p.left);
                            $(this).children(".top").val(p.top);
                            
                        }
                    })
                    .resizable({
                        // handles: 's',
                        resize: function (event, ui) {
                            
                            $(this).children(".height").val($(this).outerHeight());
                            $(this).children(".width").val($(this).outerWidth());

                            console.log("11111111",($(this).outerWidth()))
                            console.log("11111111",($(this).outerHeight()))
                        }
                    });
            });            
        } else {

        };
         
         $.each(key.colItem, function(key, object, value, i) {


             row.append($("<div class='DemoInner demo' style='left:"+ object.left+"px;top:"+ object.top+"px;width:" +object.width+"px;height:"+ object.height+"px"+ " '> <input    class='height' id='height' name='item"+ obj+".table_data"+ obj+".colItem"+key+".height' value='"+ object.height +" ' /> <input    class='width' id='width' name='item"+ obj+".table_data"+ obj+".colItem"+key+".width' value='"+ object.width +" ' /> <input    class='left' id='left' name='item"+ obj+".table_data"+ obj+".colItem"+ key+".left' value='"+ object.left +" ' /> <input  class='top' id='top' name='item"+ obj+".table_data"+ obj+".colItem"+ key+".top' value='"+ object.top +" ' /> <div class='remove'>Remove</div></div>"));

             $(function () {
                $('.DemoInner')
                    .draggable({
                       containment: $(".DemoOuter0"),
                        drag: function (event) {
                            o = $(this).offset();
                            p = $(this).position();
                            $(this).children(".left").val(p.left);
                            $(this).children(".top").val(p.top);
                        }
                    })
                    .resizable({
                        handles: 's',
                        resize: function (event, ui) {
                            $(this).children(".height").val($(this).outerHeight());
                            $(this).children(".width").val($(this).outerWidth());
        
                        }
                    });

            });
         });
 
         table.append(row);
     });
     // tableDiv.append(table);

     if(obj == 0){
        
        var buttontop = key.table_data[0].top - 100;
        console.log("key.table_data.top", buttontop);
        section.append("<div class='add btn btn-warning' style='position:absolute; top:"+ buttontop+"px;'>Add Column</div> <div style='display:none' id='theCount'></div>");
    }
     
     section.append(table);
     section.append("<div class='clearfix'/>");
     $("#localization_multicol").append(section);

 });
 var counter = 100;
 $('.add').click(function() {
                counter++;
                $("#theCount").text(counter);
                var counterNew = $("#theCount").text();
                console.log("added log",counterNew);
    
                $('.items0 .demo:last').after("<div class='DemoAdded demo' style='left:50%; top:0px; width:5px; height:100%;'>  <input class='height' id='height' name='item0.table_data0.colItem"+ counterNew+".height' value='100%' /> <input    class='width' id='width' name='item0.table_data0.colItem"+ counterNew+".width' value='5px' /> <input class='left' id='left' name='item0.table_data0.colItem"+ counterNew+".left' value='100' /> <input class='top' id='top' name='item0.table_data0.colItem"+ counterNew+".top' value='0px' /> <div class='remove icon'>Remove</div></div>");
                $('.DemoAdded')
.draggable({

   containment: $(".DemoOuter0"),
    drag: function (event) {
        o = $(this).offset();
        p = $(this).position();
        $(this).children(".left").val(p.left);
        $(this).children(".top").val(p.top);
    }
})
.resizable({
    handles: 's',
    resize: function (event, ui) {
        $(this).children(".height").val($(this).outerHeight());
        $(this).children(".width").val($(this).outerWidth());
    }
});
$(".remove").click(function() {
    $(this).parent().remove();
    // alert("Removed");
});
});
        


$(".remove").click(function() {
    $(this).parent().remove();
});

}

    $("#wait5").hide();
    $('#BtnUpdateLocalizations').click(function () {

        $("#wait5").show();
        
			var obj = $("#updateLocalizations").serializeToJSON({
				parseFloat: {
					condition: ".number,.money"
                },
                useIntKeysAsArrayIndex: true
			});
            console.log(obj);
            // alert(typeof obj);
			
            var jsonString = obj;
            console.log(jsonString);
            sessionStorage.setItem("table_coords", JSON.stringify(jsonString));
			$("#result").val(jsonString);
            // alert(typeof jsonString)
            setTimeout(function () {
                window.location.href = "table_digitization.html";
            }, 3000);
        

    });

});
