import pandas as pd
import streamlit as st
from elasticsearch import Elasticsearch,helpers
import os
import time
import re 
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title='Real Estate',layout='wide')
custom_css = """
<style>
body {
    background-color: #22222E; 
    secondary-background {
    background-color: #FA55AD; 
    padding: 10px; 
}
</style>
"""
st.get_option("theme.use_container_width")
st.write(custom_css, unsafe_allow_html=True)
st.markdown(custom_css, unsafe_allow_html=True)
st.image('AFFIXCON-LOGO.png')

index_name='real_estate'
elasticsearch_url = os.getenv('ELASTICSEARCH_URL')
elasticsearch_api_key = os.getenv('ELASTICSEARCH_API_KEY')
es = Elasticsearch(elasticsearch_url, api_key=elasticsearch_api_key)
st.title("Email Marketing Data Selection")

#-----------------------------------------------------------------
df_seg=pd.read_csv('affixcon_segments.csv',encoding='latin-1').dropna(subset=['segment_name'])
df_seg['code'] = df_seg['code'].astype(str)
df_seg.category = df_seg.category.str.upper()
selected_code= df_seg.loc[df_seg['industry'] == str('Real estate'), 'code'].values[0]
# st.write(selected_code)

def filter_values(df, input_char):
    
    numeric_part = re.search(r'\d+', input_char)
    # Extract unique values from column 'b' that start with the given input_char
    filtered_values = [value for value in df['code'].unique() if value.startswith(input_char)]

    # # If input_char has a dot ('.'), filter values at any level with one more digit after the dot
    if '.' in input_char:
        filtered_values = [value for value in filtered_values if re.match(f"{input_char}\.\d+", value)]
    else:
        if numeric_part: 
            filtered_values = [item for item in filtered_values if str(item).count('.') == 1]
            filtered_values = [value for value in filtered_values if value.split('.')[0] == input_char]
    #     # If input_char is only alphabet, filter values without a dot ('.')
        else:
            filtered_values = [value for value in filtered_values if not re.search(r'\.', value)]
            filtered_values = [item for item in filtered_values if str(item) != input_char]
    return filtered_values


item_list = []
segment_industry_dict = df_seg.groupby('code')['segment_name'].apply(list).to_dict()
def find_similar_codes(input_code, df):
    similar_codes = []
    for index, row in df.iterrows():
        code = row['code']
        if isinstance(code, str) and code.startswith(input_code):
            similar_codes.append(code)
    return similar_codes


user_contain_list = list(set(find_similar_codes(selected_code, df_seg)))

if selected_code in user_contain_list:
    for code in user_contain_list:
        item_list_code = segment_industry_dict[code]
        for item in item_list_code:
            item_list.append(item)
else:
    item_list = []

selected_segments=item_list
# st.write(selected_segments)


segment_category_dict = df_seg.set_index('segment_name')['category'].to_dict()
result_dict = {}
filtered_dict = {key: value for key, value in segment_category_dict.items() if key in selected_segments}

for key, value in filtered_dict.items():

    if value not in result_dict:
        result_dict[value] = []

    result_dict[value].append(key)
    result_dict = {key: values for key, values in result_dict.items()}
# st.write(result_dict)

if 'BRAND VISITED' in result_dict and 'BRANDS VISITED' in result_dict:
    # Extend the 'a' values with 'a1' values
    result_dict['BRAND VISITED'].extend(result_dict['BRANDS VISITED'])
    # Delete the 'a1' key
    del result_dict['BRANDS VISITED']

selected_category = st.sidebar.radio("Select one option:", list(result_dict.keys()))
if selected_segments:
    if selected_category == 'INTERESTS':
        segment_list=result_dict['INTERESTS']
    elif selected_category == 'BRAND VISITED':
        segment_list=result_dict['BRAND VISITED']
    elif selected_category == 'PLACE CATEGORIES':
        segment_list=result_dict['PLACE CATEGORIES']
    elif selected_category == 'GEO BEHAVIOUR':
        segment_list=result_dict['GEO BEHAVIOUR']
else:
    segment_list=[]

for j in segment_list:
    st.sidebar.write(j)
#-----------------------------------------------------------------
industry_count=es.count(index=index_name)['count']
# st.write(industry_count)

industry = es.search(index=index_name)['hits']['hits']

def get_distinct_values(field, index, es):
    query = {
        "aggs": {
            "distinct_values": {
                "terms": {"field": f"{field}.keyword","size": 10000}
            }
        }
    }

    result = es.search(index=index, body=query)
    return [bucket["key"] for bucket in result["aggregations"]["distinct_values"]["buckets"]]

all_age_range_values = get_distinct_values("Age_range", index_name, es)
all_gender_values = get_distinct_values("Gender", index_name, es)
all_Income_values = get_distinct_values("Income", index_name, es)
all_Suburb_values = get_distinct_values("Suburb", index_name, es)
all_State_values = get_distinct_values("State", index_name, es)


sti=time.time()
st.text("Please Select All Demographics with Own Selections. If not Select ALL")
age_range_filter = st.multiselect(f"Select Age_Range", ["All"]+sorted(set(value for value in all_age_range_values if value != '')))
Gender_filter = st.multiselect(f"Select Gender", ["All"]+sorted(set(value for value in all_gender_values if value != '' and value != "_")))
Income_filter = st.multiselect(f"Select Income", ["All"]+sorted(set(value for value in all_Income_values if value != '')))
Suburb_filter = st.multiselect(f"Select Suburb", ["All"]+sorted(set(all_Suburb_values)))
State_filter = st.multiselect(f"Select State", ["All"]+sorted(set(all_State_values)))

if 'All' in age_range_filter:
    age_range_filter=all_age_range_values
if 'All' in Gender_filter:
    Gender_filter=all_gender_values
if 'All' in Income_filter:
    Income_filter=all_Income_values
if 'All' in Suburb_filter:
    Suburb_filter=all_Suburb_values
if 'All' in State_filter:
    State_filter=all_State_values

query = {
    'query': {
        'bool': {
            'must': []
        }
    }
}
if len(age_range_filter)>0 and len(Gender_filter)>0 and len(Income_filter)>0 and len(Suburb_filter)>0 and len(State_filter)>0:
    query['query']['bool']['must'].extend([
        {"terms": {"Age_range.keyword": age_range_filter}},
        {"terms": {"Gender.keyword": Gender_filter}},
        {"terms": {"Income.keyword": Income_filter}},
        {"terms": {"Suburb.keyword": Suburb_filter}},
        {"terms": {"State.keyword": State_filter}}
    ])
else:
    st.warning("Please Select All filter.")

selections = [
    {"selected_industry": 'Real estate'},
    {"niche_list": segment_list},
    {"age_range_filter": age_range_filter} if len(age_range_filter)!=len(all_age_range_values) else {},
    {"Gender_filter": Gender_filter} if len(Gender_filter)!=len(all_gender_values) else {},
    {"Income_filter": Income_filter} if len(Income_filter)!=len(all_Income_values) else {},
    {"Suburb_filter": Suburb_filter} if len(Suburb_filter)!=len(all_Suburb_values) else {},
    {"State_filter": State_filter} if len(State_filter)!=len(all_State_values) else {},
]
flat_dict = {}
for item in selections:
    flat_dict.update({key: str(value) for key, value in item.items()})
    selections = pd.DataFrame([flat_dict]).set_index('selected_industry')

def mask_data(data):
    data['Firstname'] = '*****' + data['Firstname'][5:]
    data['Surname'] = '*****' + data['Surname'][5:]
    data['Ad1'] = '*********'
    email_parts = data['EmailAddress'].split('@')
    data['EmailAddress'] = '*****' + email_parts[1]

    return data

if st.button('Submit for see the counts'):
    st.write('Total Records: ',industry_count)
# # Execute the search
    result = es.search(index=index_name, body=query)['hits']['hits']
    count = es.count(index=index_name, body=query)['count']
    et=time.time()

    st.write("Total Matching Count",count)
    st.write('Time taken',str(round(((et-sti)),2))+' seconds')

    selections = pd.DataFrame([flat_dict]).set_index('selected_industry')

    st.write("Total Matching Count",selections)
    sample_df = es.search(index=index_name, body=query,size=5)['hits']['hits']
    l=[]
    for hit in sample_df:
        # st.write(hit['_source'])
        l.append(hit['_source'])
    if len(l)>0:
        with st.expander("View Sample Niche Market Selected Data"):
            st.write(pd.DataFrame(l).apply(mask_data,axis=1)[['Firstname','Surname','Age_range','Gender','Suburb','State']])