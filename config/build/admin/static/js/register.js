$(document).ready(function() {
  $('#success').hide();
  $('#error').hide();

  $(document).ajaxStart(function() {
    $('#wait2').css('display', 'block');
  });

  $(document).ajaxComplete(function() {
    $('#wait2').css('display', 'none');
  });


  $('#registerBtn').click(function() {
    $('#regsiterForm').validate({

      rules: {
        firstname: 'required',
        lastname: 'required',
        password: {
          required: true,
          minlength: 5,
        },
        cpassword: {
          required: true,
          minlength: 5,
          equalTo: '#password',
        },
        emailid: 'required',
        phone: 'required',
        companyname: 'required',
        jobtitle: 'required',
        question: 'required',
        answer: 'required',
      },
      messages: {
        firstname: 'Please enter your first name',
        lastname: 'Please enter your last name',
        password: {
          required: 'Please enter your password',
          minlength: 'Your password must be at least 8 characters long',
        },
        cpassword: {
          required: 'Please enter your confirm password',
          minlength: 'Your password must be at least 8 characters long',
          equalTo: 'Please enter same Password',

        },
        emailid: 'Please enter your email id',
        phone: 'Please enter your phone number',
        companyname: 'Please enter your company name',
        jobtitle: 'Please enter your job title',
        question: 'Please select your question',
        answer: 'Please enter your answer',
      },

      submitHandler: function(form) {
        const data_attrs = {

          'firstname': document.getElementById('firstname').value,
          'lastname': document.getElementById('lastname').value,
          'password': document.getElementById('password').value,
          'emailid': document.getElementById('emailid').value,
          'phone': document.getElementById('phone').value,
          'companyname': document.getElementById('companyname').value,
          'jobtitle': document.getElementById('jobtitle').value,
          'question': document.getElementById('question').value,
          'answer': document.getElementById('answer').value,

        };
        console.log(JSON.stringify(data_attrs));

        const success = {
          'url': 'https://credit.in-d.ai/hdfc_life/credit/admin_register',
          'headers': {
            'content-type': 'application/json',


          },
          'method': 'POST',
          'processData': false,
          'data': JSON.stringify(data_attrs),
        };

        $.ajax(success).done(function(data, textStatus, xhr) {
          if (xhr.status === 200) {
            console.log('Return' + JSON.stringify(data));
            $('#success').show();
            $('#success').text(data.message);
            $('#regsiterForm').trigger('reset');
            // console.log("Return" + JSON.stringify(data.message));

            $('#success').fadeTo(5000, 3000).slideUp(500, function() { });
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
