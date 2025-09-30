#!/usr/bin/env python
# coding: utf-8

# ### Report for 2025 - GHO
# 

# In[1]:


import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


# #### TASK: COLLECTION TRANSACTIONS

# #### For Collection using the Complete_Transaction data table, calculate:
# 
# 
# 1. Total collection transaction value for dynamic accounts per merchant
# 2. Total collection transaction volume for dynamic accounts per merchant
# 3. Total collection transaction charges for dynamic accounts per merchant
# 

# In[2]:


# Dynamic Account Transaction

data_2 = pd.read_csv("transaction_2025-09-26.csv")
#data_2 = pd.read_csv("transaction_01_21_09.csv")


# In[3]:


# Concatenate vertically (default: axis=0 → rows)
#data_2 = pd.concat([data_A, data_B, data_C, data_D, data_E, data_F, data_G, data_H, data_I], ignore_index=True)

data_2


# In[4]:


# Assuming the column is in GMT times
# Convert to GMT+1 and remove the timezone information after conversion

data_2['time'] = pd.to_datetime(data_2['time'], unit='s', utc=True).dt.tz_convert('Africa/Lagos').dt.tz_localize(None)


# In[5]:


data_2['transaction_date'] = pd.to_datetime(data_2['time']).dt.date


# In[6]:


data_2 = data_2.sort_values(by= ['time'])


# In[7]:


data_2


# #### we want to only modify the format of our values without doing any operation in pandas, we should just execute the following instruction:
# This forces it not to use scientific notation (exponential notation) and always displays 2 places after the decimal point. It also adds commas

# In[8]:


pd.options.display.float_format = "{:,.2f}".format


# #### Since we are interested in only transfers that are successful by the users, we make use of amount whose status are success from the table.
# 
# But first, we check the info of the data provided and checking for any missing values in the data

# In[9]:


data_2


# In[ ]:





# In[10]:


data_2.info()


# In[11]:


## checking for missing values
data_2.isnull().sum()


# #### NGN transactions

# In[12]:


df_NGN = data_2.loc[data_2['currency'] == 'NGN']

df_NGN


# In[13]:


df_NGN.info()


# In[14]:


df_NGN.isnull().sum()


# In[15]:


df_NGN['status'].value_counts()


# In[16]:


df_NGN['type'].value_counts()


# In[17]:


df_NGN = df_NGN[['user_id', 'internal_ref', 'type', 'transaction_amount', 'settled_amount', 
               'charge', 'status', 'currency', 'transaction_date', 'time']]


# In[18]:


# fill missing values 'NaN' with "0.0"

df_NGN.fillna((0.00), inplace=True)

#df.isnull().sum()


# In[19]:


df_NGN.info()


# #### DONE Transactions

# In[20]:


df_1 = df_NGN.loc[df_NGN['status'] == 'Done']

df_1 


# In[21]:


df_1['account_type'] = 'Dynamic'


# In[22]:


df_1['channel'] = 'Collection'


# In[23]:


df_1['payment_rail'] = 'Checkout_Collection'


# In[24]:


df_1.rename(columns={"user_id": "merchantId", "internal_ref": "transaction_reference", "time": "created_at"}, inplace=True)


# In[25]:


# Define function to calculate bank partner's charge
def partner_charge(amount):
    M_charge = 0.013 * amount  # 1.3%
    return min(M_charge, 2000)  # Apply ₦2000 cap


# In[26]:


# Apply function to create new column
df_1["partner_cost"] = df_1["transaction_amount"].apply(partner_charge)


# In[27]:


df_1['profit'] = df_1['charge'] - df_1['partner_cost']#.round(2)


# In[28]:


df_1['pct_charged'] = ((df_1['charge'] * 100) / df_1['transaction_amount']).round(3)


# In[29]:


df_1.loc[df_1['profit'] < 0, 'gain_status'] = 'Loss' 
df_1.loc[df_1['profit'] == 0, 'gain_status'] = 'NLNP'
df_1.loc[df_1['profit'] > 0, 'gain_status'] = 'Profit' 


# In[30]:


df_1


# In[31]:


# we will be making use of some selected columns from the data

df_2 = df_1[['transaction_reference', 'merchantId', 'type', 'currency',  'channel', 'account_type', 'payment_rail',
             'transaction_amount', 'settled_amount', 'charge', 'partner_cost', 'profit', 'pct_charged', 
             'gain_status', 'transaction_date', 'created_at']]


# In[32]:


df_2


# In[33]:


df_2.info()


# In[34]:


df_2['gain_status'].value_counts()


# In[35]:


df_L = df_2.loc[df_2['gain_status'] == 'Loss']

df_L


# In[36]:


df_2['merchantId'].unique()


# In[ ]:


df_2.to_csv('dynamic_sept_X.csv', index=False)

