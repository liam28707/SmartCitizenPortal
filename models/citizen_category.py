from odoo import api,models,fields


class CitizenCategory(models.Model):
    """
    Represents a department/category for citizen requests.
    """

    _name = "citizen.category"
    _description = "Request Category"
    icon = fields.Char(string="Icon", default="fa-folder")

    #Table Columns
    name = fields.Char(required=True)
    description = fields.Text()
    request_count = fields.Integer(compute='_compute_request_count')
    request_ids = fields.One2many('citizen.request', 'category_id', string="Requests")
    
    # =========================
    # Methods
    # =========================
    def action_view_requests(self):
        return {
        'type': 'ir.actions.act_window',
        'name': 'Requests',
        'res_model': 'citizen.request',
        'view_mode': 'list,form',
        'domain': [('category_id', '=', self.id)],
        'context': {'group_by': 'status'}
    }

    @api.depends('request_ids') 
    def _compute_request_count(self):
        for record in self:
            record.request_count = len(record.request_ids)