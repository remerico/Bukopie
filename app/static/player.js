$('#page-index').live('pagebeforeshow', function (event) {

    // Get station list
    $.getJSON('get/stations', function(data) {

        var items = [];

        $.each(data, function(key, val) {
            items.push('<li><a href="#" onclick="playStation(' + val.id + ')">' + val.name + '</a></li>');
        });

        $('#stationlist').html(items.join('')).listview('refresh');

    });

});


$('#page-playing').live('pagebeforeshow', function (event) {

    $("#stop").click(function() {
        stopStation();
    });

    $.getJSON('get/playing', function(data) {
        $('#playingstation').html(data.stream);
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
    $.mobile.changePage( "/nowplaying", { transition: "slide"} );
}

function stopStation() {
    sendAction('stop', {});
    //$.mobile.changePage( "/", { transition: "slide"} );
}