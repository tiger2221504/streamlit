import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials
import altair as alt
#import streamlit_calendar as st_calendar

# 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = [
   'https://www.googleapis.com/auth/spreadsheets',
   'https://www.googleapis.com/auth/drive'
   ]
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定。
credentials = Credentials.from_service_account_file("./Streamlit/pythongs-405212-dee426556119.json", scopes=scope)
#OAuth2の資格情報を使用してGoogle APIにログイン。
gc = gspread.authorize(credentials)
#スプレッドシートIDを変数に格納する。
SPREADSHEET_KEY = '1LkW6x8rBrNog_ynW7Dvs4rEGmdPGbPm9AYa7VHMG650'

# スプレッドシート（ブック）を開く
workbook = gc.open_by_key(SPREADSHEET_KEY)
# シートを開く
worksheet = workbook.worksheet('sheet1')

#機材リスト
kizai_sheet = workbook.worksheet('list')
kizai_df = pd.DataFrame(kizai_sheet.get_all_records())
kizai_list = kizai_df["機材名"].tolist()


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


def del_worksheet(num):
  worksheet.delete_rows(num)


def MakeDf(worksheet):
  df = pd.DataFrame(worksheet.get_all_records())
  return df


def reserve_bool(df,kizai,name,start,end):
  for i in range(len(df)):
    if df.iat[i,0]==kizai:
      if df.iat[i,1]==name:
        if df.iat[i,2]==start:
          if df.iat[i,3]==end:
            return True
    continue
          
  return False


def date_bool(df,start,end):
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


#ページコンフィグ
st.set_page_config(
     page_title="機材予約システム",
     page_icon="📹",
     initial_sidebar_state="collapsed",
     menu_items={
         'Get help': "https://docs.google.com/spreadsheets/d/1LkW6x8rBrNog_ynW7Dvs4rEGmdPGbPm9AYa7VHMG650/edit?usp=sharing",
         'About': "# GHK機材予約システム"
     }
 )



st.title('GHK 機材予約システムβ')

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
        #スプレッドシートに追加する
        write_worksheet(kizai,name,str(start),str(end),purpose,remarks)
        
        #詳細のプリント
        st.markdown("**:red[予約完了]**")
        st.write('機材名：',kizai)
        st.write('名前：',name)
        st.write('使用開始日：',start)
        st.write('返却予定日：',end)
        st.write('使用目的：',purpose)

exp = st.expander("🌟Tips", expanded=False)
glink = '<a href="https://docs.google.com/spreadsheets/d/1LkW6x8rBrNog_ynW7Dvs4rEGmdPGbPm9AYa7VHMG650/edit#gid=1580396357" target="_blank">Googleスプレッドシート</a>'
exp.markdown(glink, unsafe_allow_html=True)
exp.write("スプレッドシートから直接編集も可能です。")
exp.write("機材リストの編集もこちらから。")

st.write('''##''')

st.write('''## ●予約リスト''')
select_kizai = st.multiselect("■機材名で絞り込み", options=kizai_list, default=kizai_list)
stock = st.radio(label='■表示順', options=('予約番号', '使用開始日', '返却予定日'), index=0, horizontal=True,)

if st.button(label='予約リストを表示(更新)'):
  viewdf = MakeDf(worksheet)
  viewdf = viewdf[viewdf["機材名"].isin(select_kizai) & (pd.to_datetime(viewdf["返却予定日"])>datetime.datetime.today()+datetime.timedelta(days=-1))]

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
        st.write('続けて削除する場合は予約番号に注意してください。')
        st.write('(番号が更新されている可能性があります。)')
    except Exception as e:
      st.markdown("**:red[エラー]**")
      st.write(e)
