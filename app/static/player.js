(function() {

    var Util = {
        
        THEME_CLASSES : 'ui-btn-up-a ui-btn-up-b ui-btn-up-c ui-btn-up-d ui-btn-up-e ui-btn-hover-a ui-btn-hover-b ui-btn-hover-c ui-btn-hover-d ui-btn-hover-e',

        updateTheme : function(s, t) {
            s.removeClass(this.THEME_CLASSES)
                .attr('data-theme', t)
                .addClass('ui-btn-up-' + t);
        },

        isNull : function(c) {
            return c === null || typeof c == 'undefined';
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
                this.status.playing = true;
                this.socket.send('play', [id], $.proxy(function() {
                    $(this).trigger('streamplay', id);
                }, this));
            }
        };

        App.prototype.stop = function() {
            var id = this.status.playid;
            this.status.playing = false;
            this.socket.send('stop', [] , $.proxy(function(result, error) {
                $(this).trigger('streamstop', id);
            }, this));
        };

        App.prototype.getHistory = function() {
            this.socket.send('getHistory', [], $.proxy(function(result, error) {
                $(this).trigger('handlehistory', [result]);
            }, this));
        }

        App.prototype.setVolume = function(percent) {
            //if (percent != this.status.player.volume)
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
            this.t_historyList   = '#historylist';
            this.t_playingStream = '#nowplaying-button';
            this.selectedStream  = -1;

            $(app)
                .on('handlestatus', $.proxy(this.refresh, this))
                .on('handlehistory', $.proxy(this.refreshHistory, this));

            $(document)
                .on('pageinit',selector, $.proxy(this.init, this))
                .on('pagebeforeshow', selector, $.proxy(function() {
                    this.refresh('', this.app.status);
                }, this));

            this.registerMenuEvents();

        }

        IndexView.prototype.registerMenuEvents = function() {

            var menuStatus;

            $("#page-index #menu-button").live("click", function(){
                if(menuStatus != true){
                $(".ui-page-active").animate({
                    marginLeft: "165px",
                  }, 300, function(){menuStatus = true});
                  return false;
                  } else {
                    $(".ui-page-active").animate({
                    marginLeft: "0px",
                  }, 300, function(){menuStatus = false});
                    return false;
                  }
            });

             $('#page-index').live("swipeleft", function(){
                if (menuStatus){
                $(".ui-page-active").animate({
                    marginLeft: "0px",
                  }, 300, function(){menuStatus = false});
                  }
            });
         
            $('#page-index').live("swiperight", function(){
                if (!menuStatus){
                $(".ui-page-active").animate({
                    marginLeft: "165px",
                  }, 300, function(){menuStatus = true});
                  }
            });

            $("#menu li a").live("click", function(){
                $("#menu li").removeClass('active');
                $(this).parent().addClass('active');
            });



            $("#menu #menu-stations").live("click", function() {
                hideMenu();
                $("#page-index #subpage-stations").attr("hidden", false);
            });

            $("#menu #menu-history").live("click", $.proxy(function() {
               hideMenu();
               $("#page-index #subpage-history").attr("hidden", false);
               this.app.getHistory();
            }, this));

            $("#menu #menu-settings").live("click", function() {
               hideMenu();
               $("#page-index #subpage-settings").attr("hidden", false);
            });

            function hideMenu() {
                $("#page-index .subpage").attr("hidden", true); 
                menuStatus = false;
                $(".ui-page-active").animate({ marginLeft: "0px",
                  }, 300, function(){menuStatus = false});
            }

        }

        IndexView.prototype.init = function() {
            this.loaded = true;
            var _this = this;

            $(this.t_stationList).on('click', 'li', function() {
                _this.app.play($(this).attr('id'));
                $.mobile.changePage( "#nowplaying", { transition: "slide"} );
            });
        };

        IndexView.prototype.refresh = function(event, status) {

            if (!this.loaded) return;

            if (!Util.isNull(status.stations)) {
                this.refreshStations(status.stations);
            }
            if (!Util.isNull(status.stream)) {
                this.refreshPlaying(status.stream);
            }
            if (!Util.isNull(status.playid)) {
                this.refreshSelectedStream(status.playid);
            }

        };

        IndexView.prototype.refreshHistory = function(event, data) {
            var items = [];

            $.each(data, $.proxy(function(key, val) {
                if (val.artist != ''  && val.title != '') {
                    items.push('<li><img src="' + val.cover + '" /><h3>' + val.title + '</h3><p>' + val.artist + '</p></li>');
                }
            }, this));

            $(this.t_historyList).html(items.join(''))
            $(this.t_historyList).listview('refresh');
        }

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
            if (stream.length > 0) $(this.t_playingStream).show();
            else $(this.t_playingStream).hide();
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

            $(app).on('handlestatus', $.proxy(function(event, status) {
                if (!this.app.status.playing) $.mobile.changePage('/', { transition: "none"} );
                this.refresh(event, status);
            }, this));


            $(document)
                .on('pageinit', selector, $.proxy(this.init, this))
                .on('pagebeforeshow', selector, $.proxy(function() {
                    this.refresh('', this.app.status);
                }, this));

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
            this.coverart = $('#cover');

            volumeControl = this.volumeControl;
            this.currentVol = volumeControl.attr('value')

            this.volumeControl.on('change', $.proxy(function(event){
                var value = volumeControl.attr('value')
                if (volumeControl._dragged && this.currentVol != value) {
                    app.setVolume(value);
                    this.currentVol = value;
                }
            }, this));

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

        NowPlayingView.prototype.refresh = function(event, status) {

            if (!this.loaded) return;

            if (!Util.isNull(status.stream)) {
                this.station.html(status.stream);
            }
            if (!Util.isNull(status.player)) {
                this.connection.html(status.player.connection);
                this.stream.html(status.player.stream);

            }

            if (!Util.isNull(status.volume)) {
                if (!this.volumeControl._dragged) {
                    this.volumeControl.attr('value', status.volume).slider('refresh');
                }
            }

            // Album art
            if (!Util.isNull(status.trackinfo)) {
                if (!Util.isNull(status.trackinfo.cover)) {
                    this.coverart.attr('src', status.trackinfo.cover).stop(true,true).hide().fadeIn();
                } else {
                    this.coverart.removeAttr('src').hide();
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

        $(app).on('handlestatus', function(event, status) {
            if (!Util.isNull(status.player) && !Util.isNull(status.player.stream)) {
                if (status.player.stream != '') {
                    document.title = status.player.stream;
                }
                else {
                     document.title = 'Bukopie';   
                }
            }
        });
    });

})();



