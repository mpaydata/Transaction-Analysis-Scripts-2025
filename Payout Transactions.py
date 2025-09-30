#!/usr/bin/env python
# coding: utf-8

# ### Report for 2025

# In[1]:


import numpy as np
import pandas as pd
import pytz
import warnings
warnings.filterwarnings("ignore")


# #### TASK: PAYOUT

# In[2]:


# Dynamic Account Transaction

data_1 = pd.read_csv("transfer_2025-09-26.csv")

data_1


# In[ ]:





# In[3]:


# Assuming the column is in GMT times
# Convert to GMT+1 and remove the timezone information after conversion

data_1['time'] = pd.to_datetime(data_1['time'], unit='s', utc=True).dt.tz_convert('Africa/Lagos').dt.tz_localize(None)


# In[4]:


data_1


# In[5]:


data_1['transaction_date'] = pd.to_datetime(data_1['time']).dt.date


# In[6]:


data_1.info()


# In[7]:


data_1.isnull().sum()


# #### NGN PAYOUT

# In[8]:


df_NGN = data_1.loc[data_1['currency'] == 'NGN']


# In[9]:


df_NGN.info()


# In[10]:


df_NGN = df_NGN.drop(['id', 'session_id'], axis=1)


# In[11]:


df_NGN['userId'] = pd.to_numeric(df_NGN['userId'], errors='coerce').astype('Int64')


# In[12]:


# Since there are non-numeric values or NaNs in the amount column, 
# we use pd.to_numeric with the errors='coerce' parameter to handle them gracefully:
# The errors='coerce' parameter will convert any non-numeric values to NaN, preventing errors during conversion.

df_NGN['amount'] = pd.to_numeric(df_NGN['amount'], errors='coerce')


# In[13]:


df_NGN['charge'].fillna(0.0, inplace=True) 


# In[14]:


# the gransaction reference for payout is always unique and should not have duplicates
df_NGN['transaction_reference'].nunique()


# #### we want to only modify the format of our values without doing any operation in pandas, we should just execute the following instruction:
# This forces it not to use scientific notation (exponential notation) and always displays 2 places after the decimal point. It also adds commas.

# In[15]:


pd.options.display.float_format = "{:,.2f}".format


# In[16]:


# checking the status to know how many transfer were successful and how many were failed.

df_NGN['status'].value_counts()


# In[17]:


df_NGN['account_type'] = "Payout"


# In[18]:


df_NGN['channel'] = "Payout"


# In[19]:


df_NGN['payment_rail'] = "Payout"


# In[20]:


df_NGN['settled_amount'] = 0.00


# In[21]:


# change amount column name tO reserved account collection value

df_NGN.rename(columns={"userId": "merchantId", "amount": "transaction_amount", "time": "created_at"}, inplace=True)


# In[22]:


df_NGN.loc[df_NGN['status'] == 'success', 'partner_cost'] = 10.00


# #### Since we are interested in only transfers that are successful by the users, we make use of amount whose status are success from the table.

# In[23]:


df_1 = df_NGN.loc[df_NGN['status'] == 'success']

df_1


# In[24]:


df_1['type'] = 'TRANSFER'


# In[25]:


df_1['pct_charged'] = df_1['charge']


# In[26]:


df_1['profit'] = (df_1['charge'] - df_1['partner_cost']).round(1)


# In[27]:


df_1['gain_status'] = ''


# In[28]:


df_1.loc[df_1['profit'] < 0, 'gain_status'] = 'Loss' 
df_1.loc[df_1['profit'] == 0, 'gain_status'] = 'NLNP'
df_1.loc[df_1['profit'] > 0, 'gain_status'] = 'Profit' 


# In[29]:


df_1['pct_charged'].value_counts()


# In[30]:


# we will be making use of some selected columns from the data

df_2 = df_1[['transaction_reference', 'merchantId', 'type', 'currency',  'channel', 'account_type', 'payment_rail',
             'transaction_amount', 'settled_amount', 'charge', 'partner_cost', 'profit', 'pct_charged', 
             'gain_status', 'transaction_date', 'created_at']]


# In[31]:


df_2


# In[32]:


df_2['merchantId'].unique()


# In[33]:


df_2['gain_status'].value_counts()


# In[34]:


df_2.to_csv("payout_sept_26x.csv", index=False)


# In[ ]:




