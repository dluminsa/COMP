import pandas as pd 
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import traceback
import streamlit as st
import time
import numpy as np
#sdd
import gspread
import datetime as dt
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(
    'COMPETENCE YARD TRACKER'
)

try:
   conn = st.connection('gsheets', type=GSheetsConnection)
   exist = conn.read(worksheet= 'CONTRIBUTIONS', usecols=list(range(4)),ttl=5)
   dfpay = exist.dropna(how='all')
except:
   st.write("POOR NETWORK, COULDN'T CONNECT TO DATABASE")
   st.write('REFRESH PAGE TO START AGAIN')
   st.stop()
try:
   conn = st.connection('gsheets', type=GSheetsConnection)
   exista = conn.read(worksheet= 'EXPENSES', usecols=list(range(4)),ttl=5)
   dfpaye = exista.dropna(how='all')
except:
   st.write("POOR NETWORK, COULDN'T CONNECT TO DATABASE")
   st.write('REFRESH PAGE TO START AGAIN')
   st.stop()


file = r"MEMBERS.csv"
df = pd.read_csv(file)
dfm = df[df['MEMBER']!='ADMIN'].copy()
df = df[df['MEMBER']=='ADMIN'].copy()
members =dfm['MEMBER'].unique()


# Initialize session states
if 'passw' not in st.session_state:
    st.session_state.passw = ''
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

passwords = df['PASSWORD'].unique()

# Login form
if not st.session_state.logged_in:
    with st.form("login_form"):
        password_input = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Login")

    # Validate login on form submission
    if submit_button:
        try:
            input_password = int(password_input)
            if input_password in passwords:
                st.session_state.logged_in = True
                st.session_state.passw = input_password
                st.success("Login successful!")
                st.rerun()  # Refresh the app to remove the form after login
            else:
                st.error("Password not found")
        except ValueError:
            st.error("Please enter a valid numeric password")
else:
    # Post-login functionality
    df["PASSWORD"] = df["PASSWORD"].astype(int)
    user_df = df[df["PASSWORD"] == st.session_state.passw].copy()

    if not user_df.empty:
        st.success(f"WELCOME, ADMIN")
    else:
        st.error("Unable to retrieve your information. Please log in again.")
        st.session_state.logged_in = False
        st.rerun()
time.sleep(1)
if st.session_state.logged_in:
        # Prepare the credentials dictionary
    credentials_info = {
            "type": secrets["type"],
            "project_id": secrets["project_id"],
            "private_key_id": secrets["private_key_id"],
            "private_key": secrets["private_key"],
            "client_email": secrets["client_email"],
            "client_id": secrets["client_id"],
            "auth_uri": secrets["auth_uri"],
            "token_uri": secrets["token_uri"],
            "auth_provider_x509_cert_url": secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": secrets["client_x509_cert_url"]
        }
            
    try:
        # Define the scopes needed for your application
        scopes = ["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
        
         
        credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
            
            # Authorize and access Google Sheets
        client = gspread.authorize(credentials)
            
            # Open the Google Sheet by URL
        spreadsheetu = "https://docs.google.com/spreadsheets/d/1IgIltX9_2yvppb4YYoebRyyYwCqYZng62h0cRYPmAdE"    
        spreadsheet = client.open_by_url(spreadsheetu)
    except Exception as e:
            # Log the error message
        st.write(f"CHECK: {e}")
        st.write(traceback.format_exc())
        st.write("COULDN'T CONNECT TO GOOGLE SHEET, TRY AGAIN")
        st.stop()


if st.session_state.logged_in:
    st.write('DOWNLOADS')
    cola, colb = st.columns(2)
    with cola:
        dat = dfpay.copy()
        dat = dat.rename(columns = {'MONTH': 'DATE'})
        csv_data = dat.to_csv(index=False)
        tot = dat.shape[0]
        st.download_button(
                    label="MEMBER CONTRIBUTIONS",
                    data=csv_data,
                    file_name=f"MEMBERS.csv",
                    mime="text/csv")
    with colb:
        dat = dfpaye.copy()
        dat = dat.rename(columns = {'MONTHEX': 'DATE'})
        csv_data = dat.to_csv(index=False)
        tot = dat.shape[0]
        st.download_button(
                    label="EXPENDITURES",
                    data=csv_data,
                    file_name=f"EXPENDITURES.csv",
                    mime="text/csv")
    st.divider()
    todo = st.pills('**WHAT DO YOU WANT TO INPUT**', options=["MEMBERS' DEPOSIT",'' ,'','','EXPENDITURE'])
    if not todo:
        st.stop()
    else:
        if todo == 'EXPENDITURE':
            st.cache_data.clear()
            st.cache_resource.clear()
            #CHECKING MEMBERS WHO HAVEN'T PAID THIS MONTH
            dat = dt.date.today()
            mon = int(dat.strftime('%m'))
            dfpaye['MONTH'] = pd.to_datetime(dfpaye['MONTHEX'], errors='coerce')
            dfpaye['MON'] = dfpaye['MONTH'].dt.month
            dfpaye = dfpaye[dfpaye['MON']==mon]
            spent = dfpaye['AMOUNT'].sum()
            if spent ==0:
                st.markdown("<p style='color:purple';>NO AMOUNT HAS BEEN SPENT THIS MONTH</>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color:green';>{spent} Shs. HAS BEEN SPENT THIS MONTH/>", unsafe_allow_html=True)
            cola, colb, colc = st.columns([1,2,1])
            colb.info('EXPENDITURE DETAILS')
           
            cola,colb = st.columns([2,1])
            cola.write('**HOW MANY ITEMS DO YO WANT TO IN PUT**')
            cola,colb = st.columns([1,2])
            num = cola.number_input('**maximum input = 5**', value=None, max_value=5, min_value=1)
            if not num:
                st.stop()
            else:
                pass
            if num:
                items = []
                amounts = []
                for i in range(num):
                    cola,colb, colc = st.columns([2,1,2])
                    item = cola.text_input('**INPUT THE ITEM SPENT ON**',placeholder='eg TRANSPORT', key = i)           
                    if not item:
                        st.stop()
                    else:
                        items.append(item)
                    if item:
                        amount = colc.number_input(f'**AMOUNT SPENT ON {item}**', value=None, max_value=None, min_value=1000, key = f'{i}a')
                        if not amount:
                            st.stop()
                        else:
                            amounts.append(amount)
                    else:
                        pass
            if todo:
                df = pd.DataFrame({
                    'ITEM': items,
                    'AMOUNT': amounts
                            })
                df['MONTHEX'] = dat
                df = df[['ITEM', 'MONTHEX', 'AMOUNT']].copy()
                dfd = df[df.duplicated(subset='ITEM')]
                checka = df.shape[0]
                check = dfd.shape[0]

                if check>0:
                    dfd['ITEM'] = dfd['ITEM'].astype(str)
                    disa = ', '.join(dfd['ITEM'].unique())
                    st.warning(f'**You repeated {disa}**')
                    st.write(f"**SUM UP THE TOTAL SPENT ON {disa} INTO ONE ENTRY**")
                    st.stop()
                else:
                    st.write('**SUMMARY:** crosscheck before submission')
                if checka ==1:
                    st.markdown(f'**> YOU SPENT {amount} ON {item}**')
                    submit = st.button('**CLICK HERE TO SUBMIT**')
                if checka>1:
                    dfu = df[['ITEM', 'AMOUNT']]
                    dfu.index = pd.Index(range(1, len(dfu) + 1))
                    styled = (dfu.style
                        .set_table_styles([{'selector': 'table', 'props': [('border', '2px solid red')]}])
                        .set_table_styles([{'selector': 'td', 'props': [('font-weight', 'bold'),('color', 'green')]}])
                        .set_table_styles([{'selector': 'th', 'props': [('font-weight', 'bold'),('color', 'red') ]}])
                        )
                    st.table(styled)
                    submit = st.button('**CLICK HERE TO SUBMIT**')
                    if submit:
                        sheet1 = spreadsheet.worksheet("EXPENSES")
                        rows_to_append = df.values.tolist()
                        sheet.append_rows(rows_to_append, value_input_option='RAW')
                        time.sleep(2)
                        st.success('SUBMITTED SUCCESSFULLY')
                        st.markdown("""
                            <meta http-equiv="refresh" content="0">
                                """, unsafe_allow_html=True)
        elif todo == "MEMBERS' DEPOSIT":
            st.cache_data.clear()
            st.cache_resource.clear()
            #CHECKING MEMBERS WHO HAVEN'T PAID THIS MONTH
            dat = dt.date.today()
            mon = int(dat.strftime('%m'))
            dfpay['MONTH'] = pd.to_datetime(dfpay['MONTH'], errors='coerce')
            dfpay['MON'] = dfpay['MONTH'].dt.month
            dfpay = dfpay[dfpay['MON']==mon]
            members2 = dfpay['DIRECTOR'].unique()
            notpay = set(members)- set(members2)
            notpay = list(notpay)
            notpaid = len(notpay)
            if notpaid ==0:
                st.markdown("<p style='color:purple';>ALL MEMBERS HAVE PAID FOR THIS MONTH</>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color:green';>{notpaid} MEMBERS HAVEN'T CONTRIBUTED FOR THIS MONTH</>", unsafe_allow_html=True)
                st.write('**THEY ARE:**')
                st.write(set(notpay))
            cola, colb, colc = st.columns([1,2,1])
            colb.info('DEPOSIT DETAILS')
           
            cola,colb = st.columns([2,1])
            cola.write('**FOR HOW MANY MEMBERS ARE YOU DEPOSITING FOR**')
            cola,colb = st.columns([1,2])
            num = cola.number_input('**maximum input = 5**', value=None, max_value=5, min_value=1)
            if not num:
                st.stop()
            else:
                pass
            if num:
                names = []
                amounts = []
                for i in range(num):
                    cola,colb, colc = st.columns([2,1,1])
                    name = cola.selectbox('**CHOOSE A MEMBER**', members, index=None, key = i)           
                    if not name:
                        st.stop()
                    else:
                        names.append(name)
                    if name:
                        nam = str(name).split(' ')[0]
                        amount = colb.number_input(f'**AMOUNT FOR {nam}**', value=None, max_value=None, min_value=20000, key = f'{i}a')
                        if not amount:
                            st.stop()
                        else:
                            amounts.append(amount)
                    else:
                        pass
            if todo:
                df = pd.DataFrame({
                    'DIRECTOR': names,
                    'AMOUNT': amounts
                            })
                df['MONTH'] = dat
                df = df[['DIRECTOR', 'MONTH', 'AMOUNT']].copy()
                dfd = df[df.duplicated(subset='DIRECTOR')]
                checka = df.shape[0]
                check = dfd.shape[0]

                if check>0:
                    dfd['DIRECTOR'] = dfd['DIRECTOR'].astype(str)
                    disa = ', '.join(dfd['DIRECTOR'].unique())
                    st.warning(f'**You repeated {disa}**')
                    st.write("**SUM UP THEIR TOTAL CONTRIBUTION INTO ONE ENTRY**")
                    st.stop()
                else:
                    st.write('**SUMMARY:** crosscheck before submission')
                if checka ==1:
                    st.markdown(f'**> YOU ARE DEPOSITING {amount} for {name}**')
                    submit = st.button('**CLICK HERE TDEPOSTINGO SUBMIT**')
                if checka>1:
                    dfu = df[['DIRECTOR', 'AMOUNT']]
                    dfu.index = pd.Index(range(1, len(dfu) + 1))
                    styled = (dfu.style
                        .set_table_styles([{'selector': 'table', 'props': [('border', '2px solid red')]}])
                        .set_table_styles([{'selector': 'td', 'props': [('font-weight', 'bold'),('color', 'green')]}])
                        .set_table_styles([{'selector': 'th', 'props': [('font-weight', 'bold'),('color', 'red') ]}])
                        )
                    st.table(styled)
                    submit = st.button('**CLICK HERE TO SUBMIT**')
                    if submit:
                        sheet1 = spreadsheet.worksheet("CONTRIBUTIONS")
                        rows_to_append = df.values.tolist()
                        sheet.append_rows(rows_to_append, value_input_option='RAW')
                        time.sleep(2)
                        st.success('SUBMITTED SUCCESSFULLY')
                        st.markdown("""
                            <meta http-equiv="refresh" content="0">
                                """, unsafe_allow_html=True)
         


