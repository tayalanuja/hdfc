$(document).ready(function () {
    sessionStorage.removeItem('table_coords');
    sessionStorage.removeItem('table_data');

    // $(document).ajaxStart(function () {
    //     $("#wait2").css("display", "block");
    // });

    // $(document).ajaxComplete(function () {
    //     $("#wait2").css("display", "none");
    // });

    $('.imagePlaceholer').hide();

    const url_string = window.location.href;
    const url = new URL(url_string);
    const job_id = url.searchParams.get('job_id');
    const emailid = url.searchParams.get('emailid');
    console.log(job_id + " emailid " + emailid);

    $('#upload_documents').attr('href', 'dashboard-salaryslip.html?job_id=' + job_id);
    $('#localization').attr('href', 'localization.html?job_id=' + job_id);
    $('#digitization').attr('href', 'table_digitization.html?job_id=' + job_id);
    $('#download').attr('href', 'download_data.html?job_id=' + job_id);
    $('#calcutions').attr('href', 'calculations.html?job_id=' + job_id);

    const token = localStorage.getItem('token');
    const data_attrs = {
        'token': token,
        'job_id': job_id,
        'user_email': emailid,

    };

    doc_attributes(data_attrs);

});

// if ("localization_data" in sessionStorage) {

//     data = sessionStorage.getItem("localization_data");
//     // console.log("data", data);

//     data = JSON.parse(data);
//     doc_attributes_function(data);


// } else {
//     // alert("No");

//     sessionStorage.removeItem("file_path");

//     var data_attrs = {
//         "token": token,
//         "password": password,

//     };

//     var success2 = {
//         "url": "check_password",
//         "headers": {
//             "content-type": "application/json"
//         },
//         "method": "POST",
//         "processData": false,
//         "data": JSON.stringify(data_attrs)
//     }

//     $("#showPopup").hide();
//     $.ajax(success2).done(function (data) {
//         sessionStorage.setItem("file_path", data.file_path);
//         console.log("check password done", data.result)
//         if (data.result === true) {
//             doc_attributes(data);

//         } else {
//             $('#myModal').modal('show');
//             $("#showPopup").show();
//         }

//     }).fail(function (data) {
//         console.log("check password error", data)
//     });

// };

// $('#getpasswordBtn').click(function () {
//     $('#popupMessage').show();
//     setTimeout(function () {
//         $('#myModal').modal('hide');
//         $('.modal-backdrop').hide();

//     }, 1500);


//   let data = {
//     'file_path': sessionStorage.getItem('file_path'),
//     'doc_type': sessionStorage.getItem('doc_type'),
//     'bank_name': sessionStorage.getItem('bank_name'),
//     'readable_status': sessionStorage.getItem('readable_status'),
//   };

// //   doc_attributes(data);


// eslint-disable-next-line require-jsdoc
function doc_attributes(data_attrs) {

    $('#wait3').css('display', 'block');

    console.log('doc_attributes', JSON.stringify(data_attrs));

    const success = {
        'url': 'https://credit.in-d.ai/hdfc_life/payslip/admin_review_job',
        'headers': {
            'content-type': 'application/json',
        },
        'method': 'POST',
        'processData': false,
        'data': JSON.stringify(data_attrs),
    };

    $.ajax(success).done(function (data, textStatus, xhr) {
        // alert("HI")

        if (xhr.status === 200) {
            sessionStorage.setItem('localization_data', JSON.stringify(data));
            doc_attributes_function(data);
        } else if (xhr.status === 201) {
            alert(data.message);
        } else {

        }
    }).fail(function (data) {
        console.log('data', data);
        $('.imagePlaceholer').show();

        if (data.responseJSON.message == 'Not successful!') {

        };

        if (data.responseJSON.message == 'Token is invalid!') {
            $('#error').show();
            $('#error').text('Session expired, It will redirect to login page.', data.responseJSON.message);

            setTimeout(function () {
                window.location.assign('index.html');
            }, 2000);
            localStorage.removeItem('token');
            sessionStorage.clear();
        };
    });

};


function doc_attributes_function(data) {
    $('#wait2').css('display', 'none');
    $('#wait3').css('display', 'none');
    $('.imagePlaceholer').show();

    console.log('doc_attributes_function', data.result.length);
    console.log('doc_attributes_function', data.result);

    const imageHeight = data['height'] + 5;
    const imagewidth = data['width'];
    const readable_status = data['readable_status'];
    const reduced_percentage = data['reduced_percentage'];
    data = data.result;

    const No_Quotes_string = eval(data);
    console.log('No_Quotes_string', No_Quotes_string);
    CreateMenu(No_Quotes_string)

    const newinputs = []
    newinputs.push(No_Quotes_string[0])
    CreateInputs(newinputs, imageHeight, imagewidth)

}

function CreateInputs(No_Quotes_string, imageHeight, imagewidth) {
    // $('.items.row').empty()
    // $('.images').empty()
    // $('.table').empty()
    $('#localization_multicol').empty()




    $.each(No_Quotes_string, function (obj, key, i) {
        console.log('No_Quotes_string', No_Quotes_string);
        // console.log('key.image_path', key.image_path);

        console.log('key.file_name', key.file_name);


        console.log('No_Quotes_string file_name', No_Quotes_string[0].fields);
        // alert(key.file_name)
        // menuItem.push({"file_name":key.file_name, "email_id":key.email_id})
        $("#localization_multicol").append('<h3>Total documents -' + No_Quotes_string[0].fields.length + '</h3>')
        $.each(No_Quotes_string[0].fields, function (rowIndex, key, object, value) {

            console.log('key.rowIndex', rowIndex);
            console.log('key.key', key);
            console.log('key.object', object);
            console.log('key.value', value);

            console.log('key.inv_level_conf', key.inv_level_conf);
            // console.log('key.table_data.top', key.fields[0].Result);
            const section = $('<div class=\'items row ' + obj + '\' style=\'position:relative; padding:25px 0px; margin:0px; border:0px; height:' + imageHeight + 'px;width:' + imagewidth + 'px\' />');


            $(section).append('<div class=\'images col-7 col-md-7 \'>  <img src=\'https://credit.in-d.ai/hdfc_life/' + key.file_name + '\' /></div>');
            const table = $('<div class=\'table\'/>');
            const form = $('<form class="col-5 col-md-5" id="updateLocalizations'+rowIndex+'" action="#" />');
            
            table.append(`<input type="text" class="form-control"  value="${key.file_name}" name="file_name" hidden />`);

            $.each(key.Result, function (rowIndex, key, object, value) {
                console.log('rowIndex + rowIndex', rowIndex);
                console.log('rowIndex + key', key);
                // console.log('rowIndex + object', object);
                // console.log('rowIndex + value', value);

                var row = $('<div class="form-group"></div>');
                row.append($(`
                <label for="exampleInputEmail1">${key.label}</label>
                <input type="text" class="form-control"  value="${key.value}" name="text_fields[${rowIndex}].value"  />
                <input type="text" class="form-control"  value="${key.order_id}" name="text_fields[${rowIndex}].id" hidden />
                <input type="text" class="form-control"  value="${key.label}"name="text_fields[${rowIndex}].label" hidden />
                <input type="text" class="form-control"  value="${key.varname}" name="text_fields[${rowIndex}].varname" hidden />
            `));
                table.append(row);
            });


            form.append(table);
            section.append(form);
            section.append('<div class=\'clearfix\'/>');
            table.append(`<div class="clearfix"></div>
                            <div class="footerBtn">
                            <button type="button" class="btn btn-primary pull-right" id="BtnUpdateLocalizations${rowIndex}"> <img src="./static/images/loader2.gif" style="display:none" id="wait5" class="loader" /> Submit</button>
                    </div>`)

            $('#localization_multicol').append(section);
            $('#BtnUpdateLocalizations'+rowIndex).click(function () {
                $('#wait5').show();
                // alert(rowIndex)
                const url_string = window.location.href;
                const url = new URL(url_string);
                const job_id = url.searchParams.get('job_id');
                const emailid = url.searchParams.get('emailid');

                console.log(job_id);

                const obj = $('#updateLocalizations'+rowIndex).serializeToJSON({
                    parseFloat: {
                        condition: '.number,.money',
                    },
                    useIntKeysAsArrayIndex: true,
                    associativeArrays: false
                });
                console.log("obj", obj);
                const text_fields = obj.text_fields;
                console.log("text_fields", JSON.stringify(text_fields));

                const dataNew = {
                    "token": localStorage.getItem('token'),
                    "user_email": emailid,
                    "job_id": job_id,
                    "file_name": obj.file_name,
                    text_fields
                }

                console.log("dataNew", JSON.stringify(dataNew));

                // /payslip/admin_validate

                const success = {
                    'url': 'https://credit.in-d.ai/hdfc_life/payslip/admin_validate',
                    'headers': {
                        'content-type': 'application/json',
                    },
                    'method': 'POST',
                    'processData': false,
                    'data': JSON.stringify(dataNew),
                };

                $.ajax(success).done(function (data, textStatus, xhr) {
                    // alert("HI")
                    $('#wait5').hide();

                    if (xhr.status === 200) {
                        alert(data.message);
                    } else if (xhr.status === 201) {
                        alert(data.message);
                    } else {
                        alert(data.message);
                    }
                }).fail(function (data) {
                    console.log('data', data);
                    $('#wait5').hide();

                    if (data.responseJSON.message == 'Not successful!') {

                    };

                    if (data.responseJSON.message == 'Token is invalid!') {
                        $('#error').show();
                        $('#error').text('Session expired, It will redirect to login page.', data.responseJSON.message);

                        setTimeout(function () {
                            window.location.assign('index.html');
                        }, 2000);
                        localStorage.removeItem('token');
                        sessionStorage.clear();
                    };
                });


            });
        });
    });
}

function CreateMenu(No_Quotes_string) {

    let menuItem = $('<div class="menuItem"></div>')

    $.each(No_Quotes_string, function (obj, key, i) {
        console.log('key.email_id', key.email_id);
        console.log('key.image_path', key.image_path);

        console.log('key.file_name', key.file_name);
        // menuItem.push({"file_name":key.file_name, "email_id":key.email_id})

        menuItem.append($(`
                <div class="menuItemLink" data-file_name="${key.file_name}">${key.file_name}</label>
            `));

    });
    console.log("menuItem", menuItem)
    $("#menuWrapper").append(menuItem)
    $("#menuWrapper").append('<button type="button" class="btn btn-primary pull-right" id="BtnUpdateLocalizations"> <img src="./static/images/loader2.gif" style="display:none" id="wait6" class="loader" /> Submit Batch</button>')

    

    $(".menuItemLink").click(function () {
        const text = $(this).attr("data-file_name")
        //   alert(text)

        let bigCities = No_Quotes_string.filter(item => item.file_name == text);
        console.log("bigCities", bigCities);
        const imageHeight = undefined;
        const imagewidth = undefined;

        CreateInputs(bigCities, imageHeight, imagewidth)


    });

    $('#BtnUpdateLocalizations').click(function () {
        // alert("Hi")
        $('#wait6').show();
        const url_string = window.location.href;
        const url = new URL(url_string);
        const job_id = url.searchParams.get('job_id');
        const emailid = url.searchParams.get('emailid');
        console.log(job_id);
    
        const dataNew = {
            "token": localStorage.getItem('token'),
            "user_email": emailid,
            "job_id": job_id,
        }
    
        console.log("dataNew", JSON.stringify(dataNew));
    
        // /payslip/admin_validate
    
        const success = {
            'url': 'https://credit.in-d.ai/hdfc_life/payslip/admin_submit',
            'headers': {
                'content-type': 'application/json',
            },
            'method': 'POST',
            'processData': false,
            'data': JSON.stringify(dataNew),
        };
    
        $.ajax(success).done(function (data, textStatus, xhr) {
            // alert("HI")
            $('#wait6').hide();
    
            if (xhr.status === 200) {
                alert(data.message);
                setTimeout(function () {
                    window.location.assign('dashboard-salaryslip.html')
                }, 1000);
            } else if (xhr.status === 201) {
                alert(data.message);
            } else {
                alert(data.message);
            }
        }).fail(function (data) {
            console.log('data', data);
            $('#wait6').hide();
    
            setTimeout(function () {
                window.location.assign('dashboard-salaryslip.html')
            }, 1000);
    
            if (data.responseJSON.message == 'Not successful!') {
                
            };
    
            if (data.responseJSON.message == 'Token is invalid!') {
                $('#error').show();
                $('#error').text('Session expired, It will redirect to login page.', data.responseJSON.message);
    
                setTimeout(function () {
                    window.location.assign('index.html');
                }, 2000);
                localStorage.removeItem('token');
                sessionStorage.clear();
            };

        });
    });

}



$('#wait5').hide();



// });
