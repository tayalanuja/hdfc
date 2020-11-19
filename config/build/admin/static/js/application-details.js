$(document).ready(function () {
 
  var appdetails = JSON.parse(sessionStorage.getItem("doc_attributes")); 
  
//   console.log("fecting22", appdetails.Identity.DL);

//   console.log("fecting22", appdetails.Identity.DL.CANDIDATE_NAME);
 

  if (appdetails.Identity.PAN) {
    
   $.each(appdetails.Identity.PAN, function (key, value) {

       $('#IdentityOutput1').append("<div class='row "+key+"'> <div class='col-12 col-sm-12 col-md-5 label'>"+key.replace(/_/g, " ")+"</div> <div class='col-12 col-sm-12 col-md-7'> <input type='text' class='form-control' value='"+value+"'> </div> </div> </div> </div> </div>");
       

   });
};
if (appdetails.Identity.Aadhar) {
 
   $.each(appdetails.Identity.Aadhar, function (key, value) {

       $('#IdentityOutput2').append("<div class='row "+key+"'> <div class='col-12 col-sm-12 col-md-5 label'>"+key.replace(/_/g, " ")+"</div> <div class='col-12 col-sm-12 col-md-7'> <input type='text' class='form-control' value='"+value+"'> </div> </div> </div> </div> </div>");
       

   });
};

if (appdetails.Identity.RC) {

    

   $.each(appdetails.Identity.RC, function (key, value) {
       

       $('#IdentityOutput3').append("<div class='row "+key+"'> <div class='col-12 col-sm-12 col-md-5 label'>"+key.replace(/_/g, " ")+"</div> <div class='col-12 col-sm-12 col-md-7'> <input type='text' class='form-control' value='"+value+"'> </div> </div> </div> </div> </div>");
       

   });
};

if (appdetails.Identity.DL !=undefined) {
   
   $.each(appdetails.Identity.DL, function (key, value) {
       

       $('#IdentityOutput4').append("<div class='row "+key+"'> <div class='col-12 col-sm-12 col-md-5 label'>"+key.replace(/_/g, " ")+"</div> <div class='col-12 col-sm-12 col-md-7'> <input type='text' class='form-control' value='"+value+"'> </div> </div> </div> </div> </div>");
       

   });
};

 


$('.PAN_CANDIDATE_NAME').css("display", "none");
$('.PAN_DOB').css("display", "none");
$('.DL_CANDIDATE_NAME').css("display", "none");
$('.DL_FATHER_NAME').css("display", "none");
$('.DL_DOB').css("display", "none");

$('.FILE_PATH').css("display", "none");
$('.DOC_TYPE').css("display", "none");
// $('.DOB').css("display", "none");

// $( "div" ).filter( $( ".CANDIDATE_NAME" ) );
// $( "div" ).filter( $( ".FILE_PATH" ) );
// $( "div" ).filter( $( ".CANDIDATE_NAME" ) );


// $("p.locid").filter(function() {
//     return $(this).text() == '2';
// }).eq(1).parent().hide();

});