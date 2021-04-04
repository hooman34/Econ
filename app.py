import streamlit as st
import numpy as np
import pandas as pd
import investpy
import pandas as pd
import json
from matplotlib import pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go
# from sklearn import preprocessing
# from PIL import Image
import os
import quandl
from fredapi import Fred
from econ_platform.utils.utils import (fred_quandl, fred_fred, investing_api, convert_date_format,
                                       seekingAlpha_estimates)

with open('econ_platform/utils/index_codes.json', 'r') as indx:
    index_codes = json.load(indx)


def two_data_plot_widget(start_date, end_date, key='key1'):
  """
  the widget that plots two data
  """
  st.sidebar.write('-'*5)
  source_list = ['Fred', 'Investing.com']
  source1 = st.sidebar.selectbox("Select first data source:", source_list, key=key)
  selected_index1 = st.sidebar.selectbox('Select the index', list(index_codes[source1].keys()), key=key)
  data1 = _call_data(source1, selected_index1, start_date, end_date)

  source2 = st.sidebar.selectbox("Select second data source:", source_list, key=key+'_')
  selected_index2 = st.sidebar.selectbox('Select the index', list(index_codes[source2].keys()), key=key+'_')
  data2 = _call_data(source2, selected_index2, start_date, end_date)

  fig = _plot_two_data(data1, data2, source1, source2, selected_index1, selected_index2)

  return data1, data2, fig
  
@st.cache
def _call_data(source, selected_index, start_date, end_date, country='united states'):
  """
  Call the data to the corresponding source.
  """
  start_date = convert_date_format(start_date, source)
  end_date = convert_date_format(end_date, source)
  if source=='Fred':
    data = fred_fred(index_codes[source][selected_index], 
                     column_name=selected_index, observation_start=start_date, observation_end=end_date)
  elif source=='Investing.com':
    call_type = selected_index.split(' - ')[0]
    data = investing_api(call_type, index_codes[source][selected_index], from_date=start_date, to_date=end_date, country=country)

  return data

# TODO: process data according to each source type
# TODO: Create difference bewteen values.

def _plot_two_data(data1, data2, source1, source2, selected_index1, selected_index2):

  trace1 = _plotly_create_trace(data1, source1, selected_index1)
  trace2 = _plotly_create_trace(data2, source2, selected_index2)

  fig = go.Figure()
  fig = make_subplots(specs=[[{"secondary_y": True}]])
  fig.add_trace(trace1)
  fig.add_trace(trace2, secondary_y=True)

  return fig

def _plotly_create_trace(data, source, selected_index):

  if source=='Fred':
    trace = go.Scatter(x=data['date'],
                       y=data[selected_index],
                       name=selected_index)
  elif source=='Investing.com':
    trace = go.Scatter(x=data['Date'],
                       y=data['Close'],
                       name=selected_index)
  return trace

@st.cache
def call_estimates(ticker_list, data_type, period_type='annual'):

  estimate_list = list()
  for ticker in ticker_list:
    estimate_list.append(seekingAlpha_estimates(ticker, data_type, period_type))

  estimates_all = pd.concat(estimate_list, axis=0)
  return estimates_all


st.set_page_config(layout="wide") 
st.title("PLATFORM")

page = st.sidebar.selectbox(
  'Select page', ('Draw graphs', 'Portfolio Check')
  )

if page == 'Draw graphs':

  st.write("Specify the start and end dates. Format should be YYYY-MM-DD")
  start_date = st.sidebar.text_input('Start date (YYYY-MM-DD)')
  end_date = st.sidebar.text_input('End date (YYYY-MM-DD)')

  if start_date and end_date:
    data1_1, data1_2, fig1 = two_data_plot_widget(start_date, end_date, key='key1')
    st.plotly_chart(fig1, use_container_width=True)
  
    data2_1, data2_2, fig2 = two_data_plot_widget(start_date, end_date, key='key2')
    st.plotly_chart(fig2, use_container_width=True)


elif page == 'Portfolio Check':
  st.write("Portfolio Check")

  data_type = st.selectbox("Select data type", ('eps', 'revenues'))
  ticker_list = st.text_input('Input all the tickers. Separated with space. e.g. "AAPL AMZN LMT MSFT"')
  ticker_list = ticker_list.split(' ')
  if st.button("Retrieve data"):
    estimates_all = call_estimates(ticker_list, data_type)
    st.dataframe(estimates_all)

