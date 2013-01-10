(function() {


    var Util = {
        
        THEME_CLASSES : 'ui-btn-up-a ui-btn-up-b ui-btn-up-c ui-btn-up-d ui-btn-up-e ui-btn-hover-a ui-btn-hover-b ui-btn-hover-c ui-btn-hover-d ui-btn-hover-e',

        updateTheme : function(s, t) {
            s.removeClass(this.THEME_CLASSES)
                .attr('data-theme', t)
                .addClass('ui-btn-up-' + t);
        }

    }


    // Application state and functions
    var App = (function() {

        function App() {
            this.loaded   = false;
            this.stations = null;
            this.status   = { timestamp : 0 };
            this.playing  = { id: -1, stream: '' };

            $.ajaxSetup({ cache: false });
        }

        App.prototype.fetchStations = function() {
            $.getJSON('get/stations', $.proxy(function(data) {
                this.stations = data;
                $.event.trigger('stationschanged', data);
            }, this));
        };

        App.prototype.fetchPlaying = function() {
            $.getJSON('get/playing', $.proxy(function(data) {
                this.playing = data;
                $.event.trigger('playingchanged', data);
            }, this));
        };

        App.prototype.fetchStatus = function() {
            $.ajax({
                type    : 'POST',
                url     : 'get/status',
                data    : 'timestamp=' + this.status.timestamp,
                cache   : false,
                success : $.proxy(function(data) {
                    data = $.parseJSON(data);
                    if (data) {
                        this.status = data;
                        $.event.trigger('statuschanged', data);
                        window.setTimeout($.proxy(this.fetchStatus, this), 10);
                    }
                }, this)
            });

        };

        App.prototype.sendCommand = function(command, callback) {            
            $.ajax({
                type    : 'POST',
                url     : '/action',
                data    : $.param(command),
                success : callback
            });
        };

        App.prototype.play = function(id) {
            if (this.playing.id != id) {
                $.event.trigger('streamstop', this.playing.id);
                this.sendCommand({ action : 'play', id : id },
                    $.proxy(function() {
                        this.fetchPlaying();
                        $.event.trigger('streamplay', id);
                    }, this)
                );
            }
        };

        App.prototype.stop = function() {
            this.sendCommand({ action : 'stop' },
                $.proxy(function() {
                    this.fetchPlaying();
                    $.event.trigger('streamstop', this.playing.id);
                }, this)
            );
        };

        App.prototype.setVolume = function(percent) {
            this.sendCommand({
                action  : 'setVolume',
                percent : percent
            });
        };

        return App;

    })();


    var app = new App();


    // Bind document events
    $(document)

        .on('pageinit', function (event) {
            if (!app.loaded) {
                app.fetchPlaying();
                app.fetchStations();
                app.fetchStatus();
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
                    Util.updateTheme($('#stationlist > li#' + app.playing.id), 'b');
                }

                stationlist.listview('refresh');

            };

            var refreshBottom = function() {
                $("#nowplaying-bottom").html(app.playing.id >= 0 ? app.playing.stream : '');
            }


            $(this)
                .on('streamplay', function(event, id) {
                    Util.updateTheme($('#stationlist > li#' + id), 'b');
                })
                .on('streamstop', function(event, id) {
                    Util.updateTheme($('#stationlist > li#' + id), 'c');
                })
                .on('stationschanged', refreshStations)
                .on('playingchanged', refreshBottom);


            stationlist.on('click', 'li', function() {
                app.play($(this).attr('id'));
                $.mobile.changePage( "/nowplaying", { transition: "slide"} );
            });


            refreshBottom();
            refreshStations();

        })

        .on('pageinit', '#page-playing', function(event) {

            var refreshPlaying = function() {
                $('#station').html(app.playing.stream);
            }

            var refreshStatus = function() {
                if (app.status.station != '') {
                    $('#station').html(app.status.station);
                }
                $('#status').html(app.status.connection);
                $('#stream').html(app.status.stream);
            }

            $(this).on('playingchanged', refreshPlaying)
                   .on('statuschanged',  refreshStatus);


            $('#volume').on('change', function(event){
                app.setVolume($(this).attr('value') )
            });

            $('#pause').on('click', function(event){
                app.sendCommand({ action: 'pause' });
            });            

            $("#stop").click(function() {
                app.stop();
            });

            refreshPlaying();
            refreshStatus();

            //$('#volume').slider({ disabled: "true" });

        });

})();



