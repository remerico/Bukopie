(function() {


    var Util = {
        
        THEME_CLASSES : 'ui-btn-up-a ui-btn-up-b ui-btn-up-c ui-btn-up-d ui-btn-up-e ui-btn-hover-a ui-btn-hover-b ui-btn-hover-c ui-btn-hover-d ui-btn-hover-e',

        updateTheme : function(s, t) {
            s.removeClass(this.THEME_CLASSES)
                .attr('data-theme', t)
                .addClass('ui-btn-up-' + t);
        }
    }

    // JSON-RPC protocol
    var Socket = (function() {

        function Socket() {
            this.id = -1;
            this.callbacks = [];
        }

        Socket.prototype.connect = function() {
            console.log('connecting..')
            this.socket = new SockJS('http://' + window.location.host + '/socket');
            this.socket.onopen = $.proxy(this._onopen, this);
            this.socket.onmessage = $.proxy(this._onmessage, this);
            this.socket.onclose = $.proxy(this._onclose, this);
        }

        Socket.prototype._onopen = function() { 
            console.log('connected')
            $(this).trigger('connected'); 
        }

        Socket.prototype._onmessage = function(e) { 
            console.log('received: ' + e.data)
            var data = $.parseJSON(e.data);

            if (typeof data.id !== 'undefined') {
                if (this.callbacks[data.id]) {
                    this.callbacks[data.id](data.result, data.error);
                    this.callbacks[data.id] = null;
                }
            }
            else {
                $(this).trigger('notify', data);
            }
        }

        Socket.prototype._onclose = function() {
            console.log('disconnected');
            window.setTimeout($.proxy(this.connect, this), 1000);
        }

        Socket.prototype.getId = function() {
            return ++this.id % 10;
        }

        Socket.prototype.send = function(method, params, callback) {
            var id = this.getId();
            this.socket.send(JSON.stringify(
                { 'method' : method, 'params' : params, 'id' : id }));
            this.callbacks[id] = callback;
        }

        return Socket;

    })();


    // Application state and functions
    var App = (function() {

        function App() {
            this.status = {
                stations : null,
                player   : {},
                playing  : false,
                playid   : -1,
                stream   : ''
            };

            this.socket = new Socket();
            $(this.socket).on('notify', $.proxy(this.handleNotify, this));
        }

        App.prototype.handleNotify = function(event, data) {
            switch (data.method) {
                case 'status':
                    this.updateStatus(data.params);
                    break;
            }
        }

        App.prototype.connect = function() {
            this.socket.connect();
        }

        App.prototype.fetchStatus = function() {
            this.socket.send('getStatus', [], $.proxy(function(result, error) {
                this.updateStatus(result);
            }, this));
        }

        App.prototype.updateStatus = function(stat) {
            $.extend(true, this.status, stat);
            $(this).trigger('handlestatus', stat);
        }

        App.prototype.play = function(id) {
            if (this.status.playid != id) {
                $(this).trigger('streamstop', this.status.playid);
                this.socket.send('play', [id], $.proxy(function() {
                    $(this).trigger('streamplay', id);
                }, this));
            }

        };

        App.prototype.stop = function() {
            var id = this.status.playid;
            this.socket.send('stop', [] , $.proxy(function(result, error) {
                $(this).trigger('streamstop', id);
            }, this));
        };

        App.prototype.setVolume = function(percent) {
            if (percent != this.status.player.volume)
                this.socket.send('setVol', [percent]);
        };

        App.prototype.pause = function() {
            this.socket.send('pause', []);
        }

        return App;

    })();



    var IndexView = (function() {

        function IndexView(selector, app) {
            this.loaded = false;
            this.app = app;

            this.t_stationList   = '#stationlist';
            this.t_playingStream = '#nowplaying-bottom';
            this.selectedStream  = -1;

            $(app).on('handlestatus', $.proxy(this.refresh, this));

            $(document)
                .on('pageinit',selector, $.proxy(this.init, this))
                .on('pagebeforeshow', selector, $.proxy(this.pageBeforeShow, this));

        }

        IndexView.prototype.init = function() {
            this.loaded = true;
            var _this = this;

            $(this.t_stationList).on('click', 'li', function() {
                _this.app.play($(this).attr('id'));
                $.mobile.changePage( "#nowplaying", { transition: "slide"} );
            });
        };

        IndexView.prototype.pageBeforeShow = function() {
            this.refresh('', this.app.status);
        };

        IndexView.prototype.refresh = function(event, status) {

            if (!this.loaded) return;

            if (!$.isEmptyObject(status.stations)) {
                console.log(status.stations)
                this.refreshStations(status.stations);
            }
            if (!$.isEmptyObject(status.stream)) {
                this.refreshPlaying(status.stream);
            }
            if (!$.isEmptyObject(status.playid)) {
                this.refreshSelectedStream(status.playid);
            }

        };

        IndexView.prototype.refreshStations = function(stations) {

            var items = [];

            $.each(stations, function(key, val) {
                items.push('<li id="' + val.id + '"><a href="#">' + val.name + '</a></li>');
            });

            $(this.t_stationList).html(items.join(''))

            if (this.app.status.playid >= 0) {
                Util.updateTheme($(this.t_stationList + ' > li#' + this.app.status.playid), 'b');
            }

            $(this.t_stationList).listview('refresh');

        };

        IndexView.prototype.refreshPlaying = function(stream) {
            $(this.t_playingStream).html(stream);
        };

        IndexView.prototype.refreshSelectedStream = function(id) {
            if (typeof id != 'number') return;

            if (this.selectedStream != id) {

                if (this.selectedStream != -1) {
                    Util.updateTheme($(this.t_stationList + ' > li#' + this.selectedStream), 'c');
                }

                if (id != -1) {
                    Util.updateTheme($(this.t_stationList + ' > li#' + id), 'b');
                }
             
                this.selectedStream = id;   
            }
        };

        return IndexView;

    })();



    var NowPlayingView = (function() {

        function NowPlayingView(selector, app) {
            this.loaded = false;
            this.app = app;

            $(app).on('handlestatus', $.proxy(this.refresh, this));

            $(document)
                .on('pageinit', selector, $.proxy(this.init, this))
                .on('pagebeforeshow', selector, $.proxy(this.pageBeforeShow, this));

        }

        NowPlayingView.prototype.init = function() {

            this.loaded = true;

            var _this = this;
            this.volumeControl = $('#volume');
            this.pauseControl = $('#pause');
            this.stopControl = $('#stop');
            this.station = $('#station');
            this.stream = $('#stream');
            this.connection = $('#status');

            volumeControl = this.volumeControl;

            this.volumeControl.on('change', function(event){
                if (volumeControl._dragged) {
                    app.setVolume($(this).attr('value'))
                }
            });

            this.volumeControl.on('slidestart', function(event) {
                volumeControl._dragged = true;
            });

            this.volumeControl.on('slidestop', function(event) {
                volumeControl._dragged = false;
            });

            this.pauseControl.on('click', function(event){
                _this.app.pause();
            }); 

            this.stopControl.click(function() {
                _this.app.stop();
            });

        }
        
        NowPlayingView.prototype.pageBeforeShow = function() {
            this.refresh('', this.app.status);
        }

        NowPlayingView.prototype.refresh = function(event, status) {

            if (!this.loaded) return;

            if (!$.isEmptyObject(status.stream)) {
                this.station.html(status.stream);
            }
            if (!$.isEmptyObject(status.player)) {

                if (status.player.station != '') {
                    this.station.html(status.player.station);
                }
                this.connection.html(status.player.connection);
                this.stream.html(status.player.stream);

                if (!this.volumeControl._dragged) {
                    this.volumeControl.attr('value', status.player.volume).slider('refresh');
                }

            }

        }

        return NowPlayingView;

    })();

    var app = new App();
    var indexView = new IndexView('#page-index', app);
    var nowPlayingView = new NowPlayingView('#nowplaying', app);


    // Bind document events
    $(document).on('ready', function(event) {
        app.connect();
        $(app.socket).on('connected', function(event) {
            app.fetchStatus();
        });
    });

})();



