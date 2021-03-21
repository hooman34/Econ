import streamlit as st
import numpy as np
import pandas as pd
import investpy
import pandas as pd
import json
from matplotlib import pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
# from sklearn import preprocessing
# from PIL import Image
import os
import quandl
from fredapi import Fred
from econ_platform.utils.utils import (fred_quandl, fred_fred, convert_date_format)

with open('utils/index_codes.json', 'r') as indx:
    index_codes = json.load(indx)

st.title("PLATFORM")

page = st.sidebar.selectbox(
  'Select page', ('Overview', 'Insights')
  )

if page == 'Overview':

  st.write("Specify the start and end dates. Format should be YYYY-MM-DD")
  start_date = st.text_input('Start date (YYYY-MM-DD)')
  end_date = st.text_input('End date (YYYY-MM-DD)')

  if start_date and end_date:
  
    selected_indices = st.multiselect('Select the index', ['Treasury 10y', 'M2', 'SP500','CPI-U'])
    if len(selected_indices) >3:
      st.write("Only up to 3 indices can be displayed at once. Please disable the others.")
    else:
      start_date = convert_date_format(start_date, 'MDY')
      end_date = convert_date_format(end_date, 'MDY')
      index_data = list()
      fig = go.Figure()

      for index in selected_indices:
        data = fred_fred(index_codes['Fred'][index], column_name=index, observation_start=start_date, observation_end=end_date)
        index_data.append(data)
        plot = px.line(data, x='date', y=index)
        # fig.add_trace(plot)
      
        st.plotly_chart(plot, use_container_width=True)

  # TODO: merge the lines into one graph.
  # TODO: Create difference bewteen values.

elif page == 'Insights':
    st.write("Insight page")
#   st.subheader("Result of dynamic regression")
#   st.write("The first time running the model might take a while.")
#   ## execute Rscript
#   execute_dymanicreg()
#   st.write("Done executing Rscript. See the results below.")
#   ##
#   summary = st.checkbox('Show summary of dynamic regression')
#   resultplot = st.checkbox('Show result plot')
#   boxpierce = st.checkbox("Show result of box pierce test")
#   residuals = st.checkbox('Show residual plots')
#   ##
#   if summary:
#     f = open('result/arima_result.txt', 'r')
#     st.text(f.read())
#   if resultplot:
#     img = Image.open('result/result_plot.jpg')
#     st.image(img, use_column_width=True)
#   if boxpierce:
#     f = open('result/box_pierce_test.txt', 'r')
#     st.text(f.read())
#   if residuals:
#     acf = Image.open('result/residual_acf.jpg')
#     pacf = Image.open('result/residual_pacf.jpg')
#     histo = Image.open('result/residual_histo.jpg')
#     res = Image.open('result/residual_plot.jpg')
#     st.image([acf, pacf, histo, res], use_column_width=True)
