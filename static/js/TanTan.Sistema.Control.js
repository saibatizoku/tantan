/*global TanTanApp */
'use strict';

TanTan.module('Sistema.Control', function(CalControl, App, Backbone) {
    CalControl.Router = Marionette.AppRouter.extend({
        appRoutes: {
            "home": "goHome",
            "sensors": "goTwo",
            "agenda": "goThree",
            "nodos/:id": "goNodo"
        }
    });
    CalControl.Controller = Marionette.Controller.extend({
        initialize: function () {
            this.navbar = new App.Layout.Nav();
            this.navmenu = new App.Layout.NavUserMenu();
            this.navactions = new App.Layout.NavActions();
            this.content = new App.Sistema.Vistas.Main();
            this.granjas = new App.Sistema.Granjas();
            this.nodos = new App.Sistema.Nodos();
            this.listenTo(App.vent, 'nav:click', function (args) {
                args.view.toggleSelect();
                ab.log('controller nav', args.model.toJSON(), args.view.$el.hasClass('active'));
                var path = args.view.$el.parentsUntil('nodo', '.nav-root').text();
                ab.log('path:', args.model.url());
                switch (args.model.get('tipo')) {
                    case 'granja':
                        ab.log('GRANJA SELECTED');
                        var gview = new TanTan.Sistema.Vistas.GranjaView({
                            model: args.model
                        });
                        TanTan.main.currentView.two.currentView.docs.show(gview);
                        break;
                    case 'estanque':
                        ab.log('ESTANQUE SELECTED');
                        var eview = new TanTan.Sistema.Vistas.EstanqueView({
                            model: args.model
                        });
                        TanTan.main.currentView.two.currentView.docs.show(eview);
                        break;

                    default:
                        ab.log('DEFAULT SELECTED');
                        var doc_contents = new App.Sistema.Vistas.Contenidos({model: args.model});
                        TanTan.main.currentView.two.currentView.docs.show(doc_contents);
                        break;
                }
            });
            //var granjas = [{'_id': 'xamapan-1', 'title': 'Xamapan'}, {'_id': 'exp-1', 'title': 'Granja Experimental'}];
            App.nav.show(this.navbar);
            App.main.show(this.content);
            //this.goHome();
        },
        showNav: function () {
            //ab.log('showNav', this.user);
            if (this.user) {
                var navmenu = new App.Layout.NavUserMenu();
                App.nav.currentView.menu.show(navmenu);
                var navactions = new App.Layout.NavUserActions();
                App.nav.currentView.actions.show(navactions);
            } else {
                var navactions = new App.Layout.NavActions();
                App.nav.currentView.menu.close();
            }
            App.nav.currentView.actions.show(navactions);
        },
        goHome: function (user) {
            this.goOne();
        },
        goNodo: function (nid) {
            ab.log('yendo a nodo', nid);
            var contents = App.main.currentView.two.currentView;
            var items2 = new App.Sistema.Vistas.GranjaView();
            contents.docs.show(items2);
        },
        goOne: function () {
            var content = new App.Sistema.Vistas.Main();
            this.showNav()
            App.main.show(content);
            if (this.user) {
                App.nav.currentView.menu.currentView.ui.navhome.trigger('click');
                var raiz = new App.Sistema.Nodo({'nombre': 'Granjas acuícolas'});
                var groot = this.treeNav(raiz, this.granjas);
                //groot.on('itemview:tree:nav:click', function (args) {
                //    ab.log('itemview:tree:nav:click', this, args);
                //    //args.view.toggleCollapse();
                //    //this.toggleCollapse();
                //});
                groot.listenTo(App.vent, 'granjas:tree', groot.treeUpdate);
                content.one.show(groot);
                var doc_contents = new App.Sistema.Vistas.DocContents();
                content.two.show(doc_contents);
                var items2 = new App.Sistema.Vistas.Contenidos();
                //var items2 = new App.Sistema.Vistas.GranjaView();
                var items3 = new App.Sistema.Vistas.Modal();
                //doc_contents.tools.show(items3);
                doc_contents.docs.show(items2);
            } else {
                var doc_contents = new App.Layout.MainContent();
                content.two.show(doc_contents);
            }
            //var items = new App.Sistema.Vistas.ListaEventos({collection: this.items});

        },
        treeNav: function (root, nodes) {
            root.nodos = this.nodes;
            //var items = new App.Sistema.Vistas.RaizView({collection: this.nodos});
            return new App.Sistema.Vistas.RaizView({model: root, collection: nodes});
        },
        goTwo: function () {
            var content = new App.Sistema.Vistas.Main();
            this.showNav()
            App.main.show(content);
            if (this.user) {
                App.nav.currentView.menu.currentView.ui.navsensors.trigger('click');
                var raiz = new App.Sistema.Nodo({'nombre': 'Nodos de la granja'});
                //var items = new App.Sistema.Vistas.RaizView({collection: this.nodos});
                var items = this.treeNav(raiz, this.nodos);
                items.listenTo(App.vent, 'nodos:info', items.treeUpdate);
                //granjas.listenTo(App.vent, 'granjas:info', granjas.treeUpdate);
                //var items = new App.Sistema.Vistas.ArbolView({model: raiz});
                var items2 = new App.Sistema.Vistas.Contenidos();
                content.one.show(items);
                var doc_contents = new App.Sistema.Vistas.DocContents();
                content.two.show(doc_contents);
                var items2 = new App.Sistema.Vistas.Sensores();
                doc_contents.docs.show(items2);
            } else {
                var doc_contents = new App.Layout.MainContent();
                content.two.show(doc_contents);
            }
        },
        goThree: function () {
            var content = new App.Sistema.Vistas.Main();
            this.navmenu.ui.navagenda.trigger('click');
            App.main.show(content);
            var items = new App.Sistema.Vistas.ListaEventos({collection: this.items});
            var items2 = new App.Sistema.Vistas.Contenidos();
            var items3 = new App.Sistema.Vistas.Modal();
            content.one.show(items);
            content.two.show(items2);
            content.three.show(items3);
        }
    });
});
