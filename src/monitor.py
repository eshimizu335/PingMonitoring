import configparser as cp
import csv
import datetime as dt
import glob
import os
import PySimpleGUI as sg
import re
import schedule
import smtplib
import sys
import time
from icmplib import ping, traceroute, PID

sg.theme('BluePurple')

config = cp.ConfigParser()
config.read('config.ini')
path = config.get('settings', 'path')


def run_ping():
    now = dt.datetime.now()
    y = now.strftime('%Y')
    m = now.strftime('%m')
    d = now.strftime('%d')

    # 監視対象ノードリストを取得しノードごとのフォルダを作成
    nodes = config.get('settings', 'nodes')
    with open(nodes) as n:
        row = csv.reader(n)
        header = next(row)  # header行をスキップ
        for row in csv.reader(n):
            folder = path + '/' + row[0]
            if not os.path.isdir(folder):
                os.makedirs(folder)
            file = folder + '/' + row[0] + '_' + y + m + d + '.csv'  # 日毎のcsvファイルを作成

            # pingのオプション設定取得
            pc = config.getint('ping_options', 'p_count')
            pi = config.getint('ping_options', 'p_interval')
            pt = config.getint('ping_options', 'p_timeout')

            node = ping(row[1], count=pc, interval=pi, timeout=pt, id=PID)  # ping実行
            t = dt.datetime.now().strftime('%H:%M:%S')

            # 結果の書き込み
            with open(file, 'a') as f:
                w = csv.writer(f)
                if node.is_alive:  # ping成功
                    w.writerow([t, 'OK'])
                else:  # ping失敗
                    tc = config.getint('tracert_options', 't_count')
                    ti = config.getfloat('tracert_options', 't_interval')
                    tt = config.getint('tracert_options', 't_timeout')
                    tm = config.getint('tracert_options', 't_hops')
                    tf = config.get('tracert_options', 'fast_mode')

                    hops = traceroute(row[1], count=tc, interval=ti, timeout=tt, id=PID, max_hops=tm, fast_mode=tf)
                    w.writerow([t, 'NG', hops])

                    send_mail(row[0],file)


# ping失敗通知の送付
def send_mail(node,file):
    server = config.get('mail_settings', 'm_server')
    port = config.getint('mail_settings', 'm_port')
    user = config.get('mail_settings', 'm_user')
    password = config.get('mail_settings', 'm_password')
    mailfrom = config.get('mail_settings', 'm_from')
    mailto = config.get('mail_settings', 'm_to')
    subject = config.get('mail_settings', 'subject')+node
    body = config.get('mail_settings', 'body')+'\n'+file
    message = ('From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' % (mailfrom, mailto, subject, body))

    smtp = smtplib.SMTP_SSL(server, port)
    smtp.login(user, password)
    smtp.sendmail(mailfrom, mailto, message)


def start_window():
    # 開始画面のレイアウト作成
    layout = [[sg.Text('ping監視システム')],
              [sg.Text('初めて使う場合はまず設定を行ってください。')],
              [sg.Text('設定完了後、[ping監視実行]ボタンを押してください。')],
              [sg.Text('ping監視を中断するにはこのウインドウを閉じてください。')],
              [sg.Button('設定メニューへ', size=(20, 2), border_width=4)],
              [sg.Button('ping監視実行', size=(20, 2), border_width=4)],
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
        elif event == 'ping監視実行':
            msg1 = 'ping監視を実行します。'
            sg.popup(msg1)
            schedule.every(config.getint('settings', 'interval')).minutes.do(run_ping())
            while True:
                schedule.run_pending()
                time.sleep(1)

        window.close()


def main():
    # 設定ファイルの有無を確認し、なければ作る
    if not os.path.isfile('config.ini'):
        sec1 = 'settings'
        config.add_section(sec1)
        config.set(sec1, 'path')
        config.set(sec1, 'nodes')
        config.set(sec1, 'delete')
        config.set(sec1, 'deltime')
        config.set(sec1, 'interval')

        sec2 = 'ping_options'
        config.add_section(sec2)
        config.set(sec2, 'p_count')
        config.set(sec2, 'p_hops')
        config.set(sec2, 'p_interval')
        config.set(sec2, 'p_timeout')
        config.set(sec2, 'id', 'PID')

        sec3 = 'tracert_options'
        config.add_section(sec3)
        config.set(sec3, 't_count')
        config.set(sec3, 't_hops')
        config.set(sec3, 't_interval')
        config.set(sec3, 't_timeout')
        config.set(sec3, 'id', 'PID')
        config.set(sec3, 'fast_mode', 'False')

        sec4 = 'mail_settings'
        config.add_section(sec4)
        config.set(sec4, 'm_server')
        config.set(sec4, 'm_port')
        config.set(sec4, 'm_user')
        config.set(sec4, 'm_password')
        config.set(sec4, 'm_from')
        config.set(sec4, 'm_to')
        config.set(sec4, 'subject', 'PingFailed')
        config.set(sec4, 'body', 'Could not connect to the host')

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    # ping監視実行画面立ち上げ
    start_window()


if __name__ == '__main__':
    main()
