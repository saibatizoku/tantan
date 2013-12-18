/*global TanTan */
'use strict';

TanTan.module('Views', function (Views, App, Backbone, Marionette, $) {

    Views.BaseItemView = Marionette.ItemView.extend({
        modelEvents: {
            'change': 'render'
        }
    });

     Views.UserDocView = Views.BaseItemView.extend({
         template: '#template-userdoc',
         className: 'panel panel-default'
    });

    Views.GranjaView = Views.BaseItemView.extend({
        tagName: 'li',
        template: '#template-granjaView',

        ui: {
            edit: '.edit'
        }

    });

    Views.EstanqueView = Views.BaseItemView.extend({
        tagName: 'li',
        template: '#template-estanqueView'
    });

    Views.EventView = Views.BaseItemView.extend({
    });

    Views.TaskView = Views.EventView.extend({
        onRender: function () {
            this.$el.removeClass('active completed');

            if (this.model.get('completed')) {
                this.$el.addClass('completed');
            } else {
                this.$el.addClass('active');
            }
        },
        events: {
            'click .destroy': 'destroy'
        },
        destroy: function () {
            this.model.destroy();
        }
    });

    Views.GranjasView = Marionette.CompositeView.extend({
        template: '#template-GranjasListCompositeView',
        className: 'container',
        itemView: Views.GranjaView,
        itemViewContainer: '#granjas-list',

        ui: {
            toggle: '#toggle-all'
        },

        events: {
            'click #toggle-all': 'onToggleAllClick'
        },

        collectionEvents: {
            'all': 'update'
        },

        onRender: function () {
            this.update();
        },

        update: function () {
            function reduceCompleted(left, right) {
                return left && right.get('completed');
            }

            var allCompleted = this.collection.reduce(reduceCompleted, true);
            
            this.ui.toggle.prop('checked', allCompleted);
            this.$el.parent().toggle(!!this.collection.length);
        },

        onToggleAllClick: function (e) {
            var isChecked = e. currentTarget.checked;

            this.collection.each(function (granja) {
                //granja.save({'completed': isChecked });
            });
        }
    });

    //Views.EstanquesView = Marionette.CompositeView.extend({
    //});
    //App.vent.on('granjas:filter', function (filter) {
	//	filter = filter || 'all';
	//	$('#tantanapp').attr('class', 'filter-' + filter);
	//});
});
