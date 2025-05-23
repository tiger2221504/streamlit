import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials
import altair as alt
import smtplib, ssl
from email.mime.text import MIMEText

# 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = [
   'https://www.googleapis.com/auth/spreadsheets',
   'https://www.googleapis.com/auth/drive'
   ]
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定。
try:
   credentials = Credentials.from_service_account_file("./Streamlit/streamlit-kizai-reserve-dab82b36d3cf.json", scopes=scope)
except Exception as e:
   credentials = Credentials.from_service_account_file("./Streamlit/pythongs-405212-dee426556119.json", scopes=scope)
#OAuth2の資格情報を使用してGoogle APIにログイン。
gc = gspread.authorize(credentials)
#スプレッドシートIDを変数に格納する。
SPREADSHEET_KEY = '185-FzmoOI0BGbG9nKzHq5JXjLHRs-dfKkOa7MzaOxow'

# スプレッドシート（ブック）を開く
workbook = gc.open_by_key(SPREADSHEET_KEY)
# シートを開く
worksheet = workbook.worksheet('sheet1')

#機材リスト
kizai_sheet = workbook.worksheet('list')
kizai_df = pd.DataFrame(kizai_sheet.get_all_records())
kizai_list = kizai_df["機材名"].tolist()
if "その他(備考に記載)" not in kizai_list:
   kizai_list.append("その他(備考に記載)")

# タグ(カテゴリ)リスト
tag_sheet = workbook.worksheet('tag')
tag_df = pd.DataFrame(tag_sheet.get_all_records())
tag_list = sorted(tag_df["タグ一覧"].dropna().unique().tolist())
if "その他(備考に記載)" not in tag_list:
   tag_list.append("その他(備考に記載)")


def write_worksheet(kizai,name,start,end,purpose,remarks):
  #最終行の取得
  list_of_lists = worksheet.get_all_values()
  line = len(list_of_lists)

  # セルに文字列を代入する。
  worksheet.update_cell(line+1,1,kizai)
  worksheet.update_cell(line+1,2,name)
  worksheet.update_cell(line+1,3,start)
  worksheet.update_cell(line+1,4,end)
  worksheet.update_cell(line+1,5,purpose)
  worksheet.update_cell(line+1,6,remarks)


def del_worksheet(line):
  #worksheet.delete_rows(line)
  worksheet.update_cell(line,4,"")

def MakeDf(worksheet):
  df = pd.DataFrame(worksheet.get_all_records())
  return df


def reserve_bool(df,kizai,name,start,end):
   if kizai=="その他(備考に記載)":
      return False
   for i in range(len(df)):
    if df.iat[i,0]==kizai:
      if df.iat[i,1]==name:
        if df.iat[i,2]==start:
          if df.iat[i,3]==end:
            return True
    continue
      
   return False


def date_bool(df,start,end):
   if kizai=="その他(備考に記載)":
      return False
   for i in range(len(df)):
      if df.iat[i,0]==kizai:
         if (pd.to_datetime(df.iat[i,2])<=pd.to_datetime(start)) & (pd.to_datetime(df.iat[i,3])>=pd.to_datetime(start)):
           return True
         if (pd.to_datetime(df.iat[i,2])<=pd.to_datetime(end)) & (pd.to_datetime(df.iat[i,3])>=pd.to_datetime(end)):
           return True
         if (pd.to_datetime(df.iat[i,2])>=pd.to_datetime(start)) & (pd.to_datetime(df.iat[i,3])<=pd.to_datetime(end)):
           return True
      continue
          
   return False


#メールを送信する関数
#新規予約メール
def send_new_email(kizai,name,start,end,purpose,remarks):
  msg = make_mime_text(
    mail_to = st.secrets["send_address"],
    subject = "🔔【新規予約】"+kizai,
    body = "🔔予約完了通知<br><br>●機材名："+kizai+"<br>●名前："+name+"<br>●使用開始日："+start+"<br>●返却予定日："+end+"<br>●使用目的："+purpose+"<br>●備考："+remarks+"<br><br>予約が追加されました。<br>確認👇👇<br>https://docs.google.com/spreadsheets/d/185-FzmoOI0BGbG9nKzHq5JXjLHRs-dfKkOa7MzaOxow/edit?usp=sharing"
  )
  send_gmail(msg)

#予約削除メール
def send_del_email(kizai,name,start,end,purpose):
  msg = make_mime_text(
    mail_to = st.secrets["send_address"],
    subject = "🔔【予約削除】"+kizai,
    body = "🔔予約削除通知<br><br>●機材名："+kizai+"<br>●名前："+name+"<br>●使用開始日："+start+"<br>●返却予定日："+end+"<br>●使用目的："+purpose+"<br><br>予約が削除されました。<br>確認👇👇<br>https://docs.google.com/spreadsheets/d/185-FzmoOI0BGbG9nKzHq5JXjLHRs-dfKkOa7MzaOxow/edit?usp=sharing"
  )
  send_gmail(msg)

# 件名・送信先アドレス・本文を渡す関数
def make_mime_text(mail_to, subject, body):
  msg = MIMEText(body, "html")
  msg["Subject"] = subject
  msg["To"] = mail_to
  msg["From"] = st.secrets["account"]
  return msg

# smtp経由でメール送信する関数
def send_gmail(msg):
  server = smtplib.SMTP_SSL(
    "smtp.gmail.com", 465,
    context = ssl.create_default_context())
  server.set_debuglevel(0)
  server.login(st.secrets["account"], st.secrets["password"])
  server.send_message(msg)


#ページコンフィグ
st.set_page_config(
     page_title="機材予約システム",
     page_icon="📹",
     initial_sidebar_state="collapsed",
     menu_items={
         'Get help': "https://drive.google.com/file/d/1_opa9G1174gYz0dc0H3JVpJIUTaqvWZQ/view?usp=sharing",
         'About': """
         # GHK機材予約システム
         機材を予約できます。機材の管理については技術課まで。
         @ 2024 GHK
         """
     }
 )


#★★メンテナンス時にコメントアウトを外す★★
#st.title("**:red[メンテナンス中]**")


st.title('GHK 機材予約システム')

howtouse = '<a href="https://drive.google.com/file/d/1_opa9G1174gYz0dc0H3JVpJIUTaqvWZQ/view?usp=sharing" target="_blank">使い方</a>'
st.markdown(howtouse, unsafe_allow_html=True)
st.write("")

st.write('''## ●新規予約''')
with st.form("reserve_form", clear_on_submit=False):
    kizai = st.selectbox('*使用機材',kizai_list)
    name = st.text_input('*使用者名')
    start = st.date_input('*使用開始日:', datetime.datetime.today(),min_value=datetime.datetime.today())
    end = st.date_input('*返却予定日:', datetime.datetime.today(),min_value=datetime.datetime.today())
    purpose = st.text_input('*使用目的')
    remarks = st.text_input('備考')
    submitted1 = st.form_submit_button("予約追加")

    if 'reserve_form' in st.session_state:
        submitted=True

    if submitted1:
      df = MakeDf(worksheet)
      if start > end :
        st.markdown("**:red[エラー]**")
        st.markdown(":red[(返却予定日は使用開始日より前に設定できません。)]")
      elif name == "" or purpose == "" :
        st.markdown("**:red[エラー]**")
        st.markdown(":red[(入力されていない必須項目があります。)]")
      elif reserve_bool(df,kizai,name,str(start),str(end)):
        st.markdown("**:red[エラー]**")
        st.markdown(":red[重複した予約が既に存在します。]")
        st.markdown(":red[編集したい場合は一度削除してください。]")
      elif date_bool(df,start,end):
        st.markdown("**:red[エラー]**")
        st.markdown(":red[同じ機材で日付の重なった予約が既に存在します。]")
      else:
        if remarks=="":
           remarks="-"
        #スプレッドシートに追加する
        write_worksheet(kizai,name,str(start),str(end),purpose,remarks)
        
        #詳細のプリント
        st.markdown("**:red[予約完了]**")
        st.write('機材名：',kizai)
        st.write('名前：',name)
        st.write('使用開始日：',start)
        st.write('返却予定日：',end)
        st.write('使用目的：',purpose)

        #通知メール送信
        send_new_email(kizai,name,str(start),str(end),purpose,remarks)
        print("メール送信完了")

# exp = st.expander("🌟Tips", expanded=False)
# glink = '<a href="https://docs.google.com/spreadsheets/d/185-FzmoOI0BGbG9nKzHq5JXjLHRs-dfKkOa7MzaOxow/edit?gid=1580396357#gid=1580396357" target="_blank">Googleスプレッドシート</a>'
# exp.markdown(glink, unsafe_allow_html=True)
# exp.write("機材リストの編集はこちらから。")

glink = '<a href="https://docs.google.com/spreadsheets/d/185-FzmoOI0BGbG9nKzHq5JXjLHRs-dfKkOa7MzaOxow/edit?gid=1580396357#gid=1580396357" target="_blank">Googleスプレッドシート</a>'
st.markdown(glink, unsafe_allow_html=True)
st.write("機材リストの編集はこちらから。")

st.write('''##''')

st.write('''## ●予約リスト''')
select_tags = st.multiselect("■カテゴリで絞り込み", options=tag_list, default=tag_list,placeholder="閲覧するカテゴリを選んでください(複数選択)")
stock = st.radio(label='■表示順', options=('予約番号', '使用開始日', '返却予定日'), index=0, horizontal=True,)

if st.button(label='予約リストを表示(更新)'):
   viewdf = MakeDf(worksheet)
   # カテゴリに対応する機材を抽出
   tag_to_kizai = kizai_df[kizai_df["タグ"].isin(select_tags)]["機材名"].tolist()

   # ★後で消す
   st.write("🎯 選択されたタグ:", select_tags)
   st.write("🧾 タグに該当する機材:", tag_to_kizai)
   
   # 絞り込み：タグに対応する機材名かつ返却日が今日以降
   viewdf = viewdf[
      viewdf["機材名"].isin(tag_to_kizai) &
      (pd.to_datetime(viewdf["返却予定日"]) > datetime.datetime.today() + datetime.timedelta(days=-1))
   ]
   viewdf = viewdf.drop(columns={'カレンダー','予約ID'})
   
   if stock == "予約番号":
      viewdf = viewdf.sort_index()
      st.write('※予約番号順に表示されています')
   elif stock == "使用開始日":
      viewdf = viewdf.sort_values(by="使用開始日")
      st.write('※使用開始日順に表示されています')
   elif stock == "返却予定日":
      viewdf = viewdf.sort_values(by="返却予定日")
      st.write('※返却予定日順に表示されています')
      
   st.table(viewdf)

calendar = '<a href="https://calendar.google.com/calendar/embed?src=b2a380f349198cf89751d3efa30f8728b23e29de667b5cb0cad1e780f7b220b8%40group.calendar.google.com&ctz=Asia%2FTokyo" target="_blank">予約カレンダー📅</a>'
st.markdown(calendar, unsafe_allow_html=True)

st.write('''##''')

st.write('''## ●予約削除''')
with st.form("del_form", clear_on_submit=True):
  #最終行の取得
  list_of_lists = worksheet.get_all_values()
  last_line = len(list_of_lists)-2

  num = st.number_input('削除したい予約番号',help = "予約番号は予約リストの一番左の列",value=0,min_value=0,max_value=last_line)
  name = st.text_input('使用者名')
  submitted2 = st.form_submit_button("削除する", type="primary")

  if 'del_form' in st.session_state:
      submitted2=True

  if submitted2:
    df = MakeDf(worksheet)

    try:
      if last_line < num or num < 0:
        st.markdown("**:red[エラー]**")
        st.markdown(":red[(指定した予約は存在しません)]")
      elif name != df.iat[num,1]:
        st.markdown("**:red[エラー]**")
        st.markdown(":red[(予約番号と使用者名が一致しません)]")
      elif num == "":
        st.markdown("**:red[エラー]**")
        st.markdown(":red[(予約番号が入力されていません)]")
      else:
        del_num = num
        del_kizai = df.iat[num,0]
        del_name = df.iat[num,1]
        del_start = df.iat[num,2]
        del_end = df.iat[num,3]
        del_purpose = df.iat[num,4]

        del_worksheet(num+2)

        st.markdown("**:red[予約削除完了]**")
        st.write('以下の予約を削除しました。')
        st.write('・機材名：',del_kizai)
        st.write('・名前：',del_name)
        st.write('・使用開始日：',del_start)
        st.write('・返却予定日：',del_end)
        st.write('・使用目的：',del_purpose)

        #メール送信
        send_del_email(del_kizai,del_name,str(del_start),str(del_end),del_purpose)
        print("メール送信完了")

    except Exception as e:
      st.markdown("**:red[エラー]**")
      st.write(e)
