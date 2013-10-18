var TanTan = new Backbone.Marionette.Application();

TanTan.addRegions({
    nav: "#nav",
    main: "#main"
});

TanTan.on('initialize:after', function() {
    Backbone.history.start();
});
