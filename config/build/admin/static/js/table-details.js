$(document).ready(function() {
  $(document).ajaxStart(function() {
    $('#wait2').css('display', 'block');
    $('.tablePlaceholerDetails').css('display', 'none');
  });

  $(document).ajaxComplete(function() {
    $('#wait2').css('display', 'none');
    $('.tablePlaceholerDetails').css('display', 'block');
  });

  const url_string = window.location.href;
  const url = new URL(url_string);
  const job_id = url.searchParams.get('job_id');
  console.log(job_id);

  $('#upload_documents').attr('href', 'dashboard.html?job_id='+job_id);
  $('#localization').attr('href', 'localization.html?job_id='+job_id);
  $('#digitization').attr('href', 'table_digitization.html?job_id='+job_id);
  $('#download').attr('href', 'download_data.html?job_id='+job_id);
  $('#calcutions').attr('href', 'calculations.html?job_id='+job_id);

  // table_data = sessionStorage.getItem("table_data");
  // table_data_obj = JSON.parse(table_data)

  const data_attrs = sessionStorage.getItem('table_data');
  // var data_attrs = JSON.parse(table_data);
  // alert(typeof data_attrs)
  // var data_attrs2 = JSON.parse(data_attrs)
  const bank_name = sessionStorage.getItem('bank_name');
  // alert(bank_name)
  // alert (typeof data_attrs2)

  //   let data_attrs2 = [
  //     {'bank_name': bank_name},
  //     {'file_path': sessionStorage.getItem('file_path')},
  //     {'table_data': JSON.parse(data_attrs)}];

  const token = localStorage.getItem('token');

  const data_attrs2 = {
    'token': token,
    'job_id': job_id,
  };

  const success = {
    'url': 'https://credit.in-d.ai/hdfc_life/credit/table_data',
    'headers': {
      'content-type': 'application/json',
    },
    'method': 'POST',
    'processData': false,
    'data': JSON.stringify(data_attrs2),
  };

  // console.log(JSON.stringify(data_attrs2));

  $.ajax(success).done(function(data, textStatus, xhr) {
    if (xhr.status === 200) {
    // alert(data.download_CSV)
      $('#downloadCSV').attr('href', data.download_CSV);
      sessionStorage.setItem('download_CSV', data.download_CSV);
      // console.log(data)
      console.log('data.excel', JSON.parse(data.excel));
      sessionStorage.setItem('bank_type', data.bank_type);


      const section = $('<div class=\'items\'/>');
      const tableDiv = $('<div class=\'table\'/>');
      const table = $('<table border=\'1\' collapse=\'10\'/>');
      $.each(JSON.parse(data.excel), function(object, key, value, rowIndex) {
        console.log(object);
        console.log(key);
        console.log(value);


        // var excel_data = JSON.parse(key.excel_data);
        // $.each(excel_data, function (rowIndex, key, object, value) {
        const row = $('<tr/>');
        $.each(key, function(colIndex, c) {
          if (rowIndex == 0) {
            row.append($('<t' + (rowIndex == 0 ? 'h' : 'd') + ' width=\'100px\' />').text(c));
          } else {
            row.append($('<t' + (rowIndex == 0 ? 'h' : 'd') + ' width=\'100px\' />').text(c));
          }
        });
        table.append(row);
      // });
      });

      tableDiv.append(table);
      section.append(tableDiv);
      section.append('<div class=\'clearfix\'/>');
      $('#data_table').append(section);
    } else if (xhr.status === 201) {
      alert(JSON.stringify(data.message));
      // location.reload();
    } else {
      alert(JSON.stringify(data.message));
      // location.reload();
    }
  }).fail(function(data) {
    console.log('data', data);
  });

  $('#BtnUpdatetableDetaills').click(function() {
    // sessionStorage.removeItem("table_data");

    setTimeout(function() {
      window.location.href = 'calculations.html?job_id='+job_id;
    }, 1000);
  });
});
