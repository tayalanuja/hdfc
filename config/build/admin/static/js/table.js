$(document).ready(function() {
  $(document).ajaxStart(function() {
    $('#wait2').css('display', 'block');
  });

  $(document).ajaxComplete(function() {
    $('#wait2').css('display', 'none');
  });


  table_coords = sessionStorage.getItem('table_coords');

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

  // var data_attrs = JSON.parse(table_coords);
  const data_attrs = {
    'table_coords': JSON.parse(table_coords),
    'token': token,
    'job_id': job_id,
  };

  const success = {
    'url': 'https://credit.in-d.ai/hdfc_life/credit/table_digitization',
    'headers': {
      'content-type': 'application/json',
    },
    'method': 'POST',
    'processData': false,
    'data': JSON.stringify(data_attrs),
  };

  console.log(JSON.stringify(data_attrs));

  $.ajax(success).done(function(data, textStatus, xhr) {
    if (xhr.status === 200) {
    // console.log(data)
    // console.log("data", JSON.stringify(data));

      sessionStorage.setItem('table_data', JSON.stringify(data));
      const table_data = sessionStorage.getItem('table_data');

      // console.log(table_data);


      $.each(data.response, function(object, key, value) {
        console.log('key', key);
        const section = $('<div class=\'items\'/>');
        $(section).append('<div class=\'images\'> <img src=\'https://credit.in-d.ai/hdfc_life/' + key.image_path + '\' /></div>');
        const tableDiv = $('<div class=\'table\'/>');
        const table = $('<table border=\'1\' collapse=\'10\'/>');

        // var excel_data = eval(key.excel_data);
        const excel_data = JSON.parse(key.excel_data);

        $.each(excel_data, function(rowIndex, key, object, value) {
          const row = $('<tr/>');
          $.each(key, function(colIndex, c) {
            console.log('rowIndex', colIndex);
            console.log('c', c);
            if (rowIndex == 0) {
            //    alert("HI")
              row.append($('<t' + (rowIndex == 0 ? 'h' : 'd') + '/>').text(c));
            } else {
              row.append($('<t' + (rowIndex == 0 ? 'h' : 'd') + '/>').text(c));
            }
          });
          table.append(row);
        });
        tableDiv.append(table);
        section.append(tableDiv);
        section.append('<div class=\'clearfix\'/>');
        $('#data_table').append(section);
      });
    } else if (xhr.status === 201) {
      alert(JSON.stringify(data.message));
      // location.reload();
    } else {
      alert(JSON.stringify(data.message));
      // location.reload();
    }
  }).fail(function(data) {
    console.log('data', data);
    $('.imagePlaceholer').show();
  });


  $('#BtnUpdatetable').click(function() {
    setTimeout(function() {
      window.location.href = 'download_data.html?job_id='+job_id;
    }, 1000);
  });
});
