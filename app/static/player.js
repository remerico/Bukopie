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


    // Application controller
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

        App.prototype.getFavorites = function() {
            this.socket.send('getFavorites', [], $.proxy(function(result, error) {
                $(this).trigger('handlefavorites', [result]);
            }, this));
        }

        App.prototype.setFavorite = function(track, value) {
            this.socket.send('setFavorite', [track, value]);
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



    var MenuController = (function() {

        function MenuController(app, selector) {

            var menuStatus = false;
            var _this = this;

            var hideMenu = function() {
                $(".ui-page-active").animate({ marginLeft: "0px" }, 300, function() { menuStatus = false; });
            }

            var showMenu = function() {
                $(".ui-page-active").animate({ marginLeft: "165px" }, 300, function() { menuStatus = true; });
            }

            var toggleMenu = function() {
                if (!menuStatus) showMenu()
                else hideMenu();
            }

            // Toggle menu
            $("#page-index #menu-button").on("click", function() { toggleMenu(); });
            $(document).on("swipeleft",  function() { if (menuStatus) hideMenu(); });
            $(document).on("swiperight", function() { if (!menuStatus) showMenu(); });

            // Menu links
            $("#menu li a").on("click", function() { 
                window.location = $(this).attr('href')
                _this.selectMenu(this); 
                hideMenu();
            });

            // Change page on location hash change
            $(window).on('hashchange', function() {
                _this.changePage(window.location.hash.substring(1));
            });

            // Hide now playing link if playing stream is inactive
            $(app).on('handlestatus', function(events, status) {
                if (!Util.isNull(status.playing)) {
                    $('#menu a[href="#nowplaying"]').parent().attr('hidden', !status.playing)
                }
            });

        }

        MenuController.prototype.changePage = function(anchor) {

            $('div[data-role="subpage"]').each(function() {
                var t = $(this);
                if (!t.attr('hidden')) {
                    t.attr('hidden', true);     
                    t.trigger('hide');
                }
            });

            $('div[data-role="subpage"][id="' + anchor + '"]')
                .attr('hidden', false)
                .trigger('show');

            if (window.location.hash != '#' + anchor) {
                window.location.hash = '#' + anchor;
            }

            this.selectMenu('#menu li a[href="#' + anchor + '"]');

        }

        MenuController.prototype.selectMenu = function(selector) {
            $("#menu li").removeClass('active');
            $(selector).parent().addClass('active');
        }

        return MenuController;

    })();



    var StationsController = (function() {

        function StationsController(app, menu, selector) {
            this.app = app;
            this.menu = menu;
            this.selector = selector;

            this.selectedStream  = -1;

            this.stationList = $('#stationlist');

            $(app).on('handlestatus', $.proxy(this.refresh, this))

            this.stationList.on('click', 'li', function() {
                app.play($(this).attr('id'));
                menu.changePage('nowplaying');
            });
        } 

        StationsController.prototype.refresh = function(event, status) {

            if (!Util.isNull(status.stations)) {
                this.refreshStations(status.stations);
            }
            if (!Util.isNull(status.playid)) {
                this.refreshSelectedStream(status.playid);
            }

        }

        StationsController.prototype.refreshStations = function(stations) {

            var items = [];

            $.each(stations, function(key, val) {
                items.push('<li id="' + val.id + '"><a href="#">' + val.name + '</a></li>');
            });

            this.stationList.html(items.join(''))

            if (this.app.status.playid >= 0) {
                Util.updateTheme($('#stationlist > li#' + this.app.status.playid), 'b');
            }

            this.stationList.listview('refresh');

        };

        StationsController.prototype.refreshSelectedStream = function(id) {
            if (typeof id != 'number') return;

            if (this.selectedStream != id) {

                if (this.selectedStream != -1) {
                    Util.updateTheme($('#stationlist > li#' + this.selectedStream), 'c');
                }

                if (id != -1) {
                    Util.updateTheme($('#stationlist > li#' + id), 'b');
                }
             
                this.selectedStream = id;   
            }
        };

        return StationsController;

    })();



    var HistoryController = (function() {

        function HistoryController(app, menu, selector) {
            this.app = app;
            this.menu = menu;
            this.selector = selector;

            this.historylist = $('#historylist');

            $(app).on('handlehistory', $.proxy(this.refresh, this));

            $(selector).on('show', function() {
                app.getHistory();
            });
        }

        HistoryController.prototype.refresh = function(event, data) {
            var items = new Array();

            $.each(data, $.proxy(function(key, val) {
                if (val.artist != ''  && val.title != '') {
                    items.push('<li><img src="' + val.cover + '" /><h3>' + val.title + '</h3><p>' + val.artist + '</p></li>');
                }
            }, this));

            this.historylist.html(items.join(''))
            this.historylist.listview('refresh');
        }

        return HistoryController;

    })();



    var NowPlayingController = (function() {

        function NowPlayingController(app, menu, selector) {
            this.app = app;
            this.menu = menu;
            this.selector = selector;

            $(app).on('handlestatus', $.proxy(this.refresh, this));


            var _this = this;
            this.volumeControl = $('#volume');
            this.pauseControl = $('#pause');
            this.stopControl = $('#stop');
            this.station = $('#station');
            this.stream = $('#stream');
            this.connection = $('#status');
            this.coverart = $('#cover');
            this.favorite = $('#button-favsong');

            volumeControl = this.volumeControl;
            currentVol = volumeControl.attr('value')

            this.volumeControl.on('change', function(event){
                var value = volumeControl.attr('value')
                if (volumeControl._dragged && currentVol != value) {
                    app.setVolume(value);
                    currentVol = value;
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
                menu.changePage('stations');
            });

            this.favorite.on('click', function() {
                _this.toggleFavorite();
            });


        }

        NowPlayingController.prototype.refresh = function(event, status) {

            if (!this.app.status.playing && !$(this.selector).attr('hidden')) {
                this.menu.changePage('stations');
                return;
            }

            // Stream
            if (!Util.isNull(status.stream)) {
                this.station.html(status.stream);
            }

            // Player
            if (!Util.isNull(status.player)) {
                this.connection.html(status.player.connection);
                this.stream.html(status.player.stream);

            }

            // Volume
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


        NowPlayingController.prototype.toggleFavorite = function() {
            if (this.favorite.checked) {
                Util.updateTheme(this.favorite, 'c');
                this.favorite.checked = false;
            }
            else {
                Util.updateTheme(this.favorite, 'b');
                this.favorite.checked = true;
            }
        }

        return NowPlayingController;

    })();



    // Bind document events
    $(document).on('ready', function(event) {

        var app = new App();
        var menu = new MenuController(app, '#menu');

        new StationsController(app, menu, '#stations');
        new NowPlayingController(app, menu, '#nowplaying');
        new HistoryController(app, menu, '#history');


        $('div[data-role="subpage"]').each(function(i) {
            if (i > 0) $(this).attr('hidden', true);
        });
        

        $(app.socket).on('connected', function(event) {
            app.fetchStatus();

            if (window.location.hash) {
                menu.changePage(window.location.hash.substring(1));
            }
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

        app.connect();

    });

})();



