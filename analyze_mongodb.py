import pymongo
from collections import Counter
from pprint import pprint

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin')
db = client['llm_parsed_db']

# Analyze unique fields and patterns
collections = ['cat_1', 'cat_2', 'cat_3', 'cat_4']

print('\nFIELD PRESENCE ANALYSIS')
print('='*60)

# Check field presence across collections
field_presence = {}

for collection_name in collections:
    collection = db[collection_name]
    
    # Sample more documents to get better field coverage
    sample_size = min(100, collection.count_documents({}))
    docs = list(collection.find().limit(sample_size))
    
    all_fields = set()
    for doc in docs:
        all_fields.update(doc.keys())
    
    field_presence[collection_name] = all_fields

# Display field presence
for col, fields in field_presence.items():
    print(f'\n{col} fields: {sorted(fields)}')

# Find unique fields per collection
print('\n\nUNIQUE FIELDS PER COLLECTION:')
print('='*60)

for col, fields in field_presence.items():
    other_cols_fields = set()
    for other_col, other_fields in field_presence.items():
        if other_col != col:
            other_cols_fields.update(other_fields)
    
    unique_only_to_this = fields - other_cols_fields
    if unique_only_to_this:
        print(f'\n{col} unique fields: {sorted(unique_only_to_this)}')

# Analyze expertise field values
print('\n\nEXPERTISE FIELD VALUE ANALYSIS:')
print('='*60)

for collection_name in collections:
    collection = db[collection_name]
    
    # Get all expertise values
    expertise_docs = list(collection.find({'field_of_expertise': {'$exists': True}}).limit(50))
    
    if expertise_docs:
        all_expertise = []
        for doc in expertise_docs:
            expertise = doc.get('field_of_expertise', [])
            if isinstance(expertise, list):
                all_expertise.extend(expertise)
        
        # Count most common expertise areas
        expertise_counter = Counter(all_expertise)
        
        print(f'\n{collection_name} - Top 10 expertise areas:')
        for expertise, count in expertise_counter.most_common(10):
            print(f'  - {expertise}: {count}')