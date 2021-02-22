# %%
import requests
import pandas as pd
import streamlit as st
import json
import base64


# %%
@st.cache
def get(url):
    return requests.get(url)


r = get('https://www.bankofcanada.ca/valet/observations/group/FX_RATES_DAILY/json?start_date=2015-01-03')
data = json.loads(r.content)
df = pd.DataFrame.from_dict(data['observations'])
for i, row in df.iterrows():
    for j, cell in enumerate(row):
        if type(cell) is dict:
            df.iloc[i, j] = cell['v']

df['d'] = pd.to_datetime(df['d'])
min_date = df.d.min()
max_date = df.d.max()
resampling = {
    'Year': 'Y',
    'Month': 'M',
    'Quarter': 'Q',
    'Week': 'W',
    'Day': 'D'
}
# %%
st.write('Bank of Canada data')
date_df = df.set_index('d').astype(float)

st.sidebar.title('Filter data')
fx_rate = st.sidebar.multiselect(
    'Pick one or more rates', list(date_df.columns), default=['FXUSDCAD', 'FXEURCAD'])
sample = st.sidebar.selectbox(
    'Group by', options=list(resampling.keys()), index=2)
start, end = st.sidebar.date_input('Date Range', value=(min_date, max_date))

option = fx_rate or 'FXUSDCAD'
sample_rate = resampling[sample] if sample else 'M'
st.write(date_df.loc[start:end, option].resample(sample_rate).mean())
st.line_chart(data=date_df.loc[start:end, option])

# Download file


def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt',
                  'Click here to download your text!')

    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(
            index=True, index_label='Date')

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


if st.sidebar.button('Download data as CSV'):
    tmp_download_link = download_link(
        date_df.loc[start:end, option].resample(sample_rate).mean(), 'bocRate.csv', 'Click here to download your data!')
    st.sidebar.markdown(f"**{tmp_download_link}**", unsafe_allow_html=True)
