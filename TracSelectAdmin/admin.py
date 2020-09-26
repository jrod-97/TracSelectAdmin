"""
TracSelectAdmin: A Trac plugin for modifying custom select fields
                   for tickets in a special admin panel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from trac.core import Component, implements, TracError
from trac.util.translation import _
from trac.admin.api import IAdminPanelProvider
from trac.web.chrome import ITemplateProvider


class CustomSelectPanel(Component):
    implements(IAdminPanelProvider, ITemplateProvider)

    def _get_custom_fields(self):
        fields = []
        config = self.config['ticket-custom']
        for name in self._get_field_names_list(config):
            field_type = config.get(name)
            if field_type == 'select':
                label = config.get(name + '.label') or name.capitalize()
                fields.append((name, label))
        return fields

    @staticmethod
    def _get_field_names_list(config):
        """Returns a list with the names of all custom fields"""
        field_names = []
        for option, value in config.options():
            if '.' not in option:
                field_names.append(option)

        return field_names

    def _get_matching_field(self, page_name):
        """
        Returns the field name that matches with the given page name (url)
        :param page_name: page name
        :return: tuple of names
        """
        for field in self._get_custom_fields():
            if field[1].replace(' ', '').lower() == page_name.lower() or field[0].replace(' ', '').lower() == page_name.lower():
                return field

    # IAdminPanelProvider methods
    def get_admin_panels(self, req):
        if req.perm.has_permission('TRAC_ADMIN'):
            for field in self._get_custom_fields():
                yield ('custom-select', 'Custom Select',
                       field[1].replace(' ', '').lower(),
                       field[1])

    def render_admin_panel(self, req, cat, page, path_info):
        field_name, field_label = self._get_matching_field(page)
        req.perm.require('TICKET_ADMIN')
        data = {'label_singular': field_label}
        optionstr = self.config.get('ticket-custom', field_name + '.options')
        placeholder = optionstr.startswith('|')
        fieldoptions = optionstr.replace(' |', '|').replace('| ', '|')
        fieldoptions = fieldoptions.split('|')
        for option in fieldoptions:
            if option == '':
                fieldoptions.remove(option)
        default = self.config.get('ticket-custom', field_name + '.value')
        if not default:
            if len(fieldoptions) > 0:
                default = fieldoptions[0]
            else:
                default = ''
        if req.method == 'POST':
            # Add enum
            if req.args.get('add') and req.args.get('name'):
                fieldoptions.append(req.args.get('name'))
            elif req.args.get('add'):
                raise TracError(_("No %s specified."))
            # Remove enums
            elif req.args.get('remove'):
                sel = req.args.get('sel')
                if not sel:
                    error_msg = 'No %s selected'
                    error_msg = error_msg % data['label_plural'].lower()
                    raise TracError(_(error_msg))
                if not isinstance(sel, list):
                    sel = [sel]
                for name in sel:
                    fieldoptions.remove(name)
            # Appy changes
            elif req.args.get('apply'):
                # Set default value
                if req.args.get('default'):
                    default = req.args.get('default')
                order = dict([(str(key[6:]),
                               str(int(req.args.get(key)))) for key
                              in req.args.keys()
                              if key.startswith('value_')])
                values = dict([(val, True) for val in order.values()])
                if len(order) != len(values):
                    raise TracError(_('Order numbers must be unique'))
                for value in order:
                    fieldoptions[int(order[value])] = value
            optionstr = '|'.join(fieldoptions)
            if req.args.get('blank_placeholder'):
                optionstr = '| ' + optionstr
                default = ''
                placeholder = True
            self.config.set('ticket-custom', field_name + '.value', default)
            self.config.set('ticket-custom', field_name + '.options', optionstr)
            self.config.save()
            req.redirect(req.href.admin(cat, page))
        self.log.debug(fieldoptions)
        data.update(dict(enums=fieldoptions,
                         default=default,
                         placeholder=placeholder,
                         view='list'))
        return 'trac_select_admin.html', data

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        return []

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]
