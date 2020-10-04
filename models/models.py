# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class Topic(models.Model):
	_name = 'training.topic'
	_description = 'Course Topic'

	name = fields.Char(string="Titre", required=True)

	_sql_constraints = [
						('name_unique',
         				'UNIQUE(name)',
         				"Le titre du thème doit etre unique"),
					   ]

class Course(models.Model):
	_name = 'training.course'
	_description = 'Course'

	name = fields.Char(string="Titre", required=True)
	description = fields.Text(string="description")
	topic_id = fields.Many2one('training.topic',string="Thème",required = True)
	duration = fields.Integer(string="Durée")

	_sql_constraints = [
						('name_unique',
         				'UNIQUE(name)',
         				"Le titre du cours doit etre unique"),
					   ]

	@api.onchange('duration')
	def _check_duration(self):
		#Duration must be positive
		if self.duration < 0:
			raise UserError(_("La durée doit etre positive "))


class Session(models.Model):
	_name = 'training.session'
	_description = 'Sessions'

	course_id = fields.Many2one('training.course', string="Cours", ondelete="cascade", required=True)
	start_date = fields.Date(string="Date de début")
	end_date = fields.Date(string="Date de fin")
	duration = fields.Integer(string="Durée en jours", compute="_compute_duration", store=True)
	instructor_id = fields.Many2one('res.partner', string="Formateur", domain=[('is_instructor', '=', True)])
	attendee_ids = fields.Many2many('res.partner', string="Participants")
	max_attendees = fields.Integer(string="Nombre maximum de particpants autorisés")

	@api.depends('start_date','end_date')
	def _compute_duration(self):
		""" Compute duration from start date and end date"""
		for record in self:
			if (record.start_date and record.end_date) and record.end_date >= record.start_date:
				record.duration = (record.end_date - record.start_date).days + 1

	@api.onchange('start_date','end_date')
	def _start_date_must_not_posterior_end_date(self):
		""" start date must not be later than the end date 
			If start date is later than the end date we put end_date = start_date
		"""
		if (self.start_date and self.end_date) and self.start_date > self.end_date:
			self.end_date = self.start_date

	@api.onchange('max_attendees','attendee_ids')
	def _check_max_attendees(self):
		""" max_attendeees must not be negative and 
			the number of attendees must not be greater than max_attendees"""
		if self.max_attendees < 0:
			raise UserError(_("Nombre maximum de particpants autorisés doit etre positif "))
		if self.max_attendees < len(self.attendee_ids):
			raise UserError(_("Le nombre de particpants selectionnés ne doit pas dépasser %s " % str(self.max_attendees)))

	
	@api.constrains('instructor_id','attendee_ids')
	def _check_instructor_not_in_attendees(self):
		""" In a session a instructor can't be a attendee"""
		for record in self:
			if record.instructor_id and record.instructor_id in record.attendee_ids:
				raise ValidationError("Dans une session on ne peut pas etre formateur et partcipant")


class ResPartner(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	is_instructor = fields.Boolean(string="Est un formateur", default=False)
	#session_ids = fields.Many2many('training.session',string="Sessions")


