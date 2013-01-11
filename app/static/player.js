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
            this.status   = null;
            this.playing  = { id: -1, stream: '' };

            $.ajaxSetup({ 
                cache: false,
                headers: { "cache-control": "no-cache" } 
            });
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
                type     : 'POST',
                url      : 'get/status',
                data     : 'timestamp=' + (this.status !== null ? this.status.timestamp : 0),
                cache    : false,
                complete : $.proxy(function(x, s) {
                    window.setTimeout($.proxy(this.fetchStatus, this), 0);
                }, this),
                success  : $.proxy(function(data) {
                    data = $.parseJSON(data);
                    if (data) {
                        this.status = data;
                        $.event.trigger('statuschanged', data);
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
                action  : 'setVol',
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

            var volumeControl = $('#volume');
            var pauseControl = $('#pause');
            var stopControl = $('#stop');


            var refreshPlaying = function() {
                $('#station').html(app.playing.stream);
            }

            var refreshStatus = function() {

                if (app.status !== null) {

                    if (app.status.station != '') {
                        $('#station').html(app.status.station);
                    }
                    $('#status').html(app.status.connection);
                    $('#stream').html(app.status.stream);

                    if (!volumeControl._dragged) {
                        volumeControl.attr('value', app.status.volume).slider('refresh');
                    }

                }
            }

            $(this).on('playingchanged', refreshPlaying)
                   .on('statuschanged',  refreshStatus);


            volumeControl.on('change', function(event){
                if (volumeControl._dragged) {
                    app.setVolume($(this).attr('value'))
                }
            });

            volumeControl.on('slidestart', function(event) {
                volumeControl._dragged = true;
            });

            volumeControl.on('slidestop', function(event) {
                volumeControl._dragged = false;
            });

            pauseControl.on('click', function(event){
                app.sendCommand({ action: 'pause' });
            });            

            stopControl.click(function() {
                app.stop();
            });

            refreshPlaying();
            refreshStatus();

            //$('#volume').slider({ disabled: "true" });

        });

})();



