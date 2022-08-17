
function reset_form ( )
{
    USERNAME_MSG.html( "" );
    USERNAME_MSG.hide();
    PASSWORD_MSG.html( "" );
    PASSWORD_MSG.hide();
    CONFIRM_MSG.html( "" );
    CONFIRM_MSG.hide();
    LNAME_MSG.html( "" );
    LNAME_MSG.hide();
    FNAME_MSG.html( "" );
    FNAME_MSG.hide();
    EMAIL_MSG.html( "" );
    EMAIL_MSG.hide();
    SUBMIT.show();
}

function validate ( )
{
    let valid = true;
    reset_form ( );
    SUBMIT.hide();
    var letters = /^[A-Za-z]+$/;
    var decimal =  /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s)$/;
    if ( !USERNAME.val() || USERNAME.val().length < 10 || !USERNAME.value.match(letters) )
    {
        USERNAME_MSG.html( "Username must only be 10 characters and contain letters!" );
        USERNAME_MSG.show();
        valid = false;
    }


    if ( USERNAME.val() != USERNAME.val().toLowerCase())
    {
        USERNAME_MSG.html("Username must be in lowercase");
        USERNAME_MSG.show();
        valid = false;
    }

    if ( !PASSWORD.val() || PASSWORD.val().length < 12 || !PASSWORD.value.match(decimal) )
    {
        PASSWORD_MSG.html("Password needs to be at least 12 characters long and must contains lowercase letters, uppercase letters, numbers and special characters ");
        PASSWORD_MSG.show();
        valid = false;
    }

    if ( !CONFIRM.val() || PASSWORD.val() != CONFIRM.val() )
    {
        CONFIRM_MSG.html("Passwords must match!");
        CONFIRM_MSG.show();
        valid = false;
    }

    if ( !FNAME.val() || !FNAME.value.match(letters))
    {
        FNAME_MSG.html("Field must only contain letters and must not be empty!");
        FNAME_MSG.show();
        valid = false;
    }

    if ( !LNAME.val() || !LNAME.value.match(letters))
    {
        LNAME_MSG.html("Field must only contain letters and must not be empty!");
        LNAME_MSG.show();
        valid = false;
    }

    var x = EMAIL.val().trim();
    var atpos = x.indexOf("@");
    var dotpos = x.lastIndexOf(".");
    if ( atpos < 1 || dotpos < atpos + 2 || dotpos + 2 >= x.length ) {
        EMAIL_MSG.html("You need to enter a valid email address");
        EMAIL_MSG.show();
        valid = false;
    }

    if ( valid )
    {
        reset_form ( );
    }
}

$(document).ready ( validate );
USERNAME.change ( validate );
PASSWORD.change ( validate );
CONFIRM.change ( validate );
LNAME.change ( validate );
FNAME.change ( validate );
EMAIL.change ( validate );


