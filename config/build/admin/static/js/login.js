$(document).ready(function() {
  $('#success').hide();
  $('#error').hide();
  sessionStorage.clear();

  $(document).ajaxStart(function() {
    $('#wait2').css('display', 'block');
  });

  $(document).ajaxComplete(function() {
    $('#wait2').css('display', 'none');
  });


  $('#loginBtn').click(function() {
    $('#loginForm').validate({

      rules: {
        emailid: 'required',
        password: {
          minlength: 5,
        },
      },
      messages: {
        emailid: 'Please enter your Email ID',
        password: {
          required: 'Please enter your Password',
          minlength: 'Your password must be at least 8 characters long',
        },


      },

      submitHandler: function(form) {
        const data_attrs = {


          'emailid': document.getElementById('emailid').value,
          'password': document.getElementById('password').value,

        };

        const success = {

          'url': 'https://credit.in-d.ai/hdfc_life/credit/admin_login',
          'headers': {
            'content-type': 'application/json',
          },
          'method': 'POST',
          'processData': false,
          'data': JSON.stringify(data_attrs),

        };

        $.ajax(success).done(function(data, textStatus, xhr) {
          if (xhr.status === 200) {
            // alert(JSON.stringify(data));


            // console.log(JSON.stringify(data));
            // console.log(JSON.stringify(data.token));
            const token2 = JSON.stringify(data.token);
            const token = token2.slice(1, -1);

            $('#success').fadeTo(5000, 3000).slideUp(500, function() {

            });


            var firstname = JSON.stringify(data.firstname);
            localStorage.setItem('token', token);

            var firstname = JSON.stringify(data.firstname);
            var firstname = firstname.slice(1, -1);
            sessionStorage.setItem('firstname', firstname);
            window.location.href = 'main-dashboard.html';
          } else if (xhr.status === 201) {

            alert(JSON.stringify(data.message));
            // location.reload();

          } else {

            alert(JSON.stringify(data.message));
            // location.reload();

          }
        }).fail(function(data, textStatus, xhr) {
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
