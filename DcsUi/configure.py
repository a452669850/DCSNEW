from DcsUi.AccountManagement import AccountManagement


class configureWindow(AccountManagement):
    def __init__(self, lis_name, lis_win, lis_img, str):
        AccountManagement.__init__(self, lis_name, lis_win, lis_img, str)

    def changeData(self):
        win = self.right_widget.currentWidget()
        if callable(getattr(win, 'getTableValue')) or callable(getattr(win, 'full_in_list_data')):
            try:
                win.queryModel.datas = win.getTableValue()
                win.queryModel.layoutChanged.emit()
            except:
                win.queryModel.datas = win.full_in_list_data()

    def closeEvent(self, event):
        win = self.right_widget.widget(2)
        win.threading.interrupt.emit('')
        self.close()
