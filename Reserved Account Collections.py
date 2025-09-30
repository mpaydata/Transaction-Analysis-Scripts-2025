#!/usr/bin/env python
# coding: utf-8

# ### Report for NGN 2025

# In[1]:


import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


# ### TASK: RESERVED ACCOUNT COLLECTIONS

# In[2]:


# Reserved Account Transaction

data_3 = pd.read_csv("ra_transaction_2025-09-25.csv")

data_3


# In[3]:


data_3['webhook_data'].isnull().sum()#unique()


# In[4]:


data_3 = data_3.drop('id', axis=1)


# In[5]:


# Assuming the column is in GMT times
# Convert to GMT+1 and remove the timezone information after conversion

data_3['time'] = pd.to_datetime(data_3['time'], unit='s', utc=True).dt.tz_convert('Africa/Lagos').dt.tz_localize(None)


# In[8]:


data_3['transaction_date'] = pd.to_datetime(data_3['time']).dt.date


# In[9]:


data_3 = data_3.dropna(subset=["userId", "reference"])
data_3 = data_3[~((data_3["userId"] == "") & (data_3["reference"] == ""))]


# In[11]:


data_3 = data_3.sort_values(by= ['time'])


# In[12]:


data_3


# #### we want to only modify the format of your values without doing any operation in pandas, you should just execute the following instruction:
# This forces it not to use scientific notation (exponential notation) and always displays 2 places after the decimal point. It also adds commas.

#  we check the info of the data provided and checking for any missing values in the data

# In[13]:


data_3.info()


# In[14]:


## checking for missing values
data_3.isnull().sum()


# In[15]:


data_3['userId'] = pd.to_numeric(data_3['userId'], errors='coerce').astype('Int64')


# In[16]:


data_3['amount'] = data_3['amount'].astype(float)


# In[17]:


data_3['charge'] = (data_3['amount'] - data_3['amount_settled']).round(2)


# In[18]:


data_3['pct_charged'] = ((data_3['charge'] * 100) / data_3['amount']).round(1)


# In[19]:


data_3["payment_rail"] = np.where(
    (data_3["transaction_reference"].isna()) & (data_3["userId"].notna()),
    "Settlement",
    "Reserved_Account"
)


# In[20]:


data_3["transaction_reference"].fillna(data_3["reference"], inplace=True)


# In[21]:


pd.options.display.float_format = "{:,.2f}".format


# In[22]:


# Define function to calculate bank partner's charge
def partner_charge(amount):
    M_charge = 0.013 * amount  # 1.3%
    return min(M_charge, 2000)  # Apply ₦2000 cap


# In[24]:


# Apply function to create new column
data_3["partner_cost"] = data_3["amount"].apply(partner_charge)


# In[25]:


data_3['type'] = 'TRANSFER'


# In[26]:


data_3['account_type'] = 'Reserved'


# In[27]:


data_3['channel'] = 'Collection'


# In[29]:


data_3['profit'] = (data_3['charge'] - data_3['partner_cost']).round(2)


# In[30]:


data_3.rename(columns={"userId": "merchantId", "amount": "transaction_amount", 
                       "time": "created_at", "amount_settled": "settled_amount"}, inplace=True)


# In[31]:


data_3['gain_status'] = ''


# In[32]:


data_3.loc[data_3['profit'] < 0, 'gain_status'] = 'Loss' 
data_3.loc[data_3['profit'] == 0, 'gain_status'] = 'NLNP'
data_3.loc[data_3['profit'] > 0, 'gain_status'] = 'Profit' 


data_3


# In[34]:


# we will be making use of some selected columns from the data

df_1 = data_3[['transaction_reference', 'merchantId', 'type', 'currency',  'channel', 'account_type', 'payment_rail',
             'transaction_amount', 'settled_amount', 'charge', 'partner_cost', 'profit', 'pct_charged', 
             'gain_status', 'transaction_date', 'created_at']]


# In[35]:


df_1#.info()


# In[ ]:





# In[37]:


df_1['gain_status'].value_counts()


# In[ ]:


df_1.to_csv('reserved_sept_25.csv', index=False)


# In[ ]:




