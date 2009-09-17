#!/usr/bin/env python
import sys
import os
from itertools import islice

from PyQt4 import QtGui, QtCore
from PyQt4 import QtWebKit

import aar2html

class DictView(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.dictionary = None
        self.setWindowTitle('Aard Dictionary')

        self.word_input = QtGui.QComboBox()
        self.word_input.setEditable(True)
        self.word_input.setAutoCompletion(False)
        self.word_input.editTextChanged.connect(self.update_word_completion)
        self.word_completion = QtGui.QListWidget()

        box = QtGui.QVBoxLayout()
        box.addWidget(self.word_input)
        box.addWidget(self.word_completion)

        self.word_completion.currentItemChanged.connect(self.word_selection_changed)

        left_pane = QtGui.QWidget()
        left_pane.setLayout(box)

        splitter = QtGui.QSplitter()
        splitter.addWidget(left_pane)
        self.tabs = QtGui.QTabWidget()
        splitter.addWidget(self.tabs)
        splitter.setChildrenCollapsible(False)
        splitter.setSizes([100, 300])

        menubar = self.menuBar()
        mn_file = menubar.addMenu('&File')

        style = QtGui.QApplication.instance().style()
        fileIcon = style.standardIcon(QtGui.QStyle.SP_FileIcon)

        exit = QtGui.QAction(fileIcon, 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        exit.triggered.connect(self.close)

        mn_file.addAction(exit)

        self.setCentralWidget(splitter)
        self.resize(640, 480)

    def update_word_completion(self, word, to_select=None):
        wordstr = unicode(word).encode('utf8')
        self.word_completion.clear()
        for result in islice(self.dictionary.lookup(wordstr), 10):
            print result.title.encode('utf8')
            item = QtGui.QListWidgetItem()
            item.setText(result.title)
            item.setData(QtCore.Qt.UserRole, QtCore.QVariant(result))
            self.word_completion.addItem(item)
            if result.title == word:
                self.word_completion.setCurrentItem(item)

    def word_selection_changed(self, selected, deselected):
        self.tabs.clear()
        if selected:
            title = unicode(selected.text())
            article_read_f = selected.data(QtCore.Qt.UserRole).toPyObject()
            view = QtWebKit.QWebView()
            view.linkClicked.connect(self.link_clicked)
            html = aar2html.convert(article_read_f())
            view.setHtml(html, QtCore.QUrl(title))
            view.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
            s = view.settings()
            s.setUserStyleSheetUrl(QtCore.QUrl(os.path.abspath('aar.css')))
            self.tabs.addTab(view, title)
            print self.word_input.currentIndex()
            self.word_input.addItem(title)

    def link_clicked(self, url):
        title = str(url.toString())
        self.word_completion.currentItemChanged.disconnect(self.word_selection_changed)
        self.word_input.setEditText(title)
        self.word_completion.currentItemChanged.connect(self.word_selection_changed)
        self.update_word_completion(title, title)

def main():
    app = QtGui.QApplication(sys.argv)
    dv = DictView()

    from optparse import OptionParser
    optparser = OptionParser()
    opts, args = optparser.parse_args()
    from aarddict.dictionary import Dictionary
    d = Dictionary(args[0])
    dv.dictionary = d
    dv.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

