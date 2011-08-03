
# -*- coding: utf-8; mode: python -*-
#
# Cherokee-admin
#
# Authors:
#      Alvaro Lopez Ortega <alvaro@alobbs.com>
#
# Copyright (C) 2001-2011 Alvaro Lopez Ortega
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public
# License as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

import os
import re
import CTK
import vserver
import Wizard2
import Wizard2_GUI
import popen

from util import *


php_fpm = Wizard2.Load_Module ('01-Development Platforms/php-fpm.py')


class Install (Wizard2.Wizard):
    def __init__ (self, app_name, config_vserver, config_directory, tarball_url, params):
        self._app_name         = app_name
        self._config_vserver   = config_vserver
        self._config_directory = config_directory
        self._tarball_url      = tarball_url

        # Base
        Wizard2.Wizard.__init__ (self, app_name, params)

        # Sibling wizard
        self.php = self._Register_Child_Wizard (php_fpm.Install (params))

    def Check_Parameters (self):
        # PHP
        errors = self.php.Check_Parameters()

        # App location
        errors += self._Check_Params_Install_Type (
            allows_dir     = bool(self._config_directory),
            allows_vserver = bool(self._config_vserver))

        errors += self._Check_Software_Location()

        return errors

    def Check_Prerequisites (self):
        # PHP
        errors = self.php.Check_Prerequisites()
        if errors: return errors

        return []

    def Download (self):
        errors = self._Handle_Download (tarball = self._tarball_url)
        return errors or []

    def Unpack (self):
        errors = self._Handle_Unpacking ()
        return errors or []

    def Configure_Cherokee (self):
        # PHP
        errors = self.php.Configure_Cherokee()
        if errors: return errors

        # Collect substitutions
        props = cfg_get_surrounding_repls ('pre_rule', self.php.rule)
        props.update (self.__dict__)

        # Wordpress
        if self.type == 'directory':
            # Apply the configuration
            config = self._config_directory %(props)
            CTK.cfg.apply_chunk (config)

        elif self.type == 'vserver':
            # Apply the configuration
            config = self._config_vserver %(props)
            CTK.cfg.apply_chunk (config)

            # Static files
            vserver.Add_Usual_Static_Files (props['pre_rule_plus1'])

            # Normalize rules
            CTK.cfg.normalize ('vserver!%s!rule'%(self.vserver_num))

        return []


    #
    # Modules
    #

    def _get_PHP_modules (self):
        # PHP binary
        php_path = php_fpm._find_binary()
        if not php_path:
            return []

        # Execute php -m
        ret = popen.popen_sync ('%s -m' %(php_path))

        # Parse output
        modules = re.findall('(^[a-zA-Z0-9].*$)', ret['stdout'], re.MULTILINE)
        return modules

    def _check_PHP_modules (self, modules):
        # Preformat
        if type(modules) == list:
            mods = modules
        else:
            mods = [modules]

        # List of PHP modules
        available_modules = self._get_PHP_modules()
        if not available_modules:
            return False

        # Cross the list
        result = {}
        for m in mods:
            result[m] = m in available_modules

        return result

    def _Prerequisite__check_PHP_modules (self, modules):
        errors  = []
        results = self._check_PHP_modules (modules)

        for module in results:
            if not results[module]:
                errors += ["The PHP module '%(name)s' was not found" %({'name': module})]

        return errors

    def _Prerequisite__MySQL (self, check_mysql=True, check_mysqli=True):
        # Check the modules
        if check_mysql:
            error_mysql = self._Prerequisite__check_PHP_modules ('mysql')
        if check_mysqli:
            error_mysqli = self._Prerequisite__check_PHP_modules ('mysqli')

        # Interpret the return values
        if check_mysql and check_mysqli and error_mysql and error_mysqli:
            return [_("Wordpress requieres PHP to have either the 'mysql' or 'mysqli' modules")]

        if check_mysqli and not check_mysql and error_mysqli:
            return error_mysqli

        if check_mysql and not check_mysqli and error_mysql:
            return error_mysql

        return []
