$.validator.addMethod(
    "strongpassword",
    function(value, element, regexp) {
        var re = new RegExp(regexp);
        return this.optional(element) || re.test(value);
    },
    "Please Choose Strong Password."
);
jQuery.validator.addMethod("is_email_exists", 
function(value, element) {
    let is_valid = true
    $.ajax({
        url: "{% url 'accounts:validations' %}",
        type: "GET",
        data: { email: value },
        async:false,
        success: function (data) {
            if(data.email == true){
                is_valid = false
            }
            else{
                is_valid =  true
            }
        },
      });        
    return is_valid
},'Email already exists!');

jQuery.validator.addMethod("is_username_exists", 
function(value, element) {
    let is_valid = true
    $.ajax({
        url: "{% url 'accounts:validations' %}",
        type: "GET",
        data: { username: value },
        async:false,
        success: function (data) {
            if(data.username == true){
                is_valid = false
            }else{
                is_valid =  true
            }
            
        },
        });        
    return is_valid
},'Username already exists!');

jQuery.validator.addMethod("is_mobile_exists", 
function(value, element) {
    let is_valid = true
    $.ajax({
        url: "{% url 'accounts:validations' %}",
        type: "GET",
        data: { mobile_no: value,country_code:$('#country_code').val()},
        async:false,
        success: function (data) {
            if(data.mobile_no == true){
                is_valid = false
            }else{
                is_valid =  true
            }
        },
        });        
    return is_valid
},'Mobile number already exists!');

// Refresh page on Browser Back Button to Remove the Loader
(function () {
    window.onpageshow = function(event) {
        if (event.persisted) {
            window.location.reload();
        }
    };
})();
function Loader(formID) {
    loader_html = `
    <div class="maindiv">
        <div>
            <div class="loadericon">
                <div class="outerCircle"></div>
                    <div class="icon logoname">
                        <img alt="" width="10" src="{% static "admin-assets/images/logo.png" %}" />
                    </div>
                </div>
            </div>
        </div>
    </div>
    `
    if ($('#'+formID).length){
        if ($('#'+formID).valid()){
            $('body').append(loader_html);
            $('body').css('pointer-events','none');
            $('.btn').css('pointer-events','none');
        }
    }else{
        $('body').append(loader_html);
        $('body').css('pointer-events','none');
        $('.btn').css('pointer-events','none');
    }
}

$(document).ready( function () {
    $('#full_year').text(new Date().getFullYear());
});

if ($('textarea').val()) {
    $('textarea').val($('textarea').val().trim())
}

if($('.clickable-row').length > 0 ){
    $(document).on('click', '.clickable-row', function() {
        window.location = $(this).data("href");
    });
}

$(function () {
    $('[data-bs-toggle="tooltip"]').tooltip();
})

$(".submenu ").click(function(){
        $(".subdrop").addClass("active");
      });

    $(document).ready(function () {
        $('.timezone').val(Intl.DateTimeFormat().resolvedOptions().timeZone)
    });

$('.number_field').keypress(function(event) {
    if ((event.which != 46 || $(this).val().indexOf('.') != -1) &&
        ((event.which < 48 || event.which > 57) &&
        (event.which != 0 && event.which != 8))) {
        event.preventDefault();
    }

    var text = $(this).val();

    if ((text.indexOf('.') != -1) &&
        (text.substring(text.indexOf('.')).length > 2) &&
        (event.which != 0 && event.which != 8) &&
        ($(this)[0].selectionStart >= text.length - 2)) {
        event.preventDefault();
    }
    });

$(window).scroll(function() {    
var scroll = $(window).scrollTop();

if (scroll >= 100) {
    $(".main-head").addClass("darkheader");
}
});

function ClearNotifications(){
    $.ajax({
        url:"{% url 'accounts:delete_notifications' %}?n_id=id",
        type:"GET",
        data:{},
        success:function(data){
            location.reload()
        }
    });
}
// redirects on same tab after refresh.
$(document).ready(function(){
    $('a[data-toggle="tab"]').on('show.bs.tab', function(e) {
        localStorage.setItem('activeTab', $(e.target).attr('href'));
    });
    var activeTab = localStorage.getItem('activeTab');
    if(activeTab){
        $('#myTab a[href="' + activeTab + '"]').tab('show');
    }
    });
