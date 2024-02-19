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
import re
load_dotenv()

index_name='email_marketing'

elasticsearch_url = os.getenv('ELASTICSEARCH_URL')
elasticsearch_api_key = os.getenv('ELASTICSEARCH_API_KEY')
# # Connect to Elasticsearch
es = Elasticsearch(elasticsearch_url, api_key=elasticsearch_api_key)


# Page configuration
st.set_page_config(
    page_title="Email Marketing",
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
df_seg['code'] = df_seg['code'].astype(str)
df_seg.category = df_seg.category.str.upper()
industry_list = df_seg['industry'].dropna().unique().tolist()
selected_industry = st.selectbox(' :bookmark_tabs: Enter Industry:', industry_list)
selected_code= df_seg.loc[df_seg['industry'] == str(selected_industry), 'code'].values[0]
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
# st.subheader(f"Total Industry Match Email Address: {industry_count}")

#--------------------------------------------------------------------------------------

industry_list=[]
filtered_codes = filter_values(df_seg, selected_code)
# st.write(filtered_codes)
code_industry_dict = df_seg.groupby('code')['industry'].apply(list).to_dict()

# if selected_code in filtered_codes:
for code in filtered_codes:
    item_list_code = code_industry_dict[code]
    for item in item_list_code:
        industry_list.append(item)

industry_list=list(set(industry_list))
# Determine the number of columns based on the length of industry_list
niche_list=[]

if len(industry_list)>0:
    num_columns = len(industry_list)
    st.write("Select Niche Market Industry")
    # Create the columns dynamically
    columns = st.columns(num_columns)
    selected_industries = []
    for i, industry in enumerate(industry_list):
        checkbox_industry_list = columns[i].checkbox(industry)
        if checkbox_industry_list:
            selected_code= df_seg.loc[df_seg['industry'] == str(industry), 'code'].values[0]
            selected_industries.append(selected_code)
            # st.write(selected_code)  
    for code in selected_industries:
        item_list_code = segment_industry_dict[code]
        for item in item_list_code:
            niche_list.append(item)

else:
    pass

should_queries = [{'regexp': {'Concatenated.keyword': f'.*{word}.*'}} for word in niche_list]
query = {
    'query': {
        'bool': {
            'should': should_queries,
            'minimum_should_match': 1  # At least one should match
        }
    }
}
niche_count = es.count(index=index_name, body=query)['count']
# st.subheader(f"Total Niche Market Match Email Address: {niche_count}")


#-----------------------------------------------------------------------------------------------------------------

industry = es.search(index=index_name, body=query)['hits']['hits']
# all_age_range_values = [hit['_source']['age_range'] for hit in industry['hits']['hits']]
# unique_age_ranges = set(all_age_range_values)
all_age_range_values = [hit['_source']['age_range'] for hit in industry]
all_gender_values = [hit['_source']['Gender'] for hit in industry]
all_Income_values = [hit['_source']['Income'] for hit in industry]
unique_income_values = sorted(set(value for value in all_Income_values if value != 'unknown_income'))
ordered_categories = [
    "$20,800 - $41,599",
    "$41,600 - $64,999",
    "$65,000 - $77,999",
    "$78,000 - $103,999",
    "$104,000 - $155,999",
    "$156,000+"
]
sorted_income_values = sorted(unique_income_values, key=lambda x: ordered_categories.index(x))
ordered_income_series = pd.Categorical(sorted_income_values, categories=ordered_categories, ordered=True)
all_Suburb_values = [hit['_source']['Suburb'] for hit in industry]
all_State_values = [hit['_source']['State'] for hit in industry]

# industry_list=[]
# for hit in industry:
#     # st.write(hit['_source'])
#     industry_list.append(hit['_source'])
# # with st.expander("industry Match View Data"):
#     # st.write(pd.DataFrame(industry_list).sample(5))
# industry_list=pd.DataFrame(industry_list)
# st.write(industry_list)

# all_age_range_values = get_distinct_values("age_range", index_name, es)
# all_age_range_values= st.multiselect("Select age ranges", sorted(set(age_range_values)))
# all_gender_values= st.multiselect("Select Gender", sorted(set(all_gender_values)))
# all_Income_values= st.multiselect("Select Income ranges", sorted(set(all_Income_values)))
# all_Suburb_values= st.multiselect("Select Suburb", sorted(set(all_Suburb_values)))
# all_State_values= st.multiselect("Select State", sorted(set(all_State_values)))


# all_gender_values = get_distinct_values("Gender", index_name, es)
# all_Income_values = get_distinct_values("Income", index_name, es)
# all_Suburb_values = get_distinct_values("Suburb", index_name, es)
# all_State_values = get_distinct_values("State", index_name, es)

age_range_filter = st.multiselect(f"Select Age Range", ["All"] + sorted(set(value for value in all_age_range_values if value != '')))
Gender_filter = st.multiselect(f"Select Gender", ["All"] + sorted(set(value for value in all_gender_values if value != 'unknown_gender')))
Income_filter = st.multiselect(f"Select Income", ["All"] + list(ordered_income_series))
Suburb_filter = st.multiselect(f"Select Suburb", ["All"] + sorted(set(all_Suburb_values)))
State_filter = st.multiselect(f"Select State", ["All"] + sorted(set(all_State_values)))


if "All" in age_range_filter:
    # age_range_filter = all_age_range_values
    age_range_filter=all_age_range_values
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
# if len(l)>0:
#     with st.expander("View Data"):
#         st.write(pd.DataFrame(l).sample(5))
# else:
#     st.warning('No Matching Records Found!')

if len(Suburb_filter)==2966:
    Suburb_filter='all suburbs selected'

# selected_i=[]
# for code in selected_industries:
#     selected_i= df_seg.loc[df_seg['code'] == str(code), 'industry'].values[0]
#     selected_i.append(selected_i)

selections=[{"selected_industry":selected_industry},{"selected_industries":selected_industries},{"niche_list":niche_list},{"age_range_filter":age_range_filter},{"Gender_filter":Gender_filter},{"Income_filter":Income_filter},{"Suburb_filter":Suburb_filter},{"State_filter":State_filter}]
# def flatten_list(nested_list):
#     flat_list = []
#     for item in nested_list:
#         if isinstance(item, list):
#             flat_list.extend(flatten_list(item))
#         else:
#             flat_list.append(item)
#     return flat_list
flat_dict = {}
for item in selections:
    flat_dict.update(item)
selections = pd.DataFrame([flat_dict]).set_index('selected_industry')

# flattened_list = flatten_list(selections)
# flattened_list=[{"selected_industry":selected_industry},{"selected_industries":selected_industries},{"niche_list":niche_list},{"age_range_filter":age_range_filter},{"Gender_filter":Gender_filter},{"Income_filter":Income_filter},{"Suburb_filter":Suburb_filter},{"State_filter":State_filter}]
# selections = pd.DataFrame(flattened_list, columns=['Selection Critetias','Filters'])

# st.subheader(f"Total Matching Count: {count}")
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

if st.button("Click me to process selections"):
    
    st.subheader(f"Total Industry Match Email Address: {industry_count}")
    st.subheader(f"Total Niche Market Match Email Address: {niche_count}")
    st.subheader(f"Total Niche Market With Selected Filters: {count}")
    if len(l)>0:
        with st.expander("View Niche Market Selected Data"):
            st.write(pd.DataFrame(l).sample(5))
    else:
        st.warning('No Matching Records Found!')
    with st.expander("View All Selection Criterias"):
        st.write("Selection Criterias",selections)
