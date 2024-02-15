from elasticsearch import Elasticsearch,helpers
import streamlit as st
import time
import pandas as pd
import warnings
import altair as alt
from decouple import config
warnings.filterwarnings('ignore')
from dotenv import load_dotenv
import os
load_dotenv()

index_name='email_marketing'

elasticsearch_url = os.getenv('ELASTICSEARCH_URL')
elasticsearch_api_key = os.getenv('ELASTICSEARCH_API_KEY')
# # Connect to Elasticsearch
es = Elasticsearch(elasticsearch_url, api_key=elasticsearch_api_key)


# Page configuration
st.set_page_config(
    page_title="Own Clustering",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")
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
st.write(custom_css, unsafe_allow_html=True)
st.markdown(custom_css, unsafe_allow_html=True)
st.title("Email Marketing Data Selection")
total_count = es.count(index=index_name)['count']
# st.subheader(f"Total Available Email Address: {total_count}")

df_seg=pd.read_csv('affixcon_segments.csv',encoding='latin-1').dropna(subset=['segment_name'])
df_seg.category = df_seg.category.str.upper()
industry_list = df_seg['industry'].dropna().unique().tolist()
selected_industry = st.selectbox(' :bookmark_tabs: Enter Industry:', industry_list)
segment_industry_dict = df_seg.groupby('industry')['segment_name'].apply(list).to_dict()
item_list = segment_industry_dict[selected_industry]
select_all_segments = st.checkbox("Select All Segments",value=True)
if select_all_segments:
    selected_segments = item_list
else:
    selected_segments = st.multiselect("Select one or more segments:", item_list)

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

should_queries = [{'regexp': {'Concatenated.keyword': f'.*{word}.*'}} for word in selected_segments]
query = {
    'query': {
        'bool': {
            'should': should_queries,
            'minimum_should_match': 1  # At least one should match
        }
    }
}
industry_count = es.count(index=index_name, body=query)['count']
st.subheader(f"Total Industry Match Email Address: {industry_count}")
industry = es.search(index=index_name, body=query)['hits']['hits']
industry_list=[]
for hit in industry:
    # st.write(hit['_source'])
    industry_list.append(hit['_source'])
with st.expander("industry Match View Data"):
    st.write(pd.DataFrame(industry_list).sample(5))

all_age_range_values = get_distinct_values("age_range", index_name, es)
all_gender_values = get_distinct_values("Gender", index_name, es)
all_Income_values = get_distinct_values("Income", index_name, es)
all_Suburb_values = get_distinct_values("Suburb", index_name, es)
all_State_values = get_distinct_values("State", index_name, es)

age_range_filter = st.multiselect(f"Select Age Range", ["All"] + all_age_range_values)
Gender_filter = st.multiselect(f"Select Gender", ["All"] + all_gender_values)
Income_filter = st.multiselect(f"Select Income", ["All"] + all_Income_values)
Suburb_filter = st.multiselect(f"Select Suburb", ["All"] + all_Suburb_values)
State_filter = st.multiselect(f"Select State", ["All"] + all_State_values)


if "All" in age_range_filter:
    age_range_filter = all_age_range_values
if "All" in Gender_filter:
    Gender_filter = all_gender_values
if "All" in Income_filter:
    Income_filter = all_Income_values
if "All" in Suburb_filter:
    Suburb_filter = all_Suburb_values
if "All" in State_filter:
    State_filter = all_State_values

if 'must' not in query['query']['bool']:
    query['query']['bool']['must'] = []
if len(age_range_filter) > 0 and len(Gender_filter) > 0 and len(Income_filter) > 0 and len(Suburb_filter) > 0 and len(State_filter) > 0 :
# # Add filters to the query
    query['query']['bool']['must'].extend([
        {"terms": {"age_range.keyword": age_range_filter}},
        {"terms": {"Gender.keyword": Gender_filter}},
        {"terms": {"Income.keyword": Income_filter}},
        {"terms": {"Suburb.keyword": Suburb_filter}},
        {"terms": {"State.keyword": State_filter}}
    ])
else:
    st.warning("Please select at least one filter.")

# # Execute the search
result = es.search(index=index_name, body=query)['hits']['hits']
count = es.count(index=index_name, body=query)['count']

l=[]
for hit in result:
    # st.write(hit['_source'])
    l.append(hit['_source'])
if len(l)>0:
    with st.expander("View Data"):
        st.write(pd.DataFrame(l).sample(5))
else:
    st.warning('No MAtching Records Found!')
# st.write(count)
st.subheader(f"Total Matching Count: {count}")
# df=pd.read_csv('random_samples.csv').fillna("")
# df['Concatenated'] = df[['interests', 'brands_visited', 'place_categories','geobehaviour']].apply(lambda row: ' '.join(row), axis=1).str.strip()
# documents = df.to_dict(orient='records')

# # es.indices.create(index=index_name)

# actions = [
#     {
#         "_op_type": "index",
#         "_index": index_name,
#         "_source": document,
#     }
#     for document in documents
# ]

# # Perform the bulk index operation
# helpers.bulk(es, actions)
# # for document in documents:
# #     es.bulk(index=index_name, document=document)