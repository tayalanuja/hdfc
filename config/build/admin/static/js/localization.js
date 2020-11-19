$(document).ready(function() {
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
  console.log(job_id);

  $('#upload_documents').attr('href', 'dashboard.html?job_id='+job_id);
  $('#localization').attr('href', 'localization.html?job_id='+job_id);
  $('#digitization').attr('href', 'table_digitization.html?job_id='+job_id);
  $('#download').attr('href', 'download_data.html?job_id='+job_id);
  $('#calcutions').attr('href', 'calculations.html?job_id='+job_id);

  const token = localStorage.getItem('token');
  const data_attrs = {
    'token': token,
    'job_id': job_id,
  };

  doc_attributes(data_attrs);

  $('#wait3').css('display', 'block');

  // const success2 = {
  //   'url': 'https://credit.in-d.ai/hdfc_life/credit/pdf_password_localization_status',
  //   'headers': {
  //     'content-type': 'application/json',
  //   },
  //   'method': 'POST',
  //   'processData': false,
  //   'data': JSON.stringify(data_attrs),
  // };

  // $('#showPopup').hide();
  // $.ajax(success2).done(function(data, textStatus, xhr) {
  //   console.log('xhr, textStatus', data, textStatus, xhr, xhr.status);

  //   $('#wait3').css('display', 'none');

  //   if (xhr.status === 200) {
  //     // sessionStorage.setItem('file_path', data.file_path);
  //     // console.log('check password done', data.result);
  //     doc_attributes(data_attrs);
  //     // alert("DOne")
  //   } else if (xhr.status === 201) {
  //     alert(data.message);
  //   } else {

  //   }
  // }).fail(function(data) {
  //   alert(data);
  //   console.log('check password error', data);
  // });
  
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
//   const data_attrs = {
//     'token': token,
//     // "password": password,
//     'file_path': sessionStorage.getItem('file_path'),
//     'doc_type': sessionStorage.getItem('doc_type'),
//     'bank_name': sessionStorage.getItem('bank_name'),
//     'readable_status': sessionStorage.getItem('readable_status'),

  //   };

  $('#wait3').css('display', 'block');

  console.log('doc_attributes', JSON.stringify(data_attrs));

  const success = {
    'url': 'https://credit.in-d.ai/hdfc_life/credit/table_localization',
    'headers': {
      'content-type': 'application/json',
    },
    'method': 'POST',
    'processData': false,
    'data': JSON.stringify(data_attrs),
  };

  $.ajax(success).done(function(data, textStatus, xhr) {
    // alert("HI")

    if (xhr.status === 200) {
      sessionStorage.setItem('localization_data', JSON.stringify(data));
      doc_attributes_function(data);
    } else if (xhr.status === 201) {
      alert(data.message);
    } else {

    }
  }).fail(function(data) {
    console.log('data', data);
    $('.imagePlaceholer').show();

    if (data.responseJSON.message == 'Not successful!') {

    };

    if (data.responseJSON.message == 'Token is invalid!') {
      $('#error').show();
      $('#error').text('Session expired, It will redirect to login page.', data.responseJSON.message);

      setTimeout(function() {
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
  console.log('data', data);

  const imageHeight = data['height'] + 5;
  const imagewidth = data['width'];
  const readable_status = data['readable_status'];
  const reduced_percentage = data['reduced_percentage'];
  data = data['response'];
  const No_Quotes_string = eval(data);
  console.log('No_Quotes_string', No_Quotes_string);
  console.log('bank name', No_Quotes_string[0].bank_name);
  sessionStorage.setItem('bank_name', No_Quotes_string[0].bank_name);
  sessionStorage.setItem('readable_status', readable_status);
  sessionStorage.setItem('reduced_percentage', reduced_percentage);


  const counter11 = 1;

  $.each(No_Quotes_string, function(obj, key, i) {
    console.log('key.table_data.top', key.table_data[0].top);
    const section = $('<div class=\'items' + obj + '\' style=\'position:relative; margin:50px 0px; border-bottom:2px solid #ccc; height:' + imageHeight + 'px;width:' + imagewidth + 'px\' />');
    $(section).append('<div class=\'images\'> <img src=\'https://credit.in-d.ai/hdfc_life/' + key.corrected_imageName + '\' /> <input  name=\'item' + obj + '.bankname\' value=\'' + key.bank_name + ' \' /> <input  name=\'item' + obj + '.documentType\' value=\'' + key.documentType + '\' /> <input   name=\'item' + obj + '.corrected_imageName\' value=\'' + key.corrected_imageName + ' \' /> </div>');

    const table = $('<div class=\'table\'/>');

    $.each(key.table_data, function(rowIndex, key, object, value) {
      console.log('rowIndex + key', rowIndex);

      if (rowIndex == 0) {
        var row = $('<div class=\'DemoOuter' + obj + ' demo\' style=\'left:' + key.left + 'px;top:' + key.top + 'px;width:' + key.width + 'px;height:' + key.height + 'px' + ' \'> <input    class=\'height\' id=\'height\' name=\'item' + obj + '.table_data' + obj + '.height\' value=\'' + key.height + ' \' /> <input    class=\'width\' id=\'width\' name=\'item' + obj + '.table_data' + obj + '.width\' value=\'' + key.width + ' \' /> <input    class=\'left\' id=\'left\' name=\'item' + obj + '.table_data' + obj + '.left\' value=\'' + key.left + ' \' /> <input   class=\'top\' id=\'top\' name=\'item' + obj + '.table_data' + obj + '.top\' value=\'' + key.top + ' \' /> </div>');


        $(function() {
          $('.DemoOuter' + obj + '')
              .draggable({

                containment: $('.items' + obj + ''),
                drag: function(event) {
                  o = $(this).offset();
                  p = $(this).position();

                  $(this).children('.left').val(p.left);
                  $(this).children('.top').val(p.top);
                },
              })
              .resizable({
                resize: function(event, ui) {
                  $(this).children('.height').val($(this).outerHeight());
                  $(this).children('.width').val($(this).outerWidth());

                  console.log('11111111', ($(this).outerWidth()));
                  console.log('11111111', ($(this).outerHeight()));
                },
              });
        });
      } else {


      };

      $.each(key.colItem, function(key, object, value, i) {
        row.append($('<div class=\'DemoInner demo\' style=\'left:' + object.left + 'px;top:' + object.top + 'px;width:' + object.width + 'px;height:' + object.height + 'px' + ' \'> <input    class=\'height\' id=\'height\' name=\'item' + obj + '.table_data' + obj + '.colItem' + key + '.height\' value=\'' + object.height + ' \' /> <input    class=\'width\' id=\'width\' name=\'item' + obj + '.table_data' + obj + '.colItem' + key + '.width\' value=\'' + object.width + ' \' /> <input    class=\'left\' id=\'left\' name=\'item' + obj + '.table_data' + obj + '.colItem' + key + '.left\' value=\'' + object.left + ' \' /> <input  class=\'top\' id=\'top\' name=\'item' + obj + '.table_data' + obj + '.colItem' + key + '.top\' value=\'' + object.top + ' \' /> <div class=\'remove\'>Remove</div></div>'));


        $(function() {
          $('.DemoInner')
              .draggable({

                containment: $('.DemoOuter0'),
                drag: function(event) {
                  o = $(this).offset();
                  p = $(this).position();

                  $(this).children('.left').val(p.left);
                  $(this).children('.top').val(p.top);
                },
              })
              .resizable({
                handles: 's',
                resize: function(event, ui) {
                  $(this).children('.height').val($(this).outerHeight());
                  $(this).children('.width').val($(this).outerWidth());
                },
              });
        });
      });

      table.append(row);
    });
    // tableDiv.append(table);

    if (obj == 0) {
      const buttontop = key.table_data[0].top - 100;
      console.log('key.table_data.top', buttontop);
      section.append('<div class=\'add btn btn-warning\' style=\'position:absolute; top:' + buttontop + 'px;\'>Add Column</div> <div style=\'display:none\' id=\'theCount\'></div>');
    }

    section.append(table);
    section.append('<div class=\'clearfix\'/>');
    $('#localization_multicol').append(section);
  });
  let counter = 100;
  $('.add').click(function() {
    counter++;
    $('#theCount').text(counter);
    const counterNew = $('#theCount').text();
    console.log('added log', counterNew);

    $('.items0 .demo:last').after('<div class=\'DemoAdded demo\' style=\'left:50%; top:0px; width:5px; height:100%;\'>  <input class=\'height\' id=\'height\' name=\'item0.table_data0.colItem' + counterNew + '.height\' value=\'100%\' /> <input    class=\'width\' id=\'width\' name=\'item0.table_data0.colItem' + counterNew + '.width\' value=\'5px\' /> <input class=\'left\' id=\'left\' name=\'item0.table_data0.colItem' + counterNew + '.left\' value=\'100\' /> <input class=\'top\' id=\'top\' name=\'item0.table_data0.colItem' + counterNew + '.top\' value=\'0px\' /> <div class=\'remove icon\'>Remove</div></div>');


    $('.DemoAdded')
        .draggable({

          containment: $('.DemoOuter0'),
          drag: function(event) {
            o = $(this).offset();
            p = $(this).position();
            $(this).children('.left').val(p.left);
            $(this).children('.top').val(p.top);
          },
        })
        .resizable({
          handles: 's',
          resize: function(event, ui) {
            $(this).children('.height').val($(this).outerHeight());
            $(this).children('.width').val($(this).outerWidth());
          },
        });
    $('.remove').click(function() {
      $(this).parent().remove();
    });
  });


  $('.remove').click(function() {
    $(this).parent().remove();
  });
}

$('#wait5').hide();
$('#BtnUpdateLocalizations').click(function() {
  $('#wait5').show();
  const url_string = window.location.href;
  const url = new URL(url_string);
  const job_id = url.searchParams.get('job_id');
  console.log(job_id);

  const obj = $('#updateLocalizations').serializeToJSON({
    parseFloat: {
      condition: '.number,.money',
    },
    useIntKeysAsArrayIndex: true,
  });
  console.log(obj);
  const jsonString = obj;
  console.log(jsonString);
  sessionStorage.setItem('table_coords', JSON.stringify(jsonString));
  $('#result').val(jsonString);
  setTimeout(function() {
    window.location.href = 'table_digitization.html?job_id='+job_id;
  }, 3000);
});

// });
