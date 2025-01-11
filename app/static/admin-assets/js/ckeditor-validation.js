// validation for empty field
jQuery.validator.addMethod("ckrequired", function (value, element) {  
    var idname = $(element).attr('id');  
    var editor = CKEDITOR.instances[idname];  
    var ckValue = GetTextFromHtml(editor.getData()).replace(/<[^>]*>/gi, '').trim();
    if (ckValue.length === 0 ) {    
        $(element).val(ckValue);
    }else {  
        $(element).val(editor.getData());
    }
    return $(element).val().length > 0;
}, "Please enter description");  

function GetTextFromHtml(html) {  
    var dv = document.createElement("DIV");  
    dv.innerHTML = html;  
    return dv.textContent || dv.innerText || "";  
}

// validation for max length
jQuery.validator.addMethod("ck_maxlength", function (value, element) {  
    var idname = $(element).attr('id');  
    var editor = CKEDITOR.instances[idname];  
    var ckValue = GetTextFromHtml(editor.getData()).replace(/<[^>]*>/gi, '').trim();
    if (ckValue.length === 0 ) {    
        $(element).val(ckValue);
    }else {  
        $(element).val(editor.getData());
    }
    console.log($(element).val().split(" ").length)
    return $(element).val().split(" ").length < 500;
}, "Only 500 words allowed!");  

function GetTextFromHtml(html) {  
    var dv = document.createElement("DIV");  
    dv.innerHTML = html;  
    return dv.textContent || dv.innerText || "";  
}