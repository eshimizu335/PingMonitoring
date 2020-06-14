# csvファイルの削除
import configparser as cp
import datetime as dt
import glob
import os
import PySimpleGUI as sg
import re
import schedule
import sys
import time

sg.theme('BluePurple')

config = cp.ConfigParser()
config.read('config.ini')
path = config.get('settings', 'path')


def delete_files():
    folders = glob.glob(os.path.join(path, '*'))
    delete = config.get('settings', 'delete')
    dele = '-'+delete
    for folder in folders:
        files = glob.glob(os.path.join(folder, '*'))
        for file in files:
            # ファイル名から日付を取り出して保存期間を過ぎているか判定
            name = re.split('[._]', file)
            strdate = name[-2]
            getdate = dt.datetime.strptime(strdate, '%Y%m%d')
            date = dt.datetime.date(getdate)
            if date - dt.date.today() <= dt.timedelta(dele):  # 過ぎていたら削除する
                os.remove(file)


def start_window():
    # 開始画面のレイアウト作成
    layout = [[sg.Text('ping結果ファイルの削除')],
              [sg.Text('保存期間の過ぎたping結果ファイルを、毎日決められた時刻に削除します')],
              [sg.Text('事前にファイル保存期間と削除時刻を設定してください。\n')],
              [sg.Text('現在設定されている保存期間は' + config.get('settings', 'delete') + '日、削除時刻は' + config.get('settings',
                                                                                                    'deltime') + 'です。')],
              [sg.Text('設定完了後、[実行]ボタンを押してください。')],
              [sg.Text('削除プログラムを中断するにはこのウインドウを閉じてください。')],
              [sg.Button('設定メニューへ', size=(20, 2), border_width=4)],
              [sg.Button('実行', size=(20, 2), border_width=4)],
              [sg.Button('キャンセル', size=(20, 2), border_width=4)]]

    window = sg.Window('ping監視システム', layout)

    while True:  # Event Loop
        event, values = window.read()
        if event in (None, 'キャンセル'):
            sys.exit()
        elif event == '設定メニューへ':
            import settings as st
            st.settings()
            start_window()
        elif event == '実行':
            msg1 = 'ファイル削除を実行します。'
            sg.popup(msg1)
            # 毎日一定の時刻に古いログファイルを削除する
            deltime = config.get('settings', 'deltime')
            schedule.every().day.at(deltime).do(delete_files)
            while True:
                schedule.run_pending()
                time.sleep(59)


start_window()


