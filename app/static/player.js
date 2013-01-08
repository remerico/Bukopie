$(document).ready(function(){

    $("#play").click(function() {
        sendAction('play', {some:1}) 
    });

    $("#stop").click(function() {
        sendAction('stop', {}) 
    });

    $("#volup").click(function() {
        sendAction('volumeUp', {}) 
    });

    $("#voldown").click(function() {
        sendAction('volumeDown', {}) 
    });


    // Get station list
    $.getJSON('get/stations', function(data) {

        var items = [];

        $.each(data, function(key, val) {
            items.push('<li><a href="#" onclick="playStation(' + val.id + ')">' + val.name + '</a></li>');
        });

        $('#stationlist').html(items.join('')).listview('refresh');

    });

});


function sendAction(action, param) {

    param.action = action;
    var data = param;
    
    $.ajax({
        type: 'POST',
        url: '/action',
        data: $.param(data),
        //success: function(data) { }
    });
}

function playStation(id) {
    sendAction('play', { 'id' : id });
}