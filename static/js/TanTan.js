var TanTan = new Backbone.Marionette.Application();

TanTan.addRegions({
    nav: "#nav"
});

TanTan.on('initialize:after', function() {
    Backbone.history.start();
});
