import pandas as pd
import streamlit as st
from elasticsearch import Elasticsearch,helpers
import os
import time
import re 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from dotenv import load_dotenv
load_dotenv()

# st.set_page_config(page_title='Real Estate',layout='wide')
# custom_css = """
# <style>
# body {
#     background-color: #22222E; 
#     secondary-background {
#     background-color: #FA55AD; 
#     padding: 10px; 
# }
# </style>
# """
# st.write(custom_css, unsafe_allow_html=True)
# st.markdown(custom_css, unsafe_allow_html=True)
#     # Replace these with your Zoho Mail SMTP server details
# ZOHO_SMTP_SERVER = os.getenv('ZOHO_SMTP_SERVER')
# ZOHO_SMTP_PORT = 587
# ZOHO_USERNAME = os.getenv('ZOHO_USERNAME')  # Replace with your Zoho Mail address
# ZOHO_PASSWORD = os.getenv('ZOHO_PASSWORD')  # Replace with your Zoho Mail app password
# SENDING_EMAIL=os.getenv('SENDING_EMAIL')


# def send_email_zoho(email, df,name,email_address,mobile):
#     subject = 'Data Request'
#     body = f'Please find below details for customer details for Data Request \nCustomer Name: {name} \nCustomer Email: {email_address} \nCustomer Mobile: {mobile}'

#     # Connect to the Zoho Mail SMTP server
#     server = smtplib.SMTP(ZOHO_SMTP_SERVER, ZOHO_SMTP_PORT)
#     server.starttls()

#     # Login to your Zoho Mail account
#     server.login(ZOHO_USERNAME, ZOHO_PASSWORD)

#     # Compose the email
#     message = MIMEMultipart()
#     message['Subject'] = subject
#     message['From'] = ZOHO_USERNAME
#     message['To'] = email
#     message.attach(MIMEText(body))

#     # Convert DataFrame to CSV and attach it
#     csv_data = df.to_csv()
#     attachment = MIMEText(csv_data)
#     attachment.add_header('Content-Disposition', 'attachment', filename='Selection Criterias.csv')
#     message.attach(attachment)

#     # Send the email
#     server.sendmail(ZOHO_USERNAME, [email], message.as_string())

#     # Quit the server
#     server.quit()

# index_name='real_estate'
# elasticsearch_url = os.getenv('ELASTICSEARCH_URL')
# elasticsearch_api_key = os.getenv('ELASTICSEARCH_API_KEY')
# es = Elasticsearch(elasticsearch_url, api_key=elasticsearch_api_key)
# st.title("Email Marketing Data Selection")

# #-----------------------------------------------------------------
# df_seg=pd.read_csv('affixcon_segments.csv',encoding='latin-1').dropna(subset=['segment_name'])
# df_seg['code'] = df_seg['code'].astype(str)
# df_seg.category = df_seg.category.str.upper()
# selected_code= df_seg.loc[df_seg['industry'] == str('Real estate'), 'code'].values[0]
# # st.write(selected_code)

# def filter_values(df, input_char):
    
#     numeric_part = re.search(r'\d+', input_char)
#     # Extract unique values from column 'b' that start with the given input_char
#     filtered_values = [value for value in df['code'].unique() if value.startswith(input_char)]

#     # # If input_char has a dot ('.'), filter values at any level with one more digit after the dot
#     if '.' in input_char:
#         filtered_values = [value for value in filtered_values if re.match(f"{input_char}\.\d+", value)]
#     else:
#         if numeric_part: 
#             filtered_values = [item for item in filtered_values if str(item).count('.') == 1]
#             filtered_values = [value for value in filtered_values if value.split('.')[0] == input_char]
#     #     # If input_char is only alphabet, filter values without a dot ('.')
#         else:
#             filtered_values = [value for value in filtered_values if not re.search(r'\.', value)]
#             filtered_values = [item for item in filtered_values if str(item) != input_char]
#     return filtered_values


# item_list = []
# segment_industry_dict = df_seg.groupby('code')['segment_name'].apply(list).to_dict()
# def find_similar_codes(input_code, df):
#     similar_codes = []
#     for index, row in df.iterrows():
#         code = row['code']
#         if isinstance(code, str) and code.startswith(input_code):
#             similar_codes.append(code)
#     return similar_codes


# user_contain_list = list(set(find_similar_codes(selected_code, df_seg)))

# if selected_code in user_contain_list:
#     for code in user_contain_list:
#         item_list_code = segment_industry_dict[code]
#         for item in item_list_code:
#             item_list.append(item)
# else:
#     item_list = []

# selected_segments=item_list
# # st.write(selected_segments)


# segment_category_dict = df_seg.set_index('segment_name')['category'].to_dict()
# result_dict = {}
# filtered_dict = {key: value for key, value in segment_category_dict.items() if key in selected_segments}

# for key, value in filtered_dict.items():

#     if value not in result_dict:
#         result_dict[value] = []

#     result_dict[value].append(key)
#     result_dict = {key: values for key, values in result_dict.items()}
# # st.write(result_dict)

# if 'BRAND VISITED' in result_dict and 'BRANDS VISITED' in result_dict:
#     # Extend the 'a' values with 'a1' values
#     result_dict['BRAND VISITED'].extend(result_dict['BRANDS VISITED'])
#     # Delete the 'a1' key
#     del result_dict['BRANDS VISITED']

# selected_category = st.sidebar.radio("Select one option:", list(result_dict.keys()))
# if selected_segments:
#     if selected_category == 'INTERESTS':
#         segment_list=result_dict['INTERESTS']
#     elif selected_category == 'BRAND VISITED':
#         segment_list=result_dict['BRAND VISITED']
#     elif selected_category == 'PLACE CATEGORIES':
#         segment_list=result_dict['PLACE CATEGORIES']
#     elif selected_category == 'GEO BEHAVIOUR':
#         segment_list=result_dict['GEO BEHAVIOUR']
# else:
#     segment_list=[]

# for j in segment_list:
#     st.sidebar.write(j)





# #-----------------------------------------------------------------

# industry_count=es.count(index=index_name)['count']
# # st.write(industry_count)

# industry = es.search(index=index_name)['hits']['hits']

# def get_distinct_values(field, index, es):
#     query = {
#         "aggs": {
#             "distinct_values": {
#                 "terms": {"field": f"{field}.keyword","size": 10000}
#             }
#         }
#     }

#     result = es.search(index=index, body=query)
#     return [bucket["key"] for bucket in result["aggregations"]["distinct_values"]["buckets"]]

# all_age_range_values = get_distinct_values("Age_range", index_name, es)
# all_gender_values = get_distinct_values("Gender", index_name, es)
# all_Income_values = get_distinct_values("Income", index_name, es)
# all_Suburb_values = get_distinct_values("Suburb", index_name, es)
# all_State_values = get_distinct_values("State", index_name, es)

















# # all_age_range_values = [hit['_source']['Age_range'] for hit in industry]
# # all_gender_values = [hit['_source']['Gender'] for hit in industry]
# # all_Income_values = [hit['_source']['Income'] for hit in industry]
# # unique_income_values = sorted(set(value for value in all_Income_values if value != ''))
# # ordered_categories = [
# #     "Under $20,799",
# #     "$20,800 - $41,599",
# #     "$41,600 - $64,999",
# #     "$65,000 - $77,999",
# #     "$78,000 - $103,999",
# #     "$104,000 - $155,999",
# #     "$156,000+"
# # ]
# # sorted_income_values = sorted(unique_income_values, key=lambda x: ordered_categories.index(x))
# # ordered_income_series = pd.Categorical(sorted_income_values, categories=ordered_categories, ordered=True)
# # all_Suburb_values = [hit['_source']['Suburb'] for hit in industry]
# # all_State_values = [hit['_source']['State'] for hit in industry]

# sti=time.time()
# demographics_features = st.multiselect('Select Features to Analyze', ['Gender', 'Age_Range', 'Income', 'Suburb', 'State'])

# # Initialize filters
# # age_range_filter = ["All"]
# # Gender_filter = ["All"]
# # Income_filter = ["All"]
# # Suburb_filter = ["All"]
# # State_filter = ["All"]

# # Update options based on selected demographics_features
# if 'Age_Range' in demographics_features:
#     age_range_filter = st.multiselect(f"Select Age_Range", sorted(set(value for value in all_age_range_values if value != '')))

# if 'Gender' in demographics_features:
#     Gender_filter = st.multiselect(f"Select Gender", sorted(set(value for value in all_gender_values if value != '' and value != "_")))

# if 'Income' in demographics_features:
#     Income_filter = st.multiselect(f"Select Income", sorted(set(value for value in all_Income_values if value != '')))

# if 'Suburb' in demographics_features:
#     Suburb_filter = st.multiselect(f"Select Suburb", sorted(set(all_Suburb_values)))

# if 'State' in demographics_features:
#     State_filter = st.multiselect(f"Select State", sorted(set(all_State_values)))


# if 'Age_Range' not in demographics_features:
#     # age_range_filter = all_age_range_values
#     age_range_filter=all_age_range_values
# if "Gender" not in demographics_features:
#     Gender_filter = all_gender_values
# if 'Income' not in demographics_features:
#     Income_filter = all_Income_values
# if 'Suburb' not in demographics_features:
#     Suburb_filter = all_Suburb_values
# if 'State' not in demographics_features:
#     State_filter = all_State_values

# query = {
#     'query': {
#         'bool': {
#             'must': []
#         }
#     }
# }

# if len(demographics_features) > 0:
# # # Add filters to the query
#     query['query']['bool']['must'].extend([
#         {"terms": {"Age_range.keyword": age_range_filter}},
#         {"terms": {"Gender.keyword": Gender_filter}},
#         {"terms": {"Income.keyword": Income_filter}},
#         {"terms": {"Suburb.keyword": Suburb_filter}},
#         {"terms": {"State.keyword": State_filter}}
#     ])
# else:
#     st.warning("Please select at least one filter.")


# selections = [
#     {"selected_industry": 'Real estate'},
#     {"niche_list": segment_list},
#     {"age_range_filter": age_range_filter} if 'Age_Range' in demographics_features else {},
#     {"Gender_filter": Gender_filter} if 'Gender' in demographics_features else {},
#     {"Income_filter": Income_filter} if 'Income' in demographics_features else {},
#     {"Suburb_filter": Suburb_filter} if 'Suburb' in demographics_features else {},
#     {"State_filter": State_filter} if 'State' in demographics_features else {},
# ]
# flat_dict = {}
# for item in selections:
#     flat_dict.update({key: str(value) for key, value in item.items()})
# # st.write(pd.DataFrame([flat_dict]).set_index('selected_industry').T)


# def mask_data(data):
#     data['Firstname'] = '*****' + data['Firstname'][5:]
#     data['Surname'] = '*****' + data['Surname'][5:]
#     data['Ad1'] = '*********'
#     email_parts = data['EmailAddress'].split('@')
#     data['EmailAddress'] = '*****' + email_parts[1]

#     return data

# if 'state' not in st.session_state:
#     st.session_state.state = {}

# if st.button('Submit for see the counts'):
#     st.write('Total Records: ',industry_count)
# # # Execute the search
#     result = es.search(index=index_name, body=query)['hits']['hits']
#     count = es.count(index=index_name, body=query)['count']
#     et=time.time()

#     st.write("Total Matching Count",count)
#     st.write('Time taken',str(round(((et-sti)),2))+' seconds')

#     selections = pd.DataFrame([flat_dict]).set_index('selected_industry')
#     st.session_state.state['selections'] = selections

#     sample_df = es.search(index=index_name, body=query,size=5)['hits']['hits']
#     l=[]
#     for hit in sample_df:
#         # st.write(hit['_source'])
#         l.append(hit['_source'])
#     if len(l)>0:
#         with st.expander("View Niche Market Selected Data"):
#             st.write(pd.DataFrame(l).apply(mask_data,axis=1)[['Firstname','Surname','Age_range','Gender','Suburb','State']])

# name=st.text_input('Enter Your Name:')
# email=st.text_input('Enter Your Email Address:')
# mobile=st.text_input('Enter Your Mobile Number:')

# if name and email and mobile is not None:

#     if 'selections' in st.session_state.state and st.button('Request Data'):
#             send_email_zoho(SENDING_EMAIL, st.session_state.state['selections'].T,name,email,mobile)
#             st.success(f'Thank you for your data request. The selection data has been sent to Affixcon.')
# else:
#     st.warning('Please Enter your details to request data')
#     # else:
#     #     st.error('Please enter a valid Zoho Mail address.')





















start_row = 1000000
end_row = 1048577
usecols=['Age_range','Gender','Suburb','State','Geo_INcome','interests','brands','place_categories','geobehaviour']
df = pd.read_csv('data\PA2072_Health_Care_Data_20240228.csv', encoding='latin-1' ,usecols=usecols,skiprows=range(1, start_row), nrows=end_row - start_row).fillna("")
df['Concatenated'] = df[['interests','brands','place_categories','geobehaviour']].apply(lambda row: ' '.join(row), axis=1).str.strip()
df=df[['Age_range','Gender','Suburb','State','Geo_INcome','Concatenated']]
documents = df.to_dict(orient='records')


elasticsearch_url = os.getenv('ELASTICSEARCH_URL')
elasticsearch_api_key = os.getenv('ELASTICSEARCH_API_KEY')
es = Elasticsearch(elasticsearch_url, api_key=elasticsearch_api_key,timeout=10000)
# es.indices.create(index="health-care")
index_name='health-care'

actions = [
    {
        "_op_type": "index",
        "_index": "health-care",
        "_source": document,
    }
    for document in documents
]

# Perform the bulk index operation
helpers.bulk(es, actions)
for document in documents:
    es.bulk(index=index_name, document=document)

