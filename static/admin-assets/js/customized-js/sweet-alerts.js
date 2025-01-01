

    $('.action_confirm').click(function(event) {
        event.preventDefault();        
        Swal.fire({
            //title: "Are you sure?",
            text: $(this).attr('message'),
            icon: "question",
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Yes, delete it!",
            showCancelButton: true,
            reverseButtons: true
          }).then((result) => {
            if (result.isConfirmed) {
                location.href=$(this).attr('href')
              }
            });
        });

        $('.active_deactive').click(function(event) {
            event.preventDefault();        
            Swal.fire({
                //title: "Are you sure?",
                text: $(this).attr('message'),
                icon: "question",
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: $(this).attr('action'),
                showCancelButton: true,
                reverseButtons: true,
                //allowOutsideClick: false
              }).then((result) => {
                if (result.isConfirmed) {
                    location.href=$(this).attr('href')
                  }
                });
            });
    
    

function ConfirmFormSubmission(form){
    swal({
        title: $(form).attr('message'),
        text: "",
        icon: "warning",
        buttons: true,
    })
    .then((willDelete) => {
        if (willDelete) {
            $(form).attr('onsubmit',true)
            $(form).submit()
            Loader($(form).attr('id'))
        }
    });
    return false
}

