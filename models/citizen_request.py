from odoo import models,api,fields
from odoo.exceptions import ValidationError
import requests
import os
import textwrap

class CitizenRequest(models.Model):
    """
    Core model representing a citizen's complaint/request in the system.

    Features:
    - Tracks lifecycle (draft → submitted → in_progress → resolved)
    - Integrates AI for automatic classification + summarization
    - Supports attachments, feedback, and ratings
    """

    _name = "citizen.request"
    _description = "Citizen Request"

    # Enables tracking
    _inherit = ['mail.thread']

    #Table Columns
    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")

    category_id = fields.Many2one("citizen.category", string="Department")

    status = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved')
    ], default='draft', tracking=True)

    ai_summary = fields.Text(string="AI Summary")
    citizen_id = fields.Many2one("citizen.person", string="Citizen")

    request_date = fields.Datetime(default=fields.Datetime.now)
    resolved_date = fields.Datetime()

    location = fields.Char(string="Location")
    attachment_ids = fields.Many2many(
                'ir.attachment',
                string="Attachments"
            )

    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default = "low")

    feedback = fields.Text(string="Citizen Feedback")

    rating = fields.Selection([
        ('1', '1 ⭐'),
        ('2', '2 ⭐'),
        ('3', '3 ⭐'),
        ('4', '4 ⭐'),
        ('5', '5 ⭐')
    ], string="Rating")

    # =========================
    # MEthods
    # =========================

    @api.constrains('rating')
    def _check_rating(self):
        """
        Prevent users from rating a request unless it is resolved.
        Enforces business rule at ORM level.
        """
        for rec in self:
            if rec.rating and rec.status != 'resolved':
                raise ValidationError("You can only rate after the request is resolved.")
            
    @api.constrains('description')
    def _check_description(self):
        if not self.description:
            raise ValidationError("Description required")
        
    def action_submit(self):
        """
        Prevent users from rating a request unless it is resolved.
        Enforces business rule at ORM level.
        """
        for record in self:
            record.generate_ai_summary()
            record.status = 'submitted'

    def write(self, vals):
        """
        Override write to automatically set resolved_date
        when status transitions to 'resolved'.
        """

        if vals.get("status") == "resolved":
            vals["resolved_date"] = fields.Datetime.now()
        return super().write(vals)
    
    def action_mark_in_progress(self):
        for rec in self:
            rec.status = 'in_progress'

    def action_mark_resolved(self):
        for rec in self:
            rec.status = 'resolved'
            rec.resolved_date = fields.Datetime.now()

    def action_reopen(self):
        for rec in self:
            rec.status = 'in_progress'
    
    # AI summary generator
    def generate_ai_summary(self):
        """
        Calls Mistral API to:
        - Classify department
        - Assign priority
        - Generate 1-line summary

        Updates:
        - category_id
        - priority
        - ai_summary
        """
        
        api_key = os.getenv("MISTRAL_API_KEY")

        if not api_key:
            for record in self:
                record.ai_summary = "Missing MISTRAL_API_KEY"
            return

        for record in self:
            try:
                # Build prompt
                prompt = f"""
                    You are a government assistant.

                    From the complaint below:
                    1. Identify the department ( Electricity,Transport,Water Supply,Sanitation,Infrastructure,General Services,Environement,Public Health, Animal Welfare,Construction,Digital,Parking)
                    2. Write a short 1-line summary
                    3.Also determine priority:
                    - HIGH → danger, safety risk, urgent
                    - MEDIUM → affects daily life
                    - LOW → minor inconvenience

                    4. RULES:  Use these categories as your primary framework, but apply professional judgment for complex or safety-critical issues. 
                                1. ELECTRICITY: Sparks, wires, outages, flickering lights.
                                2. TRANSPORT: Potholes, traffic flow, road signs.
                                3. WATER SUPPLY: Leaks, pressure, contamination.
                                4. SANITATION: Trash, sewage, dead animals.
                                5. INFRASTRUCTURE: Bridges, pavements, public buildings.
                                6. GENERAL SERVICES: Noise, lost & found, inquiries.
                                7. ENVIRONMENT: Irrigation, parks, dying trees, dumping.
                                8. PUBLIC HEALTH: Food hygiene, pests, expired goods.
                                9. ANIMAL WELFARE: Strays, injured animals, noise.
                                10. CONSTRUCTION: Scaffolding, night noise, safety.
                                11. DIGITAL: App errors, QR codes, e-services.
                                12. PARKING: Blocked spots, meters, e-scooters.
                    LOGIC INSTRUCTIONS:
1. CHRONOLOGICAL CAUSE: Identify the very FIRST event that triggered the problem. If a pipe burst (Water) caused a traffic jam (Transport), the Department is WATER SUPPLY.
2. DISPATCH LOGIC: Ask "Which crew needs to arrive FIRST to stop the damage?" If the water is still flowing, the road crew cannot work. Therefore, it is WATER.
3. IGNORE SYMPTOMS: Traffic, noise, and crowds are usually symptoms. Focus on the physical object that is broken (Pipe, Wire, Asphalt).

                    Return ONLY:
                    Department: <value>
                    Priority: <value>
                    Summary: <value>

                    Complaint: {record.description}
                    """
                prompt = textwrap.dedent(prompt).strip()

                url = "https://api.mistral.ai/v1/chat/completions"

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": "mistral-small-latest",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 150
                }

                response = requests.post(url, headers=headers, json=payload)
                result = response.json()

                # Debug in case of error
                print("Mistral response:", result)

                # Parse result
                if "choices" in result and len(result["choices"]) > 0:
                    text = result["choices"][0]["message"]["content"].strip()

                    category_text = None
                    for line in text.splitlines():
                        if "department" in line.lower():
                            parts = line.split(":", 1)
                            if len(parts) > 1:
                                category_text = parts[1].strip().lower()
                        elif "priority" in line.lower():
                            priority_text = line.split(":")[1].strip().lower()
                            record.priority = priority_text if priority_text in ['low','medium','high'] else 'low'
                        elif "summary" in line.lower():
                            parts = line.split(":", 1)
                            if len(parts) > 1:
                                record.ai_summary = parts[1].strip()

                    if category_text:
                        category_model = self.env["citizen.category"]

                        # Try to find existing category
                        category = category_model.search([
                            ("name", "ilike", category_text)
                        ], limit=1)

                        if not category:
                            category = category_model.create({
                                "name": category_text.capitalize(),
                                "description": f"{category_text.capitalize()} related inquiries"
                            })

                        record.category_id = category

                else:
                    # fallback if API response invalid
                    record.ai_summary = "Mistral API error: " + str(result)

            except Exception as e:
                record.ai_summary = f"Error: {str(e)}"