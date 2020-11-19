$(document).ready(function() {

  $('#success').hide();
  $('#error').hide();

  $(document).ajaxStart(function() {
    $('#wait2').css('display', 'block');
  });

  $(document).ajaxComplete(function() {
    $('#wait2').css('display', 'none');
  });


  $('#forgotpasswordBtn').click(function() {

    // validate signup form on keyup and submit
    $('#forgotpasswordForm').validate({

      rules: {
        emailid: 'required',
      },
      messages: {
        emailid: 'Please enter your Email ID',


      },

      submitHandler: function(form) {

        let data_attrs = {

          'emailid': document.getElementById('emailid').value,

        };

        console.log(JSON.stringify(data_attrs));

        let success = {
          'url': 'forgotpassword',
          'headers': {
            'content-type': 'application/json',

          },
          'method': 'POST',
          'processData': false,
          'data': JSON.stringify(data_attrs),
        };

        $.ajax(success).done(function(data) {
          // console.log(JSON.stringify(data));
          // console.log(JSON.stringify(data.token));
          let token2 = JSON.stringify(data.token);
          let token = token2.slice(1, -1);

          localStorage.setItem('tokenReset', token);
          setTimeout(function() {
            window.location.href = 'reset-password.html';
          }, 2000);
          $('#success').fadeTo(5000, 3000).slideUp(500, function() { });

        }).fail(function(data) {
          $('#error').show();
          $('#error').text(data.responseJSON.message);
          $('#error').fadeTo(5000, 3000).slideUp(500, function() {
            $('#error').slideUp(500);
          });
          // console.log("Return" + JSON.stringify(data.responseJSON.message));
          // console.log(data);
          // $("#regsiterForm").trigger("reset");
          // console.log("Return" + JSON.parse(data.message));

          if (data.responseJSON.message == 'Token is invalid!') {
            setTimeout(function() {
              window.location.assign('index.html');
            }, 2000);
            localStorage.removeItem('token');
            sessionStorage.clear();

          };
        });

      },


    });

  });


});
