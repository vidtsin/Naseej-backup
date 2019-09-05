odoo.define('pos_product_serial.models', function (require) {
"use strict";

    
    var exports = require('point_of_sale.models');
    var PosPopups = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var screens = require('point_of_sale.screens');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;

    var Orderline = exports.Orderline;
    exports.Orderline = exports.Orderline.extend({

        get_required_number_of_lots: function(){
            var lots_required = Orderline.prototype.get_required_number_of_lots.apply(this, arguments);
            if (this.product.tracking == 'lot') {
                lots_required = this.pack_lot_lines.length;
                if (lots_required == 0){
                    lots_required = 1
                }
            }
            return lots_required;
        },

    });

    var Packlotline = exports.Packlotline;
    exports.Packlotline = exports.Packlotline.extend({
        defaults: {
            lot_name: null,
            location_id : null,
        },

        init_from_JSON: function(json) {
            Packlotline.prototype.init_from_JSON.apply(this, arguments);
            this.set_location_id(json.location_id);
        },

        set_location_id: function(location_id){
            this.set({location_id : _.str.trim(location_id) || null});
        },
        get_location_id: function(){
            return this.get('location_id');
        },
        export_as_JSON: function(){
            var res = Packlotline.prototype.export_as_JSON.apply(this, arguments);
            res['location_id'] = this.get_location_id()
            return res
        },

    });


    var PackLotLinePopupWidget = PosPopups.extend({
        template: 'PackLotLinePopupWidget',
        events: _.extend({}, PosPopups.prototype.events, {
            'change #wh-loc': '_onChangeLocation',
            'change .input-serial': '_onChangeCheckbox',
        }),

        show: function(options){
            this._super(options);
            var self = this
            var product_id = options.order_line.product.id
            var pack_lot_lines = options.pack_lot_lines;
            $('.modal-dialog').empty();
//            pack_lot_lines.remove_empty_model();
            rpc.query({
                model: 'pos.config',
                method: 'get_locations',
                args: [[this.pos.config.id]],
            }).then(function(result){
                if (result){
                    $('.modal-dialog').append($(QWeb.render('ProductSerials', {locations:result,options:options})));
                    var location_id = $('#wh-loc').val();
                    self.set_location_id(location_id);
                    rpc.query({
                        model: 'stock.quant',
                        method: 'get_serials',
                        args: [location_id,product_id],
                    }).then(function(data){
                        if(data){
                            if (pack_lot_lines.models){
                                console.log("<<<<<<<<<<",pack_lot_lines.models)
                                var arrayLength = pack_lot_lines.models.length;
                                for (var i = 0; i < arrayLength; i++) {
                                    var lot_name = pack_lot_lines.models[i].attributes.lot_name
                                    var location_id = pack_lot_lines.models[i].attributes.location_id
                                    var cid = pack_lot_lines.models[i].cid
                                    if (lot_name && location_id){
                                        var DataLength = data.length;
                                        if (DataLength > 0){
                                            for (var j = 0; j < DataLength; j++) {
                                               if (lot_name == data[j].lot_name && location_id == data[j].location_id){
                                                    data[j].cid = cid
                                               }
                                            }
                                        }

                                    }
                                }
                            }
                            $('.orderlines-serials').empty();
                            $('.orderlines-serials').append($(QWeb.render('TableContent', {serials:data})));
                        }
                    });
                }
            });

        },

        _onChangeLocation:function(ev){
            var location_id = $(ev.currentTarget).val();
            this.set_location_id(location_id);
            var product_id = this.options.order_line.product.id;
            var pack_lot_lines = this.options.pack_lot_lines;
            pack_lot_lines.remove_empty_model();
            rpc.query({
                model: 'stock.quant',
                method: 'get_serials',
                args: [location_id,product_id],
            }).then(function(res){
                if(res){
                    if (pack_lot_lines.models){
                        var ll = pack_lot_lines.models.length;
                        for (var a = 0; a < ll; a++) {
                            var lot_name = pack_lot_lines.models[a].attributes.lot_name
                            var location_id = pack_lot_lines.models[a].attributes.location_id
                            var cid = pack_lot_lines.models[a].cid
                            if (lot_name && location_id){
                                var resLength = res.length;
                                if (resLength > 0){
                                    for (var b = 0; b < resLength; b++) {
                                       if (lot_name == res[b].lot_name && location_id == res[b].location_id){
                                            res[b].cid = cid
                                       }
                                    }
                                }

                            }
                        }
                    }
                    $('.orderlines-serials').empty();
                    $('.orderlines-serials').append($(QWeb.render('TableContent', {serials:res})));
                }
            });
        },


        _onChangeCheckbox:function(ev,cc){
            var self = this
            var pack_lot_lines = this.options.pack_lot_lines
            var element = $(ev.currentTarget);
            var checked = $(ev.currentTarget).prop("checked");
            if (checked){
                var cid = element.attr('cid'),
                    lot_name = element.val(),
                    location_id = self.get_location_id()
                var pack_line = pack_lot_lines.get({cid: cid});
                if (pack_line){
                    pack_line.set_lot_name(lot_name);
                    pack_line.set_location_id(location_id);
                }else{
                    var pack_line = pack_lot_lines.add(new exports.Packlotline({}, {'order_line': self.options.order_line}));
                    pack_line.add()
                    pack_line.set_lot_name(lot_name);
                    pack_line.set_location_id(location_id);
                }
            }else{
                var cid = element.attr('cid'),
                    lot_name = element.val(),
                    location_id = self.get_location_id();
                var pack_line = pack_lot_lines.get({cid: cid});
                if (pack_line){
                    pack_line.remove();
                }

            }
        },

        click_confirm: function(){
            var self = this;
            var pack_lot_lines = this.options.pack_lot_lines
            pack_lot_lines.remove_empty_model();
            pack_lot_lines.set_quantity_by_lot();
            self.options.order.save_to_db();
            self.options.order_line.trigger('change', self.options.order_line);
            self.gui.close_popup();

        },

        get_location_id: function(){
            return this.get('location_id');
        },
        set_location_id: function(location_id){
            this.set({location_id : _.str.trim(location_id) || null});
        },

    });
    gui.define_popup({name:'packlotline', widget: PackLotLinePopupWidget});


    screens.ActionpadWidget.include({

        renderElement: function() {
            var self = this;
            this._super();
            this.$('.pay').click(function(){
            console.log("Helllllllllllo");
                var order = self.pos.get_order();
                var has_valid_product_lot = _.every(order.orderlines.models, function(line){
                    return line.has_valid_product_lot();
                });
                if(!has_valid_product_lot){
                    self.gui.show_popup('error',{
                         'title': _t('Empty Serial/Lot Number'),
                        'body':  _t('One or more product(s) required serial/lot number.'),
                    });
                }else{
                    self.gui.show_screen('payment');
                }
            });
            this.$('.set-customer').click(function(){
                self.gui.show_screen('clientlist');
            });
        }

    });


});
