import sys
import re
from pathlib import Path
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow, QTextEdit, QFileDialog, QMessageBox, QToolBar, QLabel, QDockWidget, QWidget, QFormLayout, QLineEdit, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowIcon(QIcon('./assets/editor.png'))
        self.setGeometry(100, 100, 500, 300)

        self.title = 'Editor'
        self.filters = 'Text Files (*.txt)'

        self.set_title()

        self.path = None

        self.text_edit = QTextEdit(self)
        self.text_edit.textChanged.connect(self.text_changed)
        self.setCentralWidget(self.text_edit)

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('&File')
        edit_menu = menu_bar.addMenu('&Edit')
        view_menu = menu_bar.addMenu('&View')
        help_menu = menu_bar.addMenu('&Help')

        # new menu item
        new_action = QAction(QIcon('./assets/new.png'), '&New', self)
        new_action.setStatusTip('Create a new document')
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)

        # open menu item
        open_action = QAction(QIcon('./assets/open.png'), '&Open...', self)
        open_action.triggered.connect(self.open_document)
        open_action.setStatusTip('Open a document')
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)

        # save menu item
        save_action = QAction(QIcon('./assets/save.png'), '&Save', self)
        save_action.setStatusTip('Save the document')
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_document)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        # exit menu item
        exit_action = QAction(QIcon('./assets/exit.png'), '&Exit', self)
        exit_action.setStatusTip('Exit')
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.quit)
        file_menu.addAction(exit_action)

        # edit menu
        undo_action = QAction(QIcon('./assets/undo.png'), '&Undo', self)
        undo_action.setStatusTip('Undo')
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.text_edit.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction(QIcon('./assets/redo.png'), '&Redo', self)
        redo_action.setStatusTip('Redo')
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.text_edit.redo)
        edit_menu.addAction(redo_action)


        view_search_action = QAction(QIcon('./assets/search.png'),'Search',self)
        view_search_action.setStatusTip('Show the search dock')
        view_search_action.setShortcut('Ctrl+F')
        view_search_action.triggered.connect(self.show_search_dock)
        view_menu.addAction(view_search_action)

        about_action = QAction(QIcon('./assets/about.png'), 'About', self)
        help_menu.addAction(about_action)
        about_action.setStatusTip('About')
        about_action.setShortcut('F1')

        # toolbar
        toolbar = QToolBar('Main ToolBar')
        self.addToolBar(toolbar)
        toolbar.setIconSize(QSize(16, 16))

        toolbar.addAction(new_action)
        toolbar.addAction(save_action)
        toolbar.addAction(open_action)
        toolbar.addSeparator()

        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)
        toolbar.addSeparator()

        toolbar.addAction(exit_action)

        # status bar
        self.status_bar = self.statusBar()

        # display the a message in 5 seconds
        self.status_bar.showMessage('Ready', 5000)

        # add a permanent widget to the status bar
        self.character_count = QLabel("Length: 0")
        self.status_bar.addPermanentWidget(self.character_count)

        # dock widget
        self.dock = QDockWidget('Search')
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock)

        search_form = QWidget()
        layout = QFormLayout(search_form)
        search_form.setLayout(layout)

        self.search_term = QLineEdit(search_form)
        self.search_term.setPlaceholderText("Enter a search term")
        layout.addRow(self.search_term)

        btn_search = QPushButton('Go', clicked=self.search)
        layout.addRow(btn_search)
        self.dock.setWidget(search_form)
        self.show()

    def show_search_dock(self):
        self.dock.show()

    def search(self):
        term = self.search_term.text()
        if not term:
            return

        cur = self.text_edit.find(term)
        if not cur:
            self.status_bar.showMessage(f'The term "{term}" was not found',2000)
            
    def set_title(self, filename=None):
        title = f"{filename if filename else 'Untitled'} - {self.title}"
        self.setWindowTitle(title)

    def confirm_save(self):
        if not self.text_edit.document().isModified():
            return True

        message = f"Do you want to save changes to {self.path if self.path else 'Untitled'}?"
        MsgBoxBtn = QMessageBox.StandardButton
        MsgBoxBtn = MsgBoxBtn.Save | MsgBoxBtn.Discard | MsgBoxBtn.Cancel

        button = QMessageBox.question(
            self, self.title, message, buttons=MsgBoxBtn
        )

        if button == MsgBoxBtn.Cancel:
            return False

        if button == MsgBoxBtn.Save:
            self.save_document()

        return True

    def new_document(self):
        if self.confirm_save():
            self.text_edit.clear()
            self.set_title()

    def write_file(self):
        self.path.write_text(self.text_edit.toPlainText())
        self.statusBar().showMessage('The file has been saved...', 3000)

    def save_document(self):
        # save the currently openned file
        if (self.path):
            return self.write_file()

        # save a new file
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Save File', filter=self.filters
        )

        if not filename:
            return

        self.path = Path(filename)
        self.write_file()
        self.set_title(filename)

    def open_document(self):
        filename, _ = QFileDialog.getOpenFileName(self, filter=self.filters)
        if filename:
            self.path = Path(filename)
            self.text_edit.setText(self.path.read_text())
            self.set_title(filename)

    def quit(self):
        if self.confirm_save():
            self.destroy()

    def text_changed(self):
        text = self.text_edit.toPlainText()
        self.character_count.setText(f'Length: {len(text)}')


if __name__ == '__main__':
    try:
        # show the app icon on the taskbar
        import ctypes
        myappid = 'yourcompany.yourproduct.subproduct.version'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    finally:
        app = QApplication(sys.argv)
        window = MainWindow()
        sys.exit(app.exec())



