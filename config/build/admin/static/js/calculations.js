$(document).ready(function () {
  const download_CSV = sessionStorage.getItem('download_CSV');
  const bank_name = sessionStorage.getItem('bank_name');
  const bank_type = sessionStorage.getItem('bank_type');
  const word_order = sessionStorage.getItem('word_order');
  const text = JSON.parse(sessionStorage.getItem('text'));


  const file_path = sessionStorage.getItem('file_path');

  // var data_attrs2 = [{ "bank_name": bank_name }, { "csv_path": download_CSV }, { "bank_type": bank_type }, { "file_path": file_path },{ "text": text },{"word_order":word_order}]
  //   let data_attrs2 = [{'bank_name': bank_name, 'csv_path': download_CSV, 'bank_type': bank_type, 'file_path': file_path,'text': text,'word_order': word_order}];

  // var download_CSV = sessionStorage.getItem("download_CSV")
  $('#downloadCSV').attr('href', download_CSV);


  const url_string = window.location.href;
  const url = new URL(url_string);
  const job_id = url.searchParams.get('job_id');
  console.log(job_id);

  $('#upload_documents').attr('href', 'dashboard.html?job_id=' + job_id);
  $('#localization').attr('href', 'localization.html?job_id=' + job_id);
  $('#digitization').attr('href', 'table_digitization.html?job_id=' + job_id);
  $('#download').attr('href', 'download_data.html?job_id=' + job_id);
  $('#calcutions').attr('href', 'calculations.html?job_id=' + job_id);

  const token = localStorage.getItem('token');

  const data_attrs2 = {
    'token': token,
    'job_id': job_id,
  };


  const success = {
    'url': 'https://credit.in-d.ai/hdfc_life/credit/calculations_result',
    'headers': {
      'content-type': 'application/json',
    },
    'method': 'POST',
    'processData': false,
    'data': JSON.stringify(data_attrs2),
  };

  $.ajax(success).done(function (data, textStatus, xhr) {
    if (xhr.status === 200) {
      console.log("data.pdf_file_path", data.pdf_file_path);
      console.log("data.result", data.result);
      // console.log("data.result['Total amount spent through payment gateways']", data.result['Total amount spent through payment gateways']);
      // console.log("data.result[0]",data.result[0]);


      // alert(typeof data.result)

      $('.pdfPath').attr('src', "https://credit.in-d.ai/hdfc_life/" + data.pdf_file_path);
      $('#downloadCSV2').attr('href', "https://credit.in-d.ai/hdfc_life" + data.calculation_csv_path);     



      if(typeof data.result == 'string'){

        
        var newdata = data.result.replace(/'/g, '"');
        console.log("adasdasda asdasdasd", newdata);

        var newObjData= JSON.parse(newdata);

        console.log("obj", newObjData);

        // alert(typeof data.result)
        // const dataparse = JSON.parse(data.result)
        // alert(dataparse['01. Account Holder'])
        // var newdata = data.result;
        // alert(eval(data.result))
        // var No_Quotes_string= JSON.parse(newdata);
        
        // "Account Holder": "RATHOD CHATURIBEN RATILALBHAI",
        // "Account Opening Date": "02-03-2020",
        // "Monthly Average Balance": "5555555",
        // "Total Salary": "0",
        // "Type of Account": "Individual Account"

        // alert(No_Quotes_string)
        $('#account_holder').val(newObjData['Account Holder']);
        $('#total_salary').val(newObjData['Total Salary']);
        $('#type_of_account').val(newObjData['Type of Account']);
        $('#account_opening_date').val(newObjData['Account Opening Date']);
        $('#monthly_average_balance').val(newObjData['Monthly Average Balance']);

      } else {


        $('#account_holder').val(data.result['Account Holder']);
        $('#total_salary').val(data.result['Total Salary']);
        $('#type_of_account').val(data.result['Type of Account']);
        $('#account_opening_date').val(data.result['Account Opening Date']);
        $('#monthly_average_balance').val(data.result['Monthly Average Balance']);

      }

    } else if (xhr.status === 201) {
      alert(JSON.stringify(data.message));
      // // location.reload();
    } else {
      alert(JSON.stringify(data.message));
      // // location.reload();
    }
  }).fail(function (data) {
    console.log('data', data);
  });

  $('#BtnUpdatetableDetaills').click(function () {
    sessionStorage.removeItem('table_data');

    setTimeout(function () {
      window.location.href = 'calculations.html';
    }, 1000);
  });




  $('#validate').click(function () {

    // alert("Hi")

    const data = {
      'token': token,
      "job_id": job_id,
      "Account Opening Date": $('#account_opening_date').val(),
      "Account Holder": $('#account_holder').val(),
      "Type of Account": $('#type_of_account').val(),
      "Total Salary": $('#total_salary').val(),
      "Monthly Average Balance": $('#monthly_average_balance').val(),
      "comment": $('#comments').val(),
    }

    const success = {
      'url': 'https://credit.in-d.ai/hdfc_life/credit/admin_validate',
      'headers': {
        'content-type': 'application/json',
      },
      'method': 'POST',
      'processData': false,
      'data': JSON.stringify(data),
    };

    $.ajax(success).done(function (data, textStatus, xhr) {
      console.log("data.pdf_file_path", data.message);
      
      

      if (xhr.status === 200) {
        alert(data.message)
        window.location.assign('dashboard.html')

      } else if (xhr.status === 201) {
        alert(JSON.stringify(data.message));
        // // location.reload();
      } else {
        alert(JSON.stringify(data.message));
        // // location.reload();
      }

    }).fail(function (data) {
      console.log('data', data);
    });
  });
});
