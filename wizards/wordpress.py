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

import CTK
import vserver
import Wizard2
import Wizard2_GUI as GUI

from util import *

php_tpl = Wizard2.Load_Template ('PHP.py')

#
# Configuration
#

CONFIG_VSERVER = """
vserver!%(vserver_num)s!nick = %(vserver_nick)s
vserver!%(vserver_num)s!document_root = %(app_dir)s
vserver!%(vserver_num)s!directory_index = index.php,index.html

# The PHP rule comes here

%(pre_rule_minus2)s!match = fullpath
%(pre_rule_minus2)s!match!fullpath!1 = /wp-admin
%(pre_rule_minus2)s!handler = redir
%(pre_rule_minus2)s!handler!rewrite!1!show = 0
%(pre_rule_minus2)s!handler!rewrite!1!substring = /wp-admin/

%(pre_rule_minus3)s!match = exists
%(pre_rule_minus3)s!match!iocache = 1
%(pre_rule_minus3)s!match!match_any = 1
%(pre_rule_minus3)s!match!match_only_files = 1
%(pre_rule_minus3)s!handler = common
%(pre_rule_minus3)s!handler!iocache = 1
%(pre_rule_minus3)s!handler = common
%(pre_rule_minus3)s!handler!allow_dirlist = 0

vserver!%(vserver_num)s!rule!1!match = default
vserver!%(vserver_num)s!rule!1!handler = redir
vserver!%(vserver_num)s!rule!1!handler!rewrite!1!show = 0
vserver!%(vserver_num)s!rule!1!handler!rewrite!1!regex = /?(.*)
vserver!%(vserver_num)s!rule!1!handler!rewrite!1!substring = /index.php?/$1
"""

CONFIG_DIR = """
%(pre_rule_plus1)s!match = directory
%(pre_rule_plus1)s!match!directory = %(web_directory)s
%(pre_rule_plus1)s!match!final = 0
%(pre_rule_plus1)s!document_root = %(app_dir)s

# The PHP rule comes here

%(pre_rule_minus1)s!match = fullpath
%(pre_rule_minus1)s!match!fullpath!1 = %(web_directory)s/wp-admin
%(pre_rule_minus1)s!handler = redir
%(pre_rule_minus1)s!handler!rewrite!10!show = 0
%(pre_rule_minus1)s!handler!rewrite!10!substring = %(web_directory)s/wp-admin/

%(pre_rule_minus3)s!match = and
%(pre_rule_minus3)s!match!final = 1
%(pre_rule_minus3)s!match!left = directory
%(pre_rule_minus3)s!match!left!directory = %(web_directory)s
%(pre_rule_minus3)s!match!right = exists
%(pre_rule_minus3)s!match!right!iocache = 1
%(pre_rule_minus3)s!match!right!match_any = 1
%(pre_rule_minus3)s!match!right!match_index_files = 1
%(pre_rule_minus3)s!match!right!match_only_files = 1
%(pre_rule_minus3)s!handler = common
%(pre_rule_minus3)s!handler!allow_dirlist = 0
%(pre_rule_minus3)s!handler!allow_pathinfo = 0
%(pre_rule_minus3)s!handler!iocache = 1

%(pre_rule_minus4)s!match = request
%(pre_rule_minus4)s!match!request = %(web_directory)s/?(.*)
%(pre_rule_minus4)s!handler = redir
%(pre_rule_minus4)s!handler!rewrite!1!show = 0
%(pre_rule_minus4)s!handler!rewrite!1!substring = %(web_directory)s/index.php?/$1
"""

#
# Public info
#
TARBALL = "http://wordpress.org/latest.tar.gz"

DESC_SHORT = """WordPress is a state-of-the-art, semantic, personal
publishing platform with a focus on aesthetics, Web standards, and
usability. It was born out of a desire for an elegant,
well-architected personal publishing system.
"""

software = {
 'id':             'wordpress',
 'name':           'WordPress',
 'author':         'Wordpress Community',
 'URL':            'http://wordpress.org/',
 'icon_small':     'wordpress_x96.png',
 'category':       'Content Management',
 'packager_name':  'Alvaro Lopez Ortega',
 'packager_email': 'alvaro@alobbs.com',
 'desc_short':     DESC_SHORT,
}

#
# Installer
#
class Install (php_tpl.Install):
    def __init__ (self, params):
        php_tpl.Install.__init__ (self,
                                  app_info         = software,
                                  config_vserver   = CONFIG_VSERVER,
                                  config_directory = CONFIG_DIR,
                                  default_download = lambda: TARBALL,
                                  params           = params)

    def Check_Prerequisites (self):
        errors = php_tpl.Install.Check_Prerequisites (self)
        if errors: return errors

        return self._Prerequisite__MySQL()

    def _Handle_Unpacking (self):
        errors = php_tpl.Install._Handle_Unpacking (self)
        if errors: return errors

        # Update app_dir, WP is in a subdir
        self._Update_app_dir ("wordpress.*")

    def Check_PostUnpack (self):
        return self._Check_File_Exists ('wp-comments-post.php')

    def Configure_Cherokee_PostApply (self):
        if self.type == 'vserver':
            vserver.Add_Usual_Static_Files (self.cfg_replacements['pre_rule_plus1'])

#
# GUI
#
GUI.Register_Standard_GUI (software, Install, lambda: TARBALL)
