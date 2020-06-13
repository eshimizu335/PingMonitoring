import PySimpleGUI as sg
import configparser as cp

sg.theme('LightBlue2')


def textlabel(text): return sg.Text(text + ':', justification='r', size=(15, 1))


def settings():
    # [設定変更]画面用フレーム作成
    # 設定ファイル読み込み
    config = cp.ConfigParser()
    config.read('config.ini')
    frame1 = sg.Frame('基本設定', [[textlabel('ログ保存場所'), sg.Input(config.get('settings', 'path'), key='path'),
                                sg.FolderBrowse()],
                               [textlabel('監視対象リスト'), sg.Input(config.get('settings', 'nodes'), key='nodes'),
                                sg.FileBrowse()],
                               [textlabel('ログ保存期間(日)'), sg.Input(config.get('settings', 'delete'), key='delete')],
                               [textlabel('ログ削除時刻(hh:mm)'), sg.Input(config.get('settings', 'deltime'), key='deltime')],
                               [textlabel('ping実行間隔(分)'),
                                sg.Input(config.get('settings', 'interval'), key='interval')]],
                      relief=sg.RELIEF_SUNKEN, tooltip='基本設定')

    frame2 = sg.Frame('ping設定',
                      [[textlabel('パケット送付回数'), sg.Input(config.get('ping_options', 'p_count'), key='p_count')],
                       [textlabel('ホップ数'), sg.Input(config.get('ping_options', 'p_hops'), key='p_hops')],
                       [textlabel('パケット送付間隔'),
                        sg.Input(config.get('ping_options', 'p_interval'), key='p_interval')],
                       [textlabel('生存時間'), sg.Input(config.get('ping_options', 'p_timeout'), key='p_timeout')]],
                      relief=sg.RELIEF_SUNKEN, tooltip='ping設定')

    frame3 = sg.Frame('tracert設定',
                      [[textlabel('パケット送付回数'), sg.Input(config.get('tracert_options', 't_count'), key='t_count')],
                       [textlabel('最大ホップ数'), sg.Input(config.get('tracert_options', 't_hops'), key='t_hops')],
                       [textlabel('パケット送付間隔'), sg.Input(config.get('tracert_options', 't_interval'), key='t_interval')],
                       [textlabel('生存時間'), sg.Input(config.get('tracert_options', 't_timeout'), key='t_timeout')]],
                      relief=sg.RELIEF_SUNKEN, tooltip='tracert設定')

    frame4 = sg.Frame('メール設定',
                      [[textlabel('メールサーバ'), sg.Input(config.get('mail_settings', 'm_server'), key='m_server')],
                       [textlabel('ポート番号'), sg.Input(config.get('mail_settings', 'm_port'), key='m_port')],
                       [textlabel('ユーザ名'), sg.Input(config.get('mail_settings', 'm_user'), key='m_user')],
                       [textlabel('パスワード'),
                        sg.Input(config.get('mail_settings', 'm_password'), password_char='*', key='m_password')],
                       [textlabel('送信元アドレス'), sg.Input(config.get('mail_settings', 'm_from'), key='m_from')],
                       [textlabel('宛先アドレス'), sg.Input(config.get('mail_settings', 'm_to'), key='m_to')]],
                      relief=sg.RELIEF_SUNKEN, tooltip='メール設定')

    # frame1~4を入れ子にしたレイアウトの作成
    change_settings = [[sg.Text('基本設定', size=(15, 1)), frame1],
                       [sg.Text('ping設定', size=(15, 1)), frame2],
                       [sg.Text('tracert設定', size=(15, 1)), frame3],
                       [sg.Text('メール設定', size=(15, 1)), frame4]]

    # タブ作成
    t1 = sg.Tab('使用方法', layout=[[sg.Text('本システムは、ネットワーク障害を速やかに検知することを目的として、登録された端末のping監視を行います。')],
                                [sg.Text('対象端末に対して任意の間隔でpingを実行し、応答がなかった場合はtracertを実行します。')],
                                [sg.Text('また、ping応答の有無やtracertの結果を日毎のcsvファイルに出力します。')],
                                [sg.Text('[設定]タブよりping実行間隔やpingに失敗した場合の通知先メールアドレスを設定してください。')],
                                [sg.Text('ping監視の対象端末リストは別途「nodes.csv」ファイルで作成し、[設定]>[基本設定]の監視対象リスト欄にファイルパスを入力してください。')],
                                [sg.Text('ping監視を開始するには、monitor.pyを実行してください。')]])
    t2 = sg.Tab('設定', layout=[[sg.Text('現在の設定内容は以下の通りです。空欄部分はまだ設定されていません。')],
                              [sg.Text('設定変更する場合は、項目入力後に必ず左下[保存]ボタンを押してください')],
                              [sg.Column(change_settings, scrollable=True, size=(800, 350))],
                              [sg.Button('保存'), sg.Button('キャンセル')]])

    # 全体レイアウト作成
    l1 = [[sg.TabGroup([[t1, t2]], tab_background_color='#ccc', selected_title_color='#ff0',
                       selected_background_color='#000', tab_location='topleft')]]

    # ウインドウ作成
    window = sg.Window('ping監視', l1, resizable=True, size=(900, 500))

    # イベントループ
    while True:
        event, values = window.read()  # イベント読み取り
        if event == None or event == 'キャンセル':  # 終了条件）
            break
        elif event == '保存':
            # 設定ファイルに書き込み
            config = cp.ConfigParser()

            sec1 = 'settings'
            config.add_section(sec1)
            config.set(sec1, 'path', values['path'])
            config.set(sec1, 'nodes', values['nodes'])
            config.set(sec1, 'delete', '-' + values['delete'])
            config.set(sec1, 'deltime', values['deltime'])
            config.set(sec1, 'interval', values['interval'])

            sec2 = 'ping_options'
            config.add_section(sec2)
            config.set(sec2, 'p_count', values['p_count'])
            config.set(sec2, 'p_hops', values['p_hops'])
            config.set(sec2, 'p_interval', values['p_interval'])
            config.set(sec2, 'p_timeout', values['p_timeout'])
            config.set(sec2, 'id', 'PID')

            sec3 = 'tracert_options'
            config.add_section(sec3)
            config.set(sec3, 't_count', values['t_count'])
            config.set(sec3, 't_hops', values['t_hops'])
            config.set(sec3, 't_interval', values['t_interval'])
            config.set(sec3, 't_timeout', values['t_timeout'])
            config.set(sec3, 'id', 'PID')
            config.set(sec3, 'fast_mode', 'False')

            sec4 = 'mail_settings'
            config.add_section(sec4)
            config.set(sec4, 'm_server', values['m_server'])
            config.set(sec4, 'm_port', values['m_port'])
            config.set(sec4, 'm_user', values['m_user'])
            config.set(sec4, 'm_password', values['m_password'])
            config.set(sec4, 'm_from', values['m_from'])
            config.set(sec4, 'm_to', values['m_to'])
            config.set(sec4, 'subject', 'PingFailed')
            config.set(sec4, 'body', 'Could not connect to the host')

            with open('config.ini', 'w') as configfile:
                config.write(configfile)

            # 保存完了メッセージ
            msg = '設定を保存しました。'
            sg.popup(msg)

    # 終了処理
    window.close()


settings()
