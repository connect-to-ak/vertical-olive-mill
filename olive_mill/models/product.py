# -*- coding: utf-8 -*-
# Copyright 2018 Barroux Abbey (https://www.barroux.org/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    olive_type = fields.Selection([
        # Olives are not handled as products
        ('oil', 'Olive Oil'),
        ('bottle', 'Oil Bottle'),
        ('analysis', 'Analysis'),
        ('extra_service', 'Extra Service'),
        ('service', 'Production Service'),
        ], string='Olive Type')
    olive_culture_type = fields.Selection([
        ('regular', 'Regular'),
        ('organic', 'Organic'),
        ('conversion', 'Conversion'),
        ], string='Culture Type')
    olive_bottle_free_full = fields.Boolean(
        string="Not Invoiced when Full")
    olive_invoice_service_ids = fields.Many2many(
        'product.product', 'product_template_olive_invoice_service_rel',
        'product_tmpl_id', 'product_id',
        string='Extra Production Services To Invoice',
        domain=[('olive_type', '=', 'service')])

    # DUPLICATED in product product
    @api.onchange('olive_type')
    def olive_type_change(self):
        liter_uom = self.env.ref('product.product_uom_litre')
        pce_uom = self.env.ref('product.product_uom_unit')
        if self.olive_type == 'oil':
            if self.uom_id != liter_uom:
                self.uom_id = liter_uom
                self.uom_po_id = liter_uom
            self.tracking = 'lot'
        if self.olive_type in ('service', 'extra_service'):
            self.type = 'service'
        elif self.olive_type == 'analysis':
            self.type == 'consu'
        if not self.olive_type:
            self.olive_culture_type = False

    @api.constrains('olive_type', 'uom_id', 'olive_culture_type', 'type')
    def check_olive_type(self):
        liter_uom = self.env.ref('product.product_uom_litre')
        unit_categ_uom = self.env.ref('product.product_uom_categ_unit')
        for pt in self:
            if pt.olive_type == 'oil':
                if not pt.olive_culture_type:
                    raise ValidationError(_(
                        "Product '%s' has an Olive Type 'Olive Oil', so a "
                        "culture type must also be configured.")
                        % pt.display_name)
                if pt.uom_id != liter_uom:
                    raise ValidationError(_(
                        "Product '%s' has an Olive Type 'Olive Oil' that "
                        "require 'Liter' as it's unit of measure "
                        "(current unit of measure is %s).")
                        % (pt.display_name, pt.uom_id.display_name))
                if pt.tracking != 'lot':
                    raise ValidationError(_(
                        "Product '%s' has an Olive Type (%s) that require "
                        "tracking by lots.") % (
                            pt.display_name, pt.olive_type))
            if (
                    pt.olive_type in ('bottle', 'analysis') and
                    pt.uom_id.category_id != unit_categ_uom):
                raise ValidationError(_(
                    "Product '%s' has an Olive Type 'Bottle' or 'Analysis' "
                    "that require a unit of measure that belong to the "
                    "'Unit' category (current unit of measure: %s).")
                    % (pt.display_name, pt.uom_id.display_name))
            if pt.olive_type == 'analysis' and pt.type != 'consu':
                raise ValidationError(_(
                    "Product '%s' has an Olive Type 'Analysis', so "
                    "it must be configured as a consumable.")
                    % pt.display_name)
            if (
                    pt.olive_type in ('service', 'extra_service') and
                    pt.type != 'service'):
                raise ValidationError(_(
                    "Product '%s' has an Olive Type 'Production Service' or "
                    "'Extra Service' so it must be configured as a Service.") % (
                        pt.display_name))


class ProductProduct(models.Model):
    _inherit = 'product.product'

    shrinkage_prodlot_id = fields.Many2one(
        'stock.production.lot', string='Shrinkage Production Lot',
        copy=False,
        help="Select the generic production lot that will be used for all "
        "moves of this olive oil product to the shrinkage tank.")

    # DUPLICATED in product template
    @api.onchange('olive_type')
    def olive_type_change(self):
        liter_uom = self.env.ref('product.product_uom_litre')
        pce_uom = self.env.ref('product.product_uom_unit')
        if self.olive_type == 'oil':
            if self.uom_id != liter_uom:
                self.uom_id = liter_uom
                self.uom_po_id = liter_uom
            self.tracking = 'lot'
        if self.olive_type in ('service', 'extra_service'):
            self.type = 'service'
        elif self.olive_type == 'analysis':
            self.type == 'consu'
        if not self.olive_type:
            self.olive_culture_type = False
