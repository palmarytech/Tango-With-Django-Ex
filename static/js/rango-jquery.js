$(document).ready(function(){
    $('#about-btn').click(function(){
        msgStr = $('#msg').html();
        msgStr = msgStr + ' ooo, fancy!';
        $('#msg').html(msgStr)
    });
})