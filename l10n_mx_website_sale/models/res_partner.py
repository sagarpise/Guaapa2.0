# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from .. import exceptions

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_data = fields.Selection(string="Trabaja", selection=[('si', 'Si'), ('no', 'No'), ], required=False, )
    firstname = fields.Char("First name", index=True)
    lastname = fields.Char("Last name", index=True)
    lastname2 = fields.Char(
        "Second last name",
    )
    name = fields.Char(
        compute="_compute_name",
        inverse="_inverse_name_after_cleaning_whitespace",
        required=False,
        store=True,
        readonly=False,
    )

    @api.model
    def create(self, vals):
        """Add inverted names at creation if unavailable."""
        context = dict(self.env.context)
        name = vals.get("name", context.get("default_name"))

        if name is not None:
            # Calculate the splitted fields
            inverted = self._get_inverse_name(
                self._get_whitespace_cleaned_name(name),
                vals.get("is_company", self.default_get(["is_company"])["is_company"]),
            )
            for key, value in inverted.items():
                if not vals.get(key) or context.get("copy"):
                    vals[key] = value

            # Remove the combined fields
            if "name" in vals:
                del vals["name"]
            if "default_name" in context:
                del context["default_name"]

        return super(ResPartner, self.with_context(context)).create(vals)

    def copy(self, default=None):
        """Ensure partners are copied right.

        Odoo adds ``(copy)`` to the end of :attr:`~.name`, but that would get
        ignored in :meth:`~.create` because it also copies explicitly firstname
        and lastname fields.
        """
        return super(ResPartner, self.with_context(copy=True)).copy(default)

    @api.model
    def default_get(self, fields_list):
        """Invert name when getting default values."""
        result = super(ResPartner, self).default_get(fields_list)

        inverted = self._get_inverse_name(
            self._get_whitespace_cleaned_name(result.get("name", "")),
            result.get("is_company", False),
        )

        for field in list(inverted.keys()):
            if field in fields_list:
                result[field] = inverted.get(field)

        return result

    @api.model
    def _names_order_default(self):
        return "first_last"

    @api.model
    def _get_names_order(self):
        """Get names order configuration from system parameters.
        You can override this method to read configuration from language,
        country, company or other"""
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("partner_names_order", self._names_order_default())
        )

    @api.model
    def _get_computed_name(self, lastname, firstname, lastname2=None):
        """Compute the name combined with the second lastname too.

        We have 2 lastnames, so lastnames and firstname will be separated by a
        comma.
        """
        order = self._get_names_order()
        names = list()
        if order == "first_last":
            if firstname:
                names.append(firstname)
            if lastname:
                names.append(lastname)
            if lastname2:
                names.append(lastname2)
        else:
            if lastname:
                names.append(lastname)
            if lastname2:
                names.append(lastname2)
            if names and firstname and order == "last_first_comma":
                names[-1] = names[-1] + ","
            if firstname:
                names.append(firstname)
        return " ".join(names)

    @api.depends("firstname", "lastname", "lastname2")
    def _compute_name(self):
        """Write :attr:`~.name` according to splitted data."""
        for partner in self:
            partner.name = self._get_computed_name(
                partner.lastname,
                partner.firstname,
                partner.lastname2,
            )

    def _inverse_name_after_cleaning_whitespace(self):
        """Clean whitespace in :attr:`~.name` and split it.

        The splitting logic is stored separately in :meth:`~._inverse_name`, so
        submodules can extend that method and get whitespace cleaning for free.
        """
        for record in self:
            # Remove unneeded whitespace
            clean = record._get_whitespace_cleaned_name(record.name)
            record.name = clean
            record._inverse_name()

    @api.model
    def _get_whitespace_cleaned_name(self, name, comma=False):
        """Remove redundant whitespace from :param:`name`.

        Removes leading, trailing and duplicated whitespace.
        """
        try:
            name = " ".join(name.split()) if name else name
        except UnicodeDecodeError:
            # with users coming from LDAP, name can be a str encoded as utf-8
            # this happens with ActiveDirectory for instance, and in that case
            # we get a UnicodeDecodeError during the automatic ASCII -> Unicode
            # conversion that Python does for us.
            # In that case we need to manually decode the string to get a
            # proper unicode string.
            name = " ".join(name.decode("utf-8").split()) if name else name

        if comma:
            name = name.replace(" ,", ",")
            name = name.replace(", ", ",")
        return name

    @api.model
    def _get2_inverse_name(self, name, is_company=False):
        """Compute the inverted name.

        - If the partner is a company, save it in the lastname.
        - Otherwise, make a guess.

        This method can be easily overriden by other submodules.
        You can also override this method to change the order of name's
        attributes

        When this method is called, :attr:`~.name` already has unified and
        trimmed whitespace.
        """
        # Company name goes to the lastname
        if is_company or not name:
            parts = [name or False, False]
        # Guess name splitting
        else:
            order = self._get_names_order()
            # Remove redundant spaces
            name = self._get_whitespace_cleaned_name(
                name, comma=(order == "last_first_comma")
            )
            parts = name.split("," if order == "last_first_comma" else " ", 1)
            if len(parts) > 1:
                if order == "first_last":
                    parts = [" ".join(parts[1:]), parts[0]]
                else:
                    parts = [parts[0], " ".join(parts[1:])]
            else:
                while len(parts) < 2:
                    parts.append(False)
        return {"lastname": parts[0], "firstname": parts[1]}

    
    def _inverse_name(self):
        """Try to revert the effect of :meth:`._compute_name`."""
        self.ensure_one()
        parts = self._get_inverse_name(self.name, self.is_company)
        # Avoid to hit :meth:`~._check_name` with all 3 fields being ``False``
        before, after = {}, {}
        for key, value in parts.items():
            (before if value else after)[key] = value
        if any([before[k] != self[k] for k in list(before.keys())]):
            self.update(before)
        if any([after[k] != self[k] for k in list(after.keys())]):
            self.update(after)

    @api.constrains("firstname", "lastname", "lastname2")
    def _check_name(self):
        """Ensure at least one name is set."""
        try:
            for record in self:
                if all(
                    (
                        record.type == "contact" or record.is_company,
                        not (record.firstname or record.lastname),
                    )
                ):raise exceptions.EmptyNamesError(record)
        except exceptions.EmptyNamesError:
            for partner in self:
                if not partner.lastname2:
                    raise


                

    @api.model
    def _install_partner_firstname(self):
        """Save names correctly in the database.

        Before installing the module, field ``name`` contains all full names.
        When installing it, this method parses those names and saves them
        correctly into the database. This can be called later too if needed.
        """
        # Find records with empty firstname and lastname
        records = self.search([("firstname", "=", False), ("lastname", "=", False)])

        # Force calculations there
        records._inverse_name()
        _logger.info("%d partners updated installing module.", len(records))

    # Disabling SQL constraint givint a more explicit error using a Python
    # contstraint
    _sql_constraints = [("check_name", "CHECK( 1=1 )", "Contacts require a name.")]


    def _split_part(self, name_part, name_split):
        """Split a given part of a name.

        :param name_split: The parts of the name
        :type dict

        :param name_part: The part to split
        :type str
        """
        name = name_split.get(name_part, False)
        parts = name.split(" ", 1) if name else []
        if not name or len(parts) < 2:
            return False
        return parts

    

    @api.model
    def _get_inverse_name(self, name, is_company=False):
        """Compute the inverted name.

        - If the partner is a company, save it in the lastname.
        - Otherwise, make a guess.
        """
        result = {
            "firstname": False,
            "lastname": name or False,
            "lastname2": False,
        }

        # Company name goes to the lastname
        if not name or is_company:
            return result

        order = self._get_names_order()
        result.update(self._get2_inverse_name(name, is_company))

        if order in ("first_last", "last_first_comma"):
            parts = self._split_part("lastname", result)
            if parts:
                result.update({"lastname": parts[0], "lastname2": u" ".join(parts[1:])})
        else:
            parts = self._split_part("firstname", result)
            if parts:
                result.update(
                    {"firstname": parts[-1], "lastname2": u" ".join(parts[:-1])}
                )
        return result

    