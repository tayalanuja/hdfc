

$(document).ready(function() {
  $(document).ajaxStart(function() {
    $('#wait2').css('display', 'block');
    $('#mainContent').css('display', 'none');
  });

  $(document).ajaxComplete(function() {
    $('#wait2').css('display', 'none');
    $('#mainContent').css('display', 'block');
  });

  const token = localStorage.getItem('token');
  // alert(token);
  const data_attrs = {
    'token': token,

  };

  // console.log(JSON.stringify(data_attrs))

  const success = {
    'url': 'https://credit.in-d.ai/hdfc_life/payslip/admin_submitted_dashboard',
    'headers': {
      'content-type': 'application/json',

    },
    'method': 'POST',
    'processData': false,
    'data': JSON.stringify(data_attrs),
  };

  $.ajax(success).done(function(data, textStatus, xhr) {
    if (xhr.status === 200) {
      console.log('data', JSON.stringify(data));
      data = data['result'].reverse();
      console.log('confidence level', JSON.stringify(data.job_level_conf));
      $.each(data, function(i, obj) {
        console.log('job_level_conf', obj['job_level_conf']);
      });


      $('#dahsobard_table').DataTable({
        'destroy': true,
        'processing': false,
        'serverSide': false,
        'responsive': true,
        'data': data,
        'order': [[2, 'desc']],
        'columns': [
          {'data': 'batch_name'},
          {'data': 'job_id', 'class': 'job_id'},
          {'data': 'upload_date_time'},
          {'data': 'emailid'},
          {'data': 'admin_submitted', 'class': 'job_status2'},
          {'data': 'job_id',
            'searchable': false,
            'render': function(data, type, row) {
              return '<a href="salary-slip-review.html?job_id=' + data +'&emailid=' + row.emailid+'" class="btn Complete">Procceed</a>';
            },
          },
        ],

        'bLengthChange': false, // thought this line could hide the LengthMenu
        'bInfo': false,
        'searching': false,
      });

      // $("td:contains(Complete)").addClass("complete");
      // $("td:contains(In Queue)").addClass("queued");
      // $("td:contains(In Process)").addClass("process");

      // $("td.job_status.complete").html('<a href="review.html" onclick="ShowModalAssets(this);"><button class="btn btn-primary">View</button></a>');
      // $("td.job_status.queued").html('<button class="btn btn-disable" disabled>View</button>');
      // $("td.job_status.process").html('<button class="btn btn-disable" disabled>View</button>');
    } else if (xhr.status === 201) {
      alert(JSON.stringify(data.message));
      // location.reload();
    } else {
      alert(JSON.stringify(data.message));
      // location.reload();
    }
  }).fail(function(data) {
    $('#error').show();
    $('#error').text(data.responseJSON.message);

    if (data.responseJSON.message=='Token is invalid!') {
      setTimeout(function() {
        // alert("Hi")
        window.location.assign('index.html')
      }, 2000);
      localStorage.removeItem('token');
      sessionStorage.clear();
    };
  });

  $('#autoRefresh').click( function() {
    setTimeout(function() {
      $('#autoRefresh').trigger('click');
      //    alert("Hi");
    }, 40000);

    // alert("Hi");

    const success = {
      'url': 'https://credit.in-d.ai/hdfc_life/payslip/admin_dashboard',
      'headers': {
        'content-type': 'application/json',

      },
      'method': 'POST',
      'processData': false,
      'data': JSON.stringify(data_attrs),
    };

    $.ajax(success).done(function(data) {
      // alert(data[0].message);
      // console.log(JSON.stringify(data));

      data = data['result'];
      // console.log(JSON.stringify(data));

      $('#dahsobard_table').DataTable({
        'destroy': true,
        'responsive': true,
        'processing': false,
        'serverSide': false,
        'data': data,
        'columns': [
          {'data': 'job_id', 'class': 'job_id1'},
          {'data': 'document_name'},
          {'data': 'upload_date_time'},
          {'data': 'job_size'},
          {'data': 'job_priority'},
          {'data': 'job_status'},
          {'data': 'job_status', 'class': 'job_status2'},
          {'data': 'job_status', 'class': 'job_status'},

        ],
        'columnDefs': [{
          'targets': -1,
          'data': 'job_id',
          'render': function(data, type, row, meta) {
            return '<button onclick="ShowModalAssets(this);" class="btn ' + data + '" >' + data + '</button>';
          },
        },

        ],
        'bLengthChange': false, // thought this line could hide the LengthMenu
        'bInfo': false,
        'searching': false,
      });

      // $("td:contains(Complete)").addClass("complete");
      // $("td:contains(In Queue)").addClass("queued");
      // $("td:contains(In Process)").addClass("process");

      // $("td.job_status.complete").html('<a href="review.html" onclick="ShowModalAssets(this);"><button class="btn btn-primary">View</button></a>');
      // $("td.job_status.queued").html('<button class="btn btn-disable" disabled>View</button>');
      // $("td.job_status.process").html('<button class="btn btn-disable" disabled>View</button>');
    }).fail(function(data) {
      $('#error').show();
      $('#error').text(data.responseJSON.message);

      if (data.responseJSON.message=='Token is invalid!') {
        setTimeout(function() {
          // alert("hi")
          window.location.href='index.html';
        }, 2000);
        localStorage.removeItem('token');
        sessionStorage.clear();
      };
    });
  });

  setTimeout(function() {
    $('#autoRefresh').trigger('click');
    // alert("Hi");
  }, 40000);
});


function ShowModalAssets(ths) {
  const job_id = $(ths).parent().parent().find('.job_id1').text();
  const job_status2 = $(ths).parent().parent().find('.job_status2').text();

  if (job_status2=='Complete') {
    window.location.href='review.html?id=' + job_id;
    sessionStorage.setItem('job_id', job_id);
  } else if (job_status2=='In Queue') {

  } else {


  };
};

function job_level_confidance(ths) {
  alert();
  const job_id = $(ths).parent().parent().find('.job_id1').text();
  const job_status2 = $(ths).parent().parent().find('.job_status2').text();
};


