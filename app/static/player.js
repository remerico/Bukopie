$('#page-index').live('pagebeforeshow', function (event) {

    // Get station list
    $.getJSON('get/stations', function(data) {

        var items = [];

        $.each(data, function(key, val) {
            items.push('<li ' + (val.playing ? 'data-theme="b"' : '') + '><a href="#" onclick="playStation(' + val.id + ')">' + val.name + '</a></li>');
        });

        $('#stationlist').html(items.join('')).listview('refresh');

    });

    $.getJSON('get/playing', function(data) {
        $("#nowplaying-bottom").html(data.playing ? data.stream : '');
    })

});


$('#page-playing').live('pagebeforeshow', function (event) {

    $.getJSON('get/playing', function(data) {
        $('#playingstation').html(data.stream);
    });

});

$('#page-playing').live('pagecreate', function (event) {

    $("#stop").click(function() {
        stopStation();
    });

    $("#volumeUp").click(function() {
        sendAction("volumeUp", {});
    });

    $("#volumeDown").click(function() {
        sendAction("volumeDown", {});
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