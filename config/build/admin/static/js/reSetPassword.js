$(document).ready(function() {

  if ('tokenReset' in sessionStorage) {

  } else {

    window.location.href = 'forgot-password.html';

  };

  $('#success').hide();
  $('#error').hide();
  let token = sessionStorage.getItem('tokenReset');

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
        password: {
          minlength: 5,
        },
        cpassword: {
          minlength: 5,
          equalTo: '#password',
        },
      },
      messages: {
        password: {
          required: 'Enter a Password',
          minlength: 'Enter at least {5} characters',
        },
        cpassword: {
          required: 'Enter a Password',
          minlength: 'Enter at least {5} characters',
          equalTo: 'Please enter same password',

        },


      },

      submitHandler: function(form) {

        let data_attrs = {
          'token': token,
          'password': document.getElementById('password').value,

        };

        console.log(JSON.stringify(data_attrs));

        let success = {
          'url': 'resetpassword',
          'headers': {
            'content-type': 'application/json',

          },
          'method': 'POST',
          'processData': false,
          'data': JSON.stringify(data_attrs),
        };

        $.ajax(success).done(function(data) {

          // console.log(JSON.stringify(data));
          // console.log(JSON.stringify(data.message));
          $('#success').text(data.message);
          $('#success').show();
          sessionStorage.removeItem('tokenReset', token);

          $('#success').fadeTo(5000, 3000).slideUp(500, function() {

          });

          setTimeout(function() {
            window.location.assign('index.html');
          }, 2000);

        }).fail(function(data) {
          $('#error').show();
          $('#error').text(data.responseJSON.message);
          // console.log("Return" + JSON.stringify(data.responseJSON.message));
          // console.log(data);

          $('#error').fadeTo(5000, 3000).slideUp(500, function() {

          });

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
