MyApp = new Backbone.Marionette.Application();

MyApp.addRegions({
    mainRegion: "#content"
});

Granja = Backbone.Model.extend({
    defaults: {
        nombre: "",
        tipo: "granja",
        localidad: "",
        contacto: "",
        direccion: "",
        estado: "",
        municipio: "",
        razonsocial: ""
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

var g1 = {"_id": "fea96b46aeb02badb26b3a37460065cc", "tipo": "granja", "_rev": "1-1498db99b23ce822cf075d42c996380e", "direccion": "km. 1.5 camino a El Zacatal", "razonsocial": "Sistemas Productivos Rurales de Jamapa, S.C. de R.L.", "localidad": "El Estero Norte", "nombre": "Xamapan", "contacto": "mochoguana", "estado": "Veracruz", "municipio": "Jamapa"};
