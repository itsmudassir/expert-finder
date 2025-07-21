import pymongo

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://admin:dev2018@5.161.225.172:27017/?authSource=admin')
db = client['llm_parsed_db']

collections = ['cat_1', 'cat_2', 'cat_3', 'cat_4']

print('\nMISSING/EMPTY FIELD ANALYSIS:')
print('='*60)

for collection_name in collections:
    collection = db[collection_name]
    total = collection.count_documents({})
    
    print(f'\n{collection_name} (Total: {total:,} documents):')
    
    # Check for missing or empty fields
    missing_expertise = collection.count_documents({'field_of_expertise': {'$exists': False}})
    empty_expertise = collection.count_documents({'field_of_expertise': []})
    has_expertise = collection.count_documents({'field_of_expertise': {'$exists': True, '$ne': []}})
    
    missing_education = collection.count_documents({'education': {'$exists': False}})
    empty_education = collection.count_documents({'education': []})
    
    missing_event_types = collection.count_documents({'event_types': {'$exists': False}})
    empty_event_types = collection.count_documents({'event_types': []})
    
    missing_location = collection.count_documents({'location': {'$exists': False}})
    empty_location = collection.count_documents({'location': ''})
    
    print(f'  Field of Expertise:')
    print(f'    - Has values: {has_expertise:,} ({has_expertise/total*100:.1f}%)')
    print(f'    - Missing: {missing_expertise:,} ({missing_expertise/total*100:.1f}%)')
    print(f'    - Empty array: {empty_expertise:,} ({empty_expertise/total*100:.1f}%)')
    
    print(f'  Education:')
    print(f'    - Missing: {missing_education:,} ({missing_education/total*100:.1f}%)')
    print(f'    - Empty array: {empty_education:,} ({empty_education/total*100:.1f}%)')
    
    print(f'  Event Types:')
    print(f'    - Missing: {missing_event_types:,} ({missing_event_types/total*100:.1f}%)')
    print(f'    - Empty array: {empty_event_types:,} ({empty_event_types/total*100:.1f}%)')
    
    print(f'  Location:')
    print(f'    - Missing: {missing_location:,} ({missing_location/total*100:.1f}%)')
    print(f'    - Empty string: {empty_location:,} ({empty_location/total*100:.1f}%)')

# Check data consistency
print('\n\nDATA CONSISTENCY CHECK:')
print('='*60)

for collection_name in collections:
    collection = db[collection_name]
    
    # Check for duplicate speaker names
    pipeline = [
        {'$group': {'_id': '$speaker_name', 'count': {'$sum': 1}}},
        {'$match': {'count': {'$gt': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ]
    
    duplicates = list(collection.aggregate(pipeline))
    
    if duplicates:
        print(f'\n{collection_name} - Top duplicate speaker names:')
        for dup in duplicates:
            print(f'  - "{dup["_id"]}": {dup["count"]} occurrences')