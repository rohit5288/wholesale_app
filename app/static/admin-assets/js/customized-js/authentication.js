//  password progress bar
let passwordStrength = document.getElementById("password-strength");
function checkStrength(password) {
    let strength = 0;
    if (password.match(/([a-z].*)/)) {
        strength += 1;
    }
    if (password.match(/([A-Z].*)/)) {
        strength += 1;
    }
    if (password.match(/([0-9])/)) {
        strength += 1;
    }
    if (password.match(/([!@#\$%\^&\*])/)) {
        strength += 1;
        
    }
    if (password.length > 7 && password.length < 36) {
        strength += 1;
    }
    if (strength == 0){
        passwordStrength.classList.remove('progress-bar-warning');
        passwordStrength.classList.remove('progress-bar-success');
        passwordStrength.style = 'width: 0%';
    } else if (strength == 1) {
        passwordStrength.classList.remove('progress-bar-warning');
        passwordStrength.classList.remove('progress-bar-success');
        passwordStrength.classList.add('progress-bar-danger');
        passwordStrength.style = 'width: 10%';
    } else if (strength == 2) {
        passwordStrength.classList.remove('progress-bar-warning');
        passwordStrength.classList.remove('progress-bar-success');
        passwordStrength.classList.add('progress-bar-danger');
        passwordStrength.style = 'width: 25%';
    } else if (strength == 3) {
        passwordStrength.classList.remove('progress-bar-success');
        passwordStrength.classList.remove('progress-bar-danger');
        passwordStrength.classList.add('progress-bar-warning');
        passwordStrength.style = 'width: 50%';
    } else if (strength == 4) {
        passwordStrength.classList.remove('progress-bar-success');
        passwordStrength.classList.remove('progress-bar-danger');
        passwordStrength.classList.add('progress-bar-warning');
        passwordStrength.style = 'width: 75%';
    } else if (strength == 5) {
        passwordStrength.classList.remove('progress-bar-warning');
        passwordStrength.classList.remove('progress-bar-danger');
        passwordStrength.classList.add('progress-bar-success');
        passwordStrength.style = 'width: 100%';
    }
}


// for otp boxes auto next and previous 

function ValidateOTP() {
    let is_valid = false
    $('.otp__digit').each(function () {
        $('.otp__digit').css('border-color','')
        if (!$(this).val()) {
            $(this).css('border-color','#ee0202')
            $(this).focus()
            is_valid = false
            return false
        } else {
            is_valid = true
        }
    })
    if (is_valid) {
        return true
    } else {
        return false
    }
}

var otp_inputs = document.querySelectorAll(".otp__digit")
var mykey = "0123456789".split("")
otp_inputs.forEach((_) => {
    _.addEventListener("keyup", handle_next_input)
})
function handle_next_input(event) {
    let current = event.target
    let index = parseInt(current.classList[4].split("__")[2])
    if (event.key.length == 1){
        current.value = event.key
    }
    if (event.keyCode == 8 && index > 1) {
        var previous_class = current.classList[4].substring(0,current.classList[4].length-1)+(parseInt(index)-1) 
        var previous = document.getElementsByClassName(previous_class)[0];
        previous.focus()
    }
    if (index < 4 && mykey.indexOf("" + event.key + "") != -1) {
        var next_class = current.classList[4].substring(0,current.classList[4].length-1)+(parseInt(index)+1) 
        var next = document.getElementsByClassName(next_class)[0];
        next.focus()
    }
    var _finalKey = ""
    for (let { value } of otp_inputs) {
        _finalKey += value
    }
    document.getElementById("otp").value = _finalKey
}