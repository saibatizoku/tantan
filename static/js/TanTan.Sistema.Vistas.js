/*global TanTanApp */
'use strict';

TanTan.module('Sistema.Vistas', function(SistemaView, App, Backbone) {

    SistemaView.HojaView = Marionette.ItemView.extend({
        template: '#template-hoja',
        tagName: 'li',
        className: 'thumbnail nodo hoja',
        ui: {
            'lnk': '> a'
        },
        triggers: {
            'click @ui.lnk': 'tree:nav:click'
        },
        isActive: function () {
            return this.$el.hasClass('active');
        },
        toggleSelect: function () {
            if (!this.isActive()) {
                this.toggleActive();
                //this.$el.siblings().find('.in').collapse('toggle');
            }
        },
        toggleActive: function () {
            this.$el.siblings().find('.active').removeClass('active');
            this.$el.siblings().removeClass('active');
            this.$el.toggleClass('active');
        }
    });
    SistemaView.ArbolView = Marionette.CompositeView.extend({
        template: '#template-rama',
        tagName: 'li',
        itemViewContainer: '.raiz-listado',
        className: 'thumbnail nodo',
        ui: {
            'lnk': '> a'
        },
        triggers: {
            'click @ui.lnk': 'tree:nav:click'
        },
        initialize: function () {
            var nodes = this.model.nodos;
            this.collection = nodes;
        },
        //onShow: function () {
        //onShowCalled: function () {
        onDomRefreshed: function () {
            if (this.isBranch()) {
                this.$itemViewContainer.collapse();
                this.$itemViewContainer.collapse('toggle');
            }
        },
        onRender: function () {
            if (this.isBranch()) {
                this.$el.addClass('rama');
            } else {
                this.$el.addClass('hoja');
            }
            var url = this.model.url();
            if (url) {
                this.ui.lnk.attr('href', '#'+url);
            }
        },
        isBranch: function () {
            if ((this.collection) && (this.collection.length > 0)) {
                return true;
            } else {
                return false;
            }
        },
        //appendHtml: function (collectionView, itemView) {
        buildItemView: function (item, ItemViewType, itemViewOptions) {
            // build the final list of options for the item view type
            var options = _.extend({model: item}, itemViewOptions);
            // create the item view instance
            if (!this.isBranch()) {
                ItemViewType = Sistema.Vistas.HojaView;
            }
            var view = new ItemViewType(options);
            //this.on('itemview:tree:nav:click', function (args) {
            this.listenTo(view, 'tree:nav:click itemview:nav:click', function (args) {
                //ab.log('ITEMVIEW NAV CLICK', args.model.toJSON()); //, this, args);
                App.vent.trigger('nav:click', args);
            });
            return view;
        },
        isActive: function () {
            return this.$el.hasClass('active');
        },
        toggleSelect: function () {
            if (this.isBranch()) {
                this.toggleActive();
                this.toggleCollapse();
            } else {
                if (!this.isActive()) {
                    this.toggleActive();
                }
            }
        },
        toggleActive: function () {
            this.$el.siblings().find('.active').removeClass('active');
            this.$el.siblings().removeClass('active');
            this.$el.toggleClass('active');
        },
        toggleCollapse: function () {
            this.$el.siblings().find('.in').collapse('toggle');
            this.$itemViewContainer.find('.in').collapse('toggle');
            this.$itemViewContainer.find('.active').removeClass('active');
            this.$itemViewContainer.collapse('toggle');
        }
    });

    SistemaView.RaizView = Marionette.CompositeView.extend({
        template: '#template-nav-root',
        className: 'col-sm-3 node-tree',
        itemView: SistemaView.ArbolView,
        itemViewContainer: '#raiz-listado',
        initialize: function () {
            this.on('itemview:tree:nav:click', function (args) {
                //ab.log('RAIZ itemview:tree:nav:click', args.model.toJSON());
                //args.toggleCollapse();
                App.vent.trigger('nav:click', {view: args, model: args.model, collection: args.collection});
                //this.toggleCollapse();
            });
        },
        treeUpdate: function (tree_info) {
            //ab.log('TREE INFO CALL', tree_info);
            this.collection.reset(tree_info);
        }
    });

    SistemaView.Main = Marionette.Layout.extend({
        template: '#template-main',
        className: 'container',
        regions: {
            one: '#region-one',
            two: '#region-two',
            three: '#region-three'
        }
    });

    SistemaView.DocContents = Marionette.Layout.extend({
        template: '#template-main-docs',
        className: 'col-sm-9',
        regions: {
            tools: '#content-tools',
            docs: '#content-docs'
        }

    });

    SistemaView.DocNav = Marionette.ItemView.extend({
        template: '#template-item',
        className: 'list-group-item',
        tagName: 'a',
        attributes: {
            'href': '#'
        },
        //events: {
        //    'click': 'navClick'
        //},
        triggers: {
            'click': 'doc:nav:click'
        },
        navClick: function (e) {
            if (!this.$el.hasClass('active')) {
            //    this.toggleActive(this.$el);
            //} else {
            //    this.$el.toggleClass('active');
                this.toggleActive(this.$el);
                this.trigger('nav:click', {el: this.$el, view: this});
            }
        },
        toggleActive: function (el) {
            this.$el.parent().find(".active").toggleClass('active');
            el.toggleClass('active');
        },
        buildItemView: function(item, ItemViewType, itemViewOptions){
            // build the final list of options for the item view type
            var options = _.extend({model: item}, itemViewOptions);
            // create the item view instance
            var view = new ItemViewType(options);
            //ab.log('BUILT View', view);
            App.vent.listenTo(view, 'doc:nav:items', ab.log);
            // return it
            return view;
        }
    });

    SistemaView.ListaEventos = Marionette.CompositeView.extend({
        template: '#template-item-list',
        className: 'col-sm-3',
        itemView: SistemaView.DocNav,
        itemViewContainer: '#lista-docs',
        initialize: function () {
            this.$navel = this.$el;
        },
        buildItemView: function(item, ItemViewType, itemViewOptions){
            // build the final list of options for the item view type
            var options = _.extend({model: item}, itemViewOptions);
            // create the item view instance
            var view = new ItemViewType(options);
            ab.log('BUILT View', view);
            App.vent.listenTo(view, 'doc:nav:items', ab.log);
            // return it
            return view;
        }
    });

    SistemaView.Contenidos = Marionette.CompositeView.extend({
        template: '#template-main-contents',
        className: 'thumbnail'
    });

    SistemaView.Sensores = Marionette.CompositeView.extend({
        template: '#template-main-sensores',
        className: 'col-sm-12 thumbnail'
    });

    SistemaView.GranjaView = Marionette.ItemView.extend({
        template: '#template-main-granja'
    });

    SistemaView.EstanqueView = Marionette.ItemView.extend({
        template: '#template-main-estanque',
        onRender: function () {
            var gid = "fea96b46aeb02badb26b3a37460065cc";
            var gid2= "818304e02559db2f83fcdd93e500055b";
            if ((this.model.get('granja_id') == gid) || (this.model.get('granja_id') == gid2)) {
                this.printSensors();
            } else {
                this.$('.valor').text('');
            }
        },
        printSensors: function () {
            //this.$('.carousel').carousel();
            var hr = new Date().getHours();
            if ((hr > 6) && (hr < 21)) {
                ab.log('hora en horario', hr);
                hr -= 6;
            } else {
                hr = 3;
            }
            this.$(".sensor-ph").each(function (index, item) {
                var random = new TimeSeries();
                var graf = $(item).find('.lectura-graf')[0];
                setInterval(function() {
                    var ft = Math.abs(0.567*Math.sin((hr -7.0)*Math.PI/16) + 7.01) + Math.random() * 0.001;
                    $(item).find('.valor').text(ft.toFixed(1)+"");
                    random.append(new Date().getTime(), ft);
                }, 500);
                var chart = new SmoothieChart({
                    millisPerPixel: 50,
                    minValue: 6.8,
                    maxValue: 7.5
                });
                chart.addTimeSeries(random, { strokeStyle: 'rgba(0, 255, 0, 1)', fillStyle: 'rgba(0, 255, 0, 0.2)', lineWidth: 2 });
                chart.streamTo(graf, 500);
                ab.log('buscando VALOR', $(item).find('.valor'));
            });
            this.$(".sensor-od").each(function (index, item) {
                var random = new TimeSeries();
                var graf = $(item).find('.lectura-graf')[0];
                setInterval(function() {
                    //1.89 sen((t-9.0)*pi/16) + 5.54
                    var ft  = Math.abs(1.89*Math.sin((hr-9.0)*Math.PI/16) + 4.505) + Math.random() * 0.07;
                    $(item).parent().find('.valor').text(ft.toFixed(1)+" %");
                    random.append(new Date().getTime(), ft);
                }, 500);
                var chart = new SmoothieChart({
                    millisPerPixel: 50,
                    minValue: 4.1,
                    maxValue: 6.9
                });
                chart.addTimeSeries(random, { strokeStyle: 'rgba(0, 255, 0, 1)', fillStyle: 'rgba(0, 255, 0, 0.2)', lineWidth: 2 });
                chart.streamTo(graf, 500);
                ab.log('buscando VALOR', $(item).find('.valor'));
            });
            this.$(".sensor-amonio").each(function (index, item) {
                var random = new TimeSeries();
                var graf = $(item).find('.lectura-graf')[0];
                setInterval(function() {
                    var ft  = Math.abs(0.6336*Math.sin((hr-5.0)*Math.PI/16) + 0.305) - Math.random() * 0.031;
                    $(item).parent().find('.valor').text(ft.toFixed(1)+" mg/L");
                    random.append(new Date().getTime(), ft);
                }, 500);
                var chart = new SmoothieChart({
                    millisPerPixel: 50,
                    minValue: 0.01,
                    maxValue: 1.0
                });
                chart.addTimeSeries(random, { strokeStyle: 'rgba(0, 255, 0, 1)', fillStyle: 'rgba(0, 255, 0, 0.2)', lineWidth: 2 });
                chart.streamTo(graf, 500);
                ab.log('buscando VALOR', $(item).find('.valor'));
            });
            this.$(".sensor-nitratos").each(function (index, item) {
                var random = new TimeSeries();
                var graf = $(item).find('.lectura-graf')[0];
                setInterval(function() {
                    var ft = Math.abs(0.44*Math.sin((hr-6.0)*Math.PI/16) +0.11) - Math.random() * 0.051;
                    $(item).parent().find('.valor').text(ft.toFixed(1)+" mg/L");
                    random.append(new Date().getTime(), ft);
                }, 500);
                var chart = new SmoothieChart({
                    millisPerPixel: 50,
                    minValue: 0.01,
                    maxValue: 0.6
                });
                chart.addTimeSeries(random, { strokeStyle: 'rgba(0, 255, 0, 1)', fillStyle: 'rgba(0, 255, 0, 0.2)', lineWidth: 2 });
                chart.streamTo(graf, 500);
                ab.log('buscando VALOR', $(item).find('.valor'));
            });
            this.$(".sensor-temp").each(function (index, item) {
                var random = new TimeSeries();
                var graf = $(item).find('.lectura-graf')[0];
            });
            this.$(".nodo-energia").each(function (index, item) {
                var random1 = new TimeSeries();
                var random2 = new TimeSeries();
                var random3 = new TimeSeries();
                var grafv = $(item).find('.sensor-volt .lectura-graf')[0];
                var grafc = $(item).find('.sensor-corriente .lectura-graf')[0];
                var grafp = $(item).find('.sensor-potencia .lectura-graf')[0];
                setInterval(function() {
                    var volt = 123 + Math.random()* (4.48*Math.sin(hr-5.0));
                    var corr = 14.3 + Math.random()* (0.78*Math.sin(hr-3.0));
                    var potR = volt*corr;
                    //random.append(new Date().getTime(), Math.random() * 10000);
                    $(item).find('.sensor-volt .valor').text(volt.toFixed(1)+" V");
                    $(item).find('.sensor-corriente .valor').text(corr.toFixed(1)+" A");
                    $(item).find('.sensor-potencia .valor').text(potR.toFixed(1)+" W");
                    random1.append(new Date().getTime(), volt);
                    random2.append(new Date().getTime(), corr);
                    random3.append(new Date().getTime(), potR);
                }, 500);
                var chart1 = new SmoothieChart({
                    millisPerPixel: 50,
                    minValue: 0,
                    maxValue: 130
                });
                var chart2 = new SmoothieChart({
                    millisPerPixel: 50,
                    minValue: 0,
                    maxValue: 20.0
                });
                var chart3 = new SmoothieChart({
                    millisPerPixel: 50,
                    minValue: 0,
                    maxValue: 2000
                });
                chart1.addTimeSeries(random1, { strokeStyle: 'rgba(0, 255, 0, 1)', fillStyle: 'rgba(0, 255, 0, 0.2)', lineWidth: 2 });
                chart2.addTimeSeries(random2, { strokeStyle: 'rgba(0, 255, 0, 1)', fillStyle: 'rgba(0, 255, 0, 0.2)', lineWidth: 2 });
                chart3.addTimeSeries(random3, { strokeStyle: 'rgba(0, 255, 0, 1)', fillStyle: 'rgba(0, 255, 0, 0.2)', lineWidth: 2 });
                chart1.streamTo(grafv, 500);
                chart2.streamTo(grafc, 500);
                chart3.streamTo(grafp, 500);
                ab.log('buscando VALOR', $(item).parent().find('.valor'));
            });
            //var item = this.$(".lectura-graf").get();
            //ab.log('attaching graph', item);
            //chart.streamTo(item, 500);

        }
    });

    SistemaView.Modal = Marionette.ItemView.extend({
        template: '#template-modal',
        className: 'well',
        ui: {
            'modal': '#modal-form'
        },
        onShowCalled: function () {
            //this.ui.modal.modal();
        }
    });

});
