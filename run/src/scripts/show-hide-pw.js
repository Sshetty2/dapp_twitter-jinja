
jQuery(document).ready(function(){


// Show password Button
$("#showpassword").on('click', function(){
    
    var pass = $("#password");
    var fieldtype = pass.attr('type');
    if (fieldtype == 'password') {
        pass.attr('type', 'text');
        $(this).text("Hide Password");
    }else{
        pass.attr('type', 'password');
        $(this).text("Show Password");
    }


});

});
