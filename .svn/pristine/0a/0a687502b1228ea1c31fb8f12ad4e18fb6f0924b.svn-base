$(function () {
    const _url = window.location.toString().split(window.location.host.toString())[1];
    const cargando = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    const btnSubmit = $('#submit');
    const error_btn = btnSubmit.html();
    //
    // $("#guardarform").click(function() {
    //     $("#submit").trigger("click");
    // });

    $('form').submit(function (e) {
        e.preventDefault();
        var _form = new FormData($(this)[0]);
        $.ajax({
            type: "POST",
            url: _url,
            data: _form,
            dataType: "json",
            enctype: $(this).attr('enctype'),
            cache: false,
            contentType: false,
            processData: false,
            beforeSend: function () {
                btnSubmit.html(cargando);
                btnSubmit.attr("disabled", true);
            }
        }).done(function (data) {
            if (!data.error) {
                if (data.to) {
                    location = data.to;
                }
            } else {
                // $.notify(data.msj, {type:"warning"});
                alert(data.msj);
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            // $.notify('Error de conexión con el servidor', {type:"warning"});
            alert(data.msj);
            btnSubmit.html(error_btn);
            btnSubmit.attr("disabled", false);
        }).always(function () {
            btnSubmit.html(error_btn);
            btnSubmit.attr("disabled", false);
        });
    });
});