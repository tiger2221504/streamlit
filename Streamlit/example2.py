#ライブラリの取り込み
import tkinter as tk
import youtube_dl

def button_clicked():
    #ここからYouTubeDL処理
    url = text.get()
    path = "complete/"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl':  path + "%(title)s" + '.mp3',
        'postprocessors': [
            {'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
             'preferredquality': '192'},
            {'key': 'FFmpegMetadata'},
        ],
    }
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    info_dict = ydl.extract_info(
    url, 
    download=True)


#ウィンドウの作成
win = tk.Tk()
win.title("YouTubeをmp3に変換") #タイトル
win.geometry("400x110") #サイズ



##部品作成
#ラベル
labelurl = tk.Label(win, text='URLを入力',font=("bold"))
labelurl.pack()

#テキストボックス
text = tk.Entry(win, width=60)
text.pack()

#OKボタン
okButton = tk.Button(win, text='OK')
okButton["command"] = button_clicked
okButton.pack()

labeltext1 = tk.Label(win, text=u'※OKボタンを押すと応答なしになるけど気にしないで待っててね★')
labeltext1.pack()

labeltext2 = tk.Label(win, text=u'出力したファイルはcompleteフォルダに入ってるよ！')
labeltext2.pack()

#ウィンドウを動かす
win.mainloop()


