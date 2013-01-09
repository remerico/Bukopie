(function() {

    var THEME_CLASSES = 'ui-btn-up-a ui-btn-up-b ui-btn-up-c ui-btn-up-d ui-btn-up-e ui-btn-hover-a ui-btn-hover-b ui-btn-hover-c ui-btn-hover-d ui-btn-hover-e';

    function updateTheme(s, t) {
        s.removeClass(THEME_CLASSES)
            .attr('data-theme', t)
            .addClass('ui-btn-up-' + t);
    }


    // Applicate state and functions
    var app = {

        loaded : false,
        stations : null,
        playing : { id: -1, stream: '' },


        fetchStations : function() {
            $.getJSON('get/stations', function(data) {
                var trigger = (JSON.stringify(app.stations) != JSON.stringify(data));
                app.stations = data;
                if (trigger) $.event.trigger('stationschanged', data);
            });
        },

        fetchPlaying : function() {
            $.getJSON('get/playing', function(data) {
                var trigger = (app.playing.id != data.id);
                app.playing = data;
                if (trigger) $.event.trigger('playingchanged', data);
            })
        },



        sendMessage : function(action, param) {

            param.action = action;
            var data = param;
            
            $.ajax({
                type: 'POST',
                url: '/action',
                data: $.param(data)
            });
        },

        playStation : function(id) {

            if (app.playing.id != id) {
                $.event.trigger('streamstop', app.playing.id);
                app.sendMessage('play', { 'id' : id });
                app.fetchPlaying();

                $.event.trigger('streamplay', id);
            }

            $.mobile.changePage( "/nowplaying", { transition: "slide"} );
        },

        stopStation : function() {
            app.sendMessage('stop', {});
            app.fetchPlaying();

            $.event.trigger('streamstop', app.playing.id);
        }

    };


    // Bind document events
    $(document)

        .on('pageinit', function (event) {
            if (!app.loaded) {
                app.fetchPlaying();
                app.fetchStations();
                app.loaded = true;
            }
        })

        .on('pageinit', '#page-index', function (event) {

            var stationlist = $('#stationlist');

            var refreshStations = function() {

                if (app.stations === null) return;

                var items = [];

                $.each(app.stations, function(key, val) {
                    items.push('<li id="' + val.id + '"><a href="#">' + val.name + '</a></li>');
                });

                stationlist.html(items.join(''))

                if (app.playing.id >= 0) {
                    updateTheme($('#stationlist > li#' + app.playing.id), 'b');
                }

                stationlist.listview('refresh');

            };

            var refreshBottom = function() {
                $("#nowplaying-bottom").html(app.playing.id >= 0 ? app.playing.stream : '');
            }


            $(this)
                .on('streamplay', function(event, id) {
                    updateTheme($('#stationlist > li#' + id), 'b');
                })
                .on('streamstop', function(event, id) {
                    updateTheme($('#stationlist > li#' + id), 'c');
                })
                .on('stationschanged', refreshStations)
                .on('playingchanged', refreshBottom);


            stationlist.on('click', 'li', function() {
                app.playStation($(this).attr('id'));
            });


            refreshBottom();
            refreshStations();

        })

        .on('pageinit', '#page-playing', function(event) {

            var refreshPlaying = function() {
                $('#playingstation').html(app.playing.stream);
            }

            $(this).on('playingchanged', refreshPlaying);


            $("#stop").click(function() {
                app.stopStation();
            });

            $("#volumeUp").click(function() {
                app.sendMessage("volumeUp", {});
            });

            $("#volumeDown").click(function() {
                app.sendMessage("volumeDown", {});
            });


            refreshPlaying();

        })

        .on('pagebeforeshow', '#page-playing', function (event) {

            $.getJSON('get/status', function(data) {
                alert(JSON.stringify(data));
            });
            

        });

})();



