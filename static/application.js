MyApp = new Backbone.Marionette.Application();

MyApp.addRegions({
    mainRegion: "#content"
});

Sistema = Backbone.Model.extend({
    defaults: {
        nombre: ""
    }
});

AngryCat = Backbone.Model.extend({
    defaults: {
        votes: 0
    },

         addVote: function(){
             this.set('votes', this.get('votes') + 1);
         },

         rankUp: function() {
             this.set({rank: this.get('rank') - 1});
         },

         rankDown: function() {
             this.set({rank: this.get('rank') + 1});
         }
});

AngryCats = Backbone.Collection.extend({
    model: AngryCat,

          initialize: function(cats){
              var rank = 1;
              _.each(cats, function(cat) {
                  cat.set('rank', rank);
                  ++rank;
              });

              this.on('add', function(cat){
                  if( ! cat.get('rank') ){
                      var error =  Error("Cat must have a rank defined before being added to the collection");
                      error.name = "NoRankError";
                      throw error;
                  }
              });

              var self = this;

              MyApp.on("rank:up", function(cat){
                  if (cat.get('rank') === 1) {
                      // can't increase rank of top-ranked cat
                      return true;
                  }
                  self.rankUp(cat);
                  self.sort();
                  self.trigger("reset");
              });

              MyApp.on("rank:down", function(cat){
                  if (cat.get('rank') === self.size()) {
                      // can't decrease rank of lowest ranked cat
                      return true;
                  }
                  self.rankDown(cat);
                  self.sort();
                  self.trigger("reset");
              });

              MyApp.on("cat:disqualify", function(cat){
                  var disqualifiedRank = cat.get('rank');
                  var catsToUprank = self.filter(
                      function(cat){ return cat.get('rank') > disqualifiedRank; }
                      );
                  catsToUprank.forEach(function(cat){
                      cat.rankUp();
                  });
                  self.trigger('reset');
              });
          },

          comparator: function(cat) {
              return cat.get('rank');
          },

          rankUp: function(cat) {
              // find the cat we're going to swap ranks with
              var rankToSwap = cat.get('rank') - 1;
              var otherCat = this.at(rankToSwap - 1);

              // swap ranks
              cat.rankUp();
              otherCat.rankDown();
          },

          rankDown: function(cat) {
              // find the cat we're going to swap ranks with
              var rankToSwap = cat.get('rank') + 1;
              var otherCat = this.at(rankToSwap - 1);

              // swap ranks
              cat.rankDown();
              otherCat.rankUp();
          }
});

AngryCatView = Backbone.Marionette.ItemView.extend({
    template: "#angry_cat-template",
             tagName: 'tr',
             className: 'angry_cat',

             events: {
                 'click .rank_up span.glyphicon-chevron-up': 'rankUp',
                 'click .rank_down span.glyphicon-chevron-down': 'rankDown',
                 'click a.disqualify': 'disqualify'
             },

             initialize: function(){
                 this.listenTo(this.model, "change:votes", this.render);
             },

             rankUp: function(){
                 this.model.addVote();
                 MyApp.trigger("rank:up", this.model);
             },

             rankDown: function(){
                 this.model.addVote();
                 MyApp.trigger("rank:down", this.model);
             },

             disqualify: function(){
                 MyApp.trigger("cat:disqualify", this.model);
                 this.model.destroy();
             }
});

AngryCatsView = Backbone.Marionette.CompositeView.extend({
    tagName: "table",
              id: "angry_cats",
              className: "table table-striped table-bordered",
              template: "#angry_cats-template",
              itemView: AngryCatView,

              initialize: function(){
                  this.listenTo(this.collection, "sort", this.renderCollection);
              },

              appendHtml: function(collectionView, itemView){
                  collectionView.$("tbody").append(itemView.el);
              }
});

MyApp.addInitializer(function(options){
    var angryCatsView = new AngryCatsView({
        collection: options.cats
    });
    MyApp.mainRegion.show(angryCatsView);
});


$(document).ready(function() {

    var date = new Date();
    var d = date.getDate();
    var m = date.getMonth();
    var y = date.getFullYear();

    $('.calendario').fullCalendar({
        dayNames: ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
        dayNamesShort: ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa'],
        monthNames: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
                     'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        monthNamesShort: ['Ene', 'Feb', 'Mar', 'Abr', 'Mayo', 'Jun', 'Jul',
                     'Ago', 'Sep', 'Oct', 'Nov', 'Dic'],
        titleFormat: {
            month: 'MMM yyyy',                             // September 2009
            week: "MMM d[ yyyy]{ '&#8212;'[ MMM] d yyyy}", // Sep 7 - 13 2009
            day: 'd/MMM/yy'                  // 8/Sep/09
        },
        defaultView: 'basicDay',
        firstDay: 1,
        aspectRatio: 2,
        buttonText: {
            today: 'hoy',
            month: 'mes',
            week: 'semana',
            day:   'día',
        },
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,basicWeek,basicDay'
        },
        editable: true,
        events: [
    {
        title: 'All Day Event',
        start: new Date(y, m, 1)
    },
        {
            title: 'Long Event',
        start: new Date(y, m, d-5),
        end: new Date(y, m, d-2)
        },
        {
            id: 999,
        title: 'Repeating Event',
        start: new Date(y, m, d-3, 16, 0),
        allDay: false
        },
        {
            id: 999,
            title: 'Repeating Event',
            start: new Date(y, m, d+4, 16, 0),
            allDay: false
        },
        {
            title: 'Meeting',
            start: new Date(y, m, d, 10, 30),
            allDay: false
        },
        {
            title: 'Lunch',
            start: new Date(y, m, d, 12, 0),
            end: new Date(y, m, d, 14, 0),
            allDay: false
        },
        {
            title: 'Birthday Party',
            start: new Date(y, m, d+1, 19, 0),
            end: new Date(y, m, d+1, 22, 30),
            allDay: false
        },
        {
            title: 'Click for Google',
            start: new Date(y, m, 28),
            end: new Date(y, m, 29),
            url: 'http://google.com/'
        }
    ]
    });
    var cats = new AngryCats([
            new AngryCat({ name: 'Wet Cat', image_path: 'assets/images/cat2.jpg' }),
            new AngryCat({ name: 'Bitey Cat', image_path: 'assets/images/cat1.jpg' }),
            new AngryCat({ name: 'Surprised Cat', image_path: 'assets/images/cat3.jpg' })
            ]);

    MyApp.start({cats: cats});

    cats.add(new AngryCat({
        name: 'Cranky Cat',
        image_path: 'assets/images/cat4.jpg',
        rank: cats.size() + 1
    }));
});
