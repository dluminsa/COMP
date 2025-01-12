import pandas as pd 
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import traceback
import streamlit as st
import plotly.express as px
import time
import numpy as np
#sdd
import gspread
import datetime as dt
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials

st.cache_data.clear()
st.cache_resource.clear()

st.set_page_config(
    'COMPETENCE YARD TRACKER'
)
file = r"MEMBERS.csv"
df = pd.read_csv(file)
df = df[df['MEMBER']!='ADMIN'].copy()
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
        director_name = user_df.iloc[0, 0]
        st.success(f"WELCOME, DIRECTOR {director_name}")
    else:
        st.error("Unable to retrieve your information. Please log in again.")
        st.session_state.logged_in = False
        st.rerun()
time.sleep(1)
if st.session_state.logged_in:
    conn = st.connection('gsheets', type=GSheetsConnection)
    exist = conn.read(worksheet= 'CONTRIBUTIONS', usecols=list(range(4)),ttl=5)
    dfp = exist.dropna(how='all')
    try:
        conn = st.connection('gsheets', type=GSheetsConnection)
        exist = conn.read(worksheet= 'CONTRIBUTIONS', usecols=list(range(4)),ttl=5)
        dfp = exist.dropna(how='all')
    except:
         st.write("POOR NETWORK, COULDN'T CONNECT TO DATABASE")
         st.write('REFRESH PAGE TO START AGAIN')
         st.stop()
    try:
        conn = st.connection('gsheets', type=GSheetsConnection)
        exista = conn.read(worksheet= 'EXPENSES', usecols=list(range(4)),ttl=5)
        dfe = exista.dropna(how='all')
    except:
         st.write("POOR NETWORK, COULDN'T CONNECT TO DATABASE")
         st.write('REFRESH PAGE TO START AGAIN')
         st.stop()
    dfpa = dfp[dfp['DIRECTOR']== director_name].copy()
    tot = dfp['AMOUNT'].sum()
    contribut = dfpa['AMOUNT'].sum()
    dfpaye = dfe.copy()
    exp = dfe['AMOUNT'].sum()
    bal = int(tot) - int(exp)
    perc = round((bal/tot)*100)
    spent = 100- int(perc)

    col1,col2,col3 = st.columns(3, gap='large')

    with col1:
        st.metric(label="**TOTAL CONTRIBUTION**", value=f'{tot:,.0f}')
    with col2:
        st.metric(label='**EXPENSES**', value=f'{exp:,.0f}')
    with col3:
        st.metric(label='**BALANCE**', value=f'{bal:,.0f}')

    st.divider()
    cola, colb = st.columns([1,4])
    colb.info(f'**DEAR DR. {director_name} BELOW IS YOUR CONTRIBUTION SUMMARY**')
    dfpay = dfpa.copy()
    nym = dfpa.shape[0]
    yours = contribut
    perc = perc/100
    yourb = round(int(yours) * perc)

    own = (yourb/bal)*100

    col1, col2 = st.columns(2)

    col1.write(f'**YOU HAVE SO FAR CONTRIBUTED: {nym} TIMES**')
    col2.write(f'**THIS IS A TOTAL OF:  {yours}**')
    col1.write(f'**EXPENSES OF {spent} % HAVE BEEN MADE**')
    col2.write(f'**YOUR ACTUAL BALANCE IS HENCE:  {yourb}**')
    st.divider()
    st.markdown(
    f"<p style='color:purple;'>YOU OWN {own:,.0f}% OF THE TOTAL CONTRIBUTIONS MADE SO FAR BY ALL MEMBERS</p>",
    unsafe_allow_html=True)

    tod = dt.date.today()
    mon = int(tod.strftime('%m'))
    check = dfpa.copy()
    check['MONTHA'] = pd.to_datetime(check['MONTH'], errors='coerce')
    check['MON'] = check['MONTHA'].dt.month
    dfpal = check.copy()
    check['MON'] = pd.to_numeric(check['MON'], errors='coerce')
    
    check = check[check['MON'] == mon]
    paid = check.shape[0]
    if paid == 0:
        st.warning("**YOU HAVEN'T CONTRIBUTED THIS MONTH**")
    else:
        pass

    #line graphs

    dfpl = dfp[['MONTH', 'AMOUNT']].copy()
    dfel = dfe[['MONTHEX', 'AMOUNT']].copy()
    dfpl['MONTHA'] = pd.to_datetime(dfpl['MONTH'], errors='coerce')
    dfpl['MON'] = dfpl['MONTHA'].dt.month
    dfpl['TYPE'] = 'CONTRIBUTION'
    dfpl['MON'] = pd.to_numeric(dfpl['MON'], errors='coerce')

    dfel['MONTHA'] = pd.to_datetime(dfel['MONTHEX'], errors='coerce')
    dfel['MON'] = dfel['MONTHA'].dt.month
    dfel['TYPE'] = 'SPENT'

    dfel['MON'] = pd.to_numeric(dfel['MON'], errors='coerce')
    dfpl = dfpl[['TYPE','MON', 'AMOUNT']].copy()
    dfcl = pd.concat([dfel, dfpl])#, on = 'MON', how = 'outer')
    dfcl = dfcl.sort_values(by = ['MON'])
    dfcl['MONA'] = pd.to_numeric(dfcl['MON'], errors='coerce')

    cola, colb, colc = st.columns([3,1,2])
    dfcl = dfcl[['MONA', 'TYPE', 'AMOUNT']].copy()
    groupd = dfcl.groupby(['MONA', 'TYPE'], as_index=False).sum()
    
    with cola:
        fig = px.line(
            groupd,
            x="MONA",
            y="AMOUNT",
            color="TYPE",
            color_discrete_map={"SPENT": "red", "CONTRIBUTION": "blue"},
            markers=True,  # Optional: Add markers to the lines
            title="TREND THE GROUP'S CONTRIBUTIONS AND EXPENSES"
        )
        fig.update_layout(
        xaxis=dict(title='Month', tickformat='d'),
        yaxis=dict(title='Total Amount', tickformat='d'),
        template='plotly_white'
               )
        st.plotly_chart(fig)
    with colc:
        aggregated_df = dfcl.groupby("TYPE")["AMOUNT"].sum().reset_index()
        fig = px.pie(
        aggregated_df,
        names="TYPE",
        values="AMOUNT",
        title="BALANCE VS SPENT",
        hole=0.1, 
        color="TYPE", 
        color_discrete_map={"SPENT": "red", "CONTRIBUTION": "blue"} # Optional: Makes it a donut chart
         )
        st.plotly_chart(fig)
    st.divider()    
        
    cola, colb, colc = st.columns([1,2,1])
    with colb:
            grouped = dfpal.groupby('MON', as_index=False)['AMOUNT'].sum()
            # Plot the line graph
            fig = px.line(grouped, x='MON', y='AMOUNT', markers=True, title='Your contributions over the months')

            # Update layout to ensure x-axis is displayed with integer ticks
            fig.update_layout(
                xaxis=dict(tickmode='array', tickvals=grouped['MON'], title='Month'),
                yaxis=dict(title='Total Amount', tickformat='d'),
                template='plotly_white'
               )

            st.plotly_chart(fig)

if st.session_state.logged_in:
    st.markdown("<p style='color:red'><b><u>DOWNLOADS</u></b></p>", unsafe_allow_html=True)
    cola, colb = st.columns(2)
    with cola:
        dat = dfpay.copy()
        dat = dat.rename(columns = {'MONTH': 'DATE'})
        csv_data = dat.to_csv(index=False)
        tot = dat.shape[0]
        st.download_button(
                    label="YOUR CONTRIBUTIONS",
                    data=csv_data,
                    file_name=f"YOURS.csv",
                    mime="text/csv")
    with colb:
        dat = dfpaye.copy()
        dat = dat.rename(columns = {'MONTHEX': 'DATE'})
        csv_data = dat.to_csv(index=False)
        tot = dat.shape[0]
        st.download_button(
                    label="ALL EXPENDITURES",
                    data=csv_data,
                    file_name=f"EXPENDITURES.csv",
                    mime="text/csv")



   



    


    


    

        
