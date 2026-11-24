# -*- coding: utf-8 -*-
from odoo import models, fields, api
import hashlib
from .ldap_service import add_user_to_ldap, update_user_in_ldap, delete_user_from_ldap, get_ldap_users
import logging

_logger = logging.getLogger(__name__)


class User(models.Model):
    _name = 'modulakuntingcustom.user'
    _table = 'modulakuntingcustom_user'#tamabahan
    _description = 'User'

    name = fields.Char(string='Name')
    username = fields.Char(string='Username')
    email = fields.Char(string='Email address', required=True, email=True)
    password = fields.Char(string='Password', invisible=True)
    card = fields.Char(string='Card ID')
    access_rights = fields.Selection([
        ('10mbps', '10Mbps'),
        ('15mbps', '15Mbps'),
        ('20mbps', '20Mbps'),
    ], string='Access rights', default='10mbps')
    employee_number = fields.Char(string='Employee Number')  # Menambahkan field ini

    # Enkripsi password
    @api.model
    def create(self, vals):
        if vals.get('password'):
            vals['password'] = hashlib.sha256(
                vals['password'].encode('utf-8')).hexdigest()[:20]
        record = super(User, self).create(vals)

        # Tambahkan user ke LDAP setelah dibuat di Odoo
        try:
            add_user_to_ldap(record)
        except Exception as e:
            _logger.error(f"Error adding user to LDAP: {e}")
            raise

        return record

    def write(self, vals):
        if vals.get('password'):
            vals['password'] = hashlib.sha256(
                vals['password'].encode('utf-8')).hexdigest()[:20]

        result = super(User, self).write(vals)

        # Update user di LDAP setelah data diperbarui di Odoo
        for record in self:
            try:
                update_user_in_ldap(record)
            except Exception as e:
                _logger.error(f"Error updating user in LDAP: {e}")
                raise

        return result

    def unlink(self):
        # Delete user from LDAP before deleting from Odoo
        for record in self:
            try:
                delete_user_from_ldap(record)
            except Exception as e:
                _logger.error(f"Error deleting user from LDAP: {e}")
                raise
        # Proceed with deletion in Odoo
        return super(User, self).unlink()

    # Fetch LDAP users
    @api.model
    def fetch_ldap_users(self, *args, **kwargs):
        try:
            ldap_users = get_ldap_users()
            for ldap_user in ldap_users:
                email = ldap_user.mail.value if hasattr(
                    ldap_user, 'mail') else None
                if email:
                    self.create({
                        'name': ldap_user.cn.value,
                        'username': ldap_user.uid.value,
                        'email': email,
                        'card': ldap_user.card.value if hasattr(ldap_user, 'card') else '',
                        'access_rights': ldap_user.accessRights.value if hasattr(ldap_user, 'accessRights') else '10mbps',
                        'employee_number': ldap_user.employeeNumber.value if hasattr(ldap_user, 'employeeNumber') else '',  # Ambil employee number
                    })
                else:
                    _logger.warning(
                        f"LDAP user {ldap_user.uid.value} has no email address and will be skipped.")
        except Exception as e:
            _logger.error(f"Error fetching LDAP users: {e}")
            raise