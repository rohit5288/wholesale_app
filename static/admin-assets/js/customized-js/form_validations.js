

function GetContactId(id,email){
    $('#contactus_id').val(id);
    $('#reply_id').text(email);
}

// login validation
$("#login").validate({
    rules: {
        username: {
            required: true,
            normalizer: function (value) {
                return $.trim(value);
            },
            email:true,
        },
        password: {
            required: true, 
            minlength: 8,
            maxlength: 35,
            normalizer: function (value) {
                return $.trim(value);
            }
        },
    },
    messages: {
        username: {
            required: "Please enter your email address",
            
        },
        password: {
            required: "Please enter password",
            minlength: "At least 8 characters required!",
            maxlength: "At most 35 characters only!"
        },
    }
});

function changetype(){
    if ($("#password").attr('type') == "password"){
        document.getElementById("password").type = "text";
    }
    else{
        document.getElementById("password").type = "password";
    }
}
$(document).ready( function () {
    $('#full_year').text(new Date().getFullYear());
});

// forget password validation
$("#forget_password").validate({
    rules: {
        email: {
            required: true,
            email: true,
            normalizer: function (value) {
                return $.trim(value);
            }
        },
    },
    messages: {
        email: {
            required: "Please enter email address",
        },
    }
});

//Add Subscription form
$("#add-subscription").validate({
    ignore: [],
    rules: {
        validity: {
            required: true,
        },
        title: {
            required: true,
            normalizer: function (value) {
                return $.trim(value);
            }
        },
        price: {
            required: true,
            min:1,
            normalizer: function (value) {
                return $.trim(value);
            }
        },
        content: {
            ckrequired:true,
        }
    },
    messages: {
        validity: {
            required: "Please select validity",
        },
        title: {
            required: "Please enter title",
        },
        price: {
            required: "Please enter price",
        },
        content: {
            ckrequired: "Please enter features"
        }
    },
});

// add Booster plan
$("#add-booster").validate({
    ignore: [],
    rules: {
        days: {
            required: true,
        },
        title: {
            required: true,
            normalizer: function (value) {
                return $.trim(value);
            }
        },
        price: {
            required: true,
            min:1,
            normalizer: function (value) {
                return $.trim(value);
            }
        },
    },
    messages: {
        days: {
            required: "Please select validity (number of days)",
        },
        title: {
            required: "Please enter title",
        },
        price: {
            required: "Please enter price",
        },
    },
});  

//Add Blog
$("#add-blog").validate({
    ignore: [],
    rules: {
        title: {
            required: true,
            normalizer: function (value) {
                return $.trim(value);
            }
        },
        images: {
            required: true,
            accept: "jpg,png,jpeg,gif"
        },
        description: {
            required: function(textarea) {
                CKEDITOR.instances[textarea.id].updateElement();
                var editorcontent = textarea.value.replace(/]*>/gi, '');
                return editorcontent.length === 0;
            }
        },
    },
    messages: {
        title: {
            required: "Please enter title",
        },
        images: {
            required: "Please select blog images",
            accept: "Please upload file in these format only (jpg, jpeg, png, gif)"
        },
        description: {
            required: "Please enter description"
        }
    },
    errorPlacement: function (error, element) {
        if (element.attr("name") == "images") {
            $("#empty_image_error").html(error);
        }
        else if (element.attr("name") == "description") {
            error.insertAfter(".description_div");
        }
        else {
            error.insertAfter(element);
        }
    },
});  

$("#edit-blog").validate({
    ignore: [],
    rules: {
        category: {
            required: true,
        },
        title: {
            required: true,
            normalizer: function (value) {
                return $.trim(value);
            }
        },
        images: {
            accept: "jpg,png,jpeg,gif"
        },
        description: {
            required: function(textarea) {
                CKEDITOR.instances[textarea.id].updateElement();
                var editorcontent = textarea.value.replace(/]*>/gi, '');
                return editorcontent.length === 0;
            }
        },
    },
    messages: {
        category: {
            required: "Please select category",
        },
        title: {
            required: "Please enter title",
        },
        images: {
            accept: "Please upload file in these format only (jpg, jpeg, png, gif)"
        },
        description: {
            required: "Please enter description"
        }
    },
    errorPlacement: function (error, element) {
        if (element.attr("name") == "images") {
            $("#empty_image_error").html(error);

        }
        else if (element.attr("name") == "description") {
            error.insertAfter(".description_div");
        }
        else {
            error.insertAfter(element);
        }
    },
});   

// Reply to contact us form
$("#reply-user").validate({
    rules: {
        reply_message: {
            required: true,
            normalizer: function( value ) {
                return $.trim( value );
            }
        }
    },
    messages: {
        reply_message: {
            required: "Please enter reply message"
        }
    }
});

$("#edit-details").validate({
    rules: {
        address: {
            required: true,
            normalizer: function (value) {
                return $.trim(value);
            }
        },
        email: {
            required: true,
            normalizer: function (value) {
                return $.trim(value);
            },
            email: true,
        },
        mobile_no: {
            required: true,
            normalizer: function (value) {
                return $.trim(value);
            },
            number: true,
            minlength: 8,
            maxlength: 15,
        },
    },
    messages: {
        address: {
            required: "Please enter address"
        },
        email: {
            required: "Please enter your email address",
        },
        mobile_no: {
            required: "Please enter your mobile number",
            minlength: "Mobile number should be at least 8 digits",
            maxlength: "Mobile number should not be more than 15 digits",
        },
    }
});  

$("#edit-social-details").validate({
    rules: {
        facebook: {
            required: true
        },
        twitter: {
            required: true
        },
        google: {
            required: true
        },
        
    },
    messages: {
        facebook: {
            required: "Please enter valid facebook url"
        },
        twitter: {
            required: "Please enter valid twitter url"
        },
        google: {
            required: "Please enter valid google url"
        },
        
    }
}); 
