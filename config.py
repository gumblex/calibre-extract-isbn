#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2011, Grant Drake <grant.drake@gmail.com>'
__docformat__ = 'restructuredtext en'

from collections import OrderedDict
try:
    from PyQt5 import QtWidgets as QtGui
    from PyQt5.Qt import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton
except ImportError as e:
    from PyQt4 import QtGui
    from PyQt4.Qt import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton
from calibre.utils.config import JSONConfig

from calibre_plugins.extract_isbn.common_utils import KeyValueComboBox, KeyboardConfigDialog

STORE_NAME = 'Options'
KEY_VALID_ISBN13_PREFIX = 'validISBN13Prefix'
KEY_POST_TASK = 'postTask'
KEY_WORKER_THRESHOLD = 'workerThreshold'
KEY_BATCH_SIZE = 'batchSize'

SHOW_TASKS = OrderedDict([('none', 'Do not change my search'),
                        ('updated', 'Show the books that have new or updated ISBNs')])

DEFAULT_STORE_VALUES = {
    KEY_POST_TASK: 'none',
    KEY_VALID_ISBN13_PREFIX: ['977', '978', '979'],
    KEY_WORKER_THRESHOLD: 1,
    KEY_BATCH_SIZE: 100
}

# This is where all preferences for this plugin will be stored
plugin_prefs = JSONConfig('plugins/Extract ISBN')

# Set defaults
plugin_prefs.defaults[STORE_NAME] = DEFAULT_STORE_VALUES

class ConfigWidget(QWidget):

    def __init__(self, plugin_action):
        QWidget.__init__(self)
        self.plugin_action = plugin_action
        layout = QGridLayout(self)
        self.setLayout(layout)

        c = plugin_prefs[STORE_NAME]

        layout.addWidget(QLabel('When the scan completes:', self), 0, 0, 1, 2)
        post_show = c.get(KEY_POST_TASK, DEFAULT_STORE_VALUES[KEY_POST_TASK])
        self.showCombo = KeyValueComboBox(self, SHOW_TASKS, post_show)
        layout.addWidget(self.showCombo, 1, 0, 1, 2)

        layout.addWidget(QLabel('Valid prefixes for ISBN-13 (comma separated):', self), 2, 0, 1, 2)
        prefixes = c.get(KEY_VALID_ISBN13_PREFIX, DEFAULT_STORE_VALUES[KEY_VALID_ISBN13_PREFIX])
        self.isbn13_ledit = QLineEdit(','.join(prefixes), self)
        layout.addWidget(self.isbn13_ledit, 3, 0, 1, 2)

        lbl = QLabel('Selected books before running as a background job:', self)
        lbl.setToolTip('Running as a background job is slower but is the only way to avoid\n' +
                       'memory leaks and will keep the UI more responsive.')
        layout.addWidget(lbl, 4, 0, 1, 1)
        worker_threshold = c.get(KEY_WORKER_THRESHOLD, DEFAULT_STORE_VALUES[KEY_WORKER_THRESHOLD])
        self.threshold_spin = QtGui.QSpinBox(self)
        self.threshold_spin.setMinimum(0)
        self.threshold_spin.setMaximum(20)
        self.threshold_spin.setProperty('value', worker_threshold)
        layout.addWidget(self.threshold_spin, 4, 1, 1, 1)

        batch_lbl = QLabel('Batch size running as a background job:', self)
        batch_lbl.setToolTip('Books will be broken into batches to ensure that if you run\n'
                       'extract for a large group you can cancel/close calibre without\n'
                       'losing all of your results as you can cancel the pending groups.')
        layout.addWidget(batch_lbl, 5, 0, 1, 1)
        batch_size = c.get(KEY_BATCH_SIZE, DEFAULT_STORE_VALUES[KEY_BATCH_SIZE])
        self.batch_spin = QtGui.QSpinBox(self)
        self.batch_spin.setMinimum(1)
        self.batch_spin.setMaximum(10000)
        self.batch_spin.setProperty('value', batch_size)
        layout.addWidget(self.batch_spin, 5, 1, 1, 1)

        keyboard_shortcuts_button = QPushButton('Keyboard shortcuts...', self)
        keyboard_shortcuts_button.setToolTip(_(
                    'Edit the keyboard shortcuts associated with this plugin'))
        keyboard_shortcuts_button.clicked.connect(self.edit_shortcuts)
        layout.addWidget(keyboard_shortcuts_button, 6, 0, 1, 2)

    def save_settings(self):
        new_prefs = {}
        new_prefs[KEY_POST_TASK] = self.showCombo.selected_key()
        prefixes = self.isbn13_ledit.text().replace(' ','')
        new_prefs[KEY_VALID_ISBN13_PREFIX] = prefixes.split(',')
        new_prefs[KEY_WORKER_THRESHOLD] = int(self.threshold_spin.value())
        new_prefs[KEY_BATCH_SIZE] = int(self.batch_spin.value())

        plugin_prefs[STORE_NAME] = new_prefs

    def edit_shortcuts(self):
        d = KeyboardConfigDialog(self.plugin_action.gui, self.plugin_action.action_spec[0])
        if d.exec_() == d.Accepted:
            self.plugin_action.gui.keyboard.finalize()
