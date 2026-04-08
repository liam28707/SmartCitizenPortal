from odoo import api,models,fields
from odoo.exceptions import ValidationError
from datetime import date
import re

class Citizen(models.Model):
    """
    Represents a citizen in the system.

    Responsibilities:
    - Stores identity and personal data
    - Validates national ID format and consistency
    - Enforces age constraints
    - Links to citizen requests
    """
    _name = "citizen.person"
    _description = "Citizen"

    #Table COlumns
    name = fields.Char(required=True)

    # EmiratesID style national ID enforcment 
    national_id = fields.Char(string="National ID", help="Format: 783-YYYY-7890123-4")
    dob = fields.Date(string="Date of Birth")
    phone = fields.Char()
    image = fields.Binary(string="Image")
    is_verified = fields.Boolean(string="Verified", compute="_compute_verified", store=True)
    _sql_constraints = [
        ('unique_national_id', 'unique(national_id)', 'National ID must be unique!')
    ]

    request_ids = fields.One2many(
        'citizen.request',
        'citizen_id',
        string="Requests"
    )

    # =========================
    # Methods
    # =========================
    
    @api.depends('national_id')
    def _compute_verified(self):
        for record in self:
            record.is_verified = bool(record.national_id)
    
    @api.constrains('dob')
    def _check_dob(self):
        for record in self:
            if record.dob:
                today = date.today()
                age = today.year - record.dob.year

                if record.dob > today:
                    raise ValidationError("Date of birth cannot be in the future.")

                if age < 0:
                    raise ValidationError("Invalid date of birth.")

                if age < 10:
                    raise ValidationError("Citizen must be at least 10 years old.")

                if age > 120:
                    raise ValidationError("Age seems unrealistic.")

    @api.constrains('national_id', 'dob')
    def _check_national_id(self):
        for record in self:
            if not record.national_id:
                continue
            
            existing = self.search([
            ('national_id', '=', record.national_id),
            ('id', '!=', record.id)
            ], limit=1)

            if existing:
                raise ValidationError("This National ID already exists!")
        
            # 1. Regex Pattern: 783 - 4digits - 7digits - 1digit
            # ^783-\d{4}-\d{7}-\d{1}$
            pattern = r'^783-\d{4}-\d{7}-\d{1}$'
            if not re.match(pattern, record.national_id):
                raise ValidationError(
                    "Invalid National ID format! Use: 783-YYYY-XXXXXXX-D "
                    "(e.g., 783-1990-1234567-8)"
                )

            # 2. Year Validation: Ensure the ID year matches the DOB year
            if record.dob:
                id_parts = record.national_id.split('-')
                id_year = id_parts[1]  # The YYYY part
                dob_year = str(record.dob.year)

                if id_year != dob_year:
                    raise ValidationError(
                        f"National ID year ({id_year}) does not match "
                        f"the Date of Birth year ({dob_year})."
                    )
                
    def action_submit_request(self):
        if not self.is_verified:
            raise ValidationError("Citizen must be verified (valid National ID required).")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Submit Request',
            'res_model': 'citizen.request',
            'view_mode': 'form',
            'context': {'default_citizen_id': self.id},
        }
    
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or record.name.strip() == "":
                raise ValidationError("Name cannot be empty.")