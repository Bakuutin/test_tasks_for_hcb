function update_sum(message) {
    $('#current-sum').html(message.data);
}

$("#form").on('submit', function(){
    $.ajax({
        url: "http://127.0.0.1:8080/vote",
        type: "POST",
        data: JSON.stringify({"number": parseInt($("input[name='number']:checked").val())}),
        headers: {'x-token': window.token},
        success: function(data) {
            $("#form").hide();
        },
        error: function(e) {
            $("#submit").addClass("btn-danger");
        }
    });
    return false;
});

$(document).ready(function(){
    new WebSocket("ws://127.0.0.1:8080/online").onmessage = update_sum;
    $.post("http://127.0.0.1:8080/session", (data) => {window.token = data;});
});
