import json, os, zipfile
     
EDGES = json.load(open('./data/edges.json'))
ORDERS = json.load(open('./data/orders.json')).values()

if os.path.isfile('./data/departments.zip'):
    with zipfile.ZipFile('./data/departments.zip', 'r') as zip_ref:
        zip_ref.extractall('./data')
        with open('./data/departments.csv', 'r') as file:
            next(file)
            DEPARTMENTS = {line.strip().split(',')[0]: line.strip().split(',')[1] for line in file}
        
if os.path.isfile('./data/aisles.zip'):
    with zipfile.ZipFile('./data/aisles.zip', 'r') as zip_ref:
        zip_ref.extractall('./data')
        with open('./data/aisles.csv', 'r') as file:
            next(file)
            AISLES = {line.strip().split(',')[0]: line.strip().split(',')[1] for line in file}


if os.path.isfile('./data/products.zip'):
    with zipfile.ZipFile('./data/products.zip', 'r') as zip_ref:
        zip_ref.extractall('./data')

PRODUCTS = {}
departament_counts = {}
aisle_counts = {}

with open('./data/products.csv', 'r', encoding='utf8') as file:
    next(file)
    for line in file:
        if '"' in line:
            line = line.replace('\""', '')
            init, product_name, end = line.strip().split('"')
            line = init + end
        product_id, scrap, aisle_id, department_id = line.strip().split(',')
        if scrap != '': product_name = scrap
        
        PRODUCTS[product_id] = {'name': product_name, 'aisle': AISLES[aisle_id], 'department': DEPARTMENTS[department_id]}
        departament_counts[department_id] = departament_counts.get(department_id, 0)+1
        aisle_counts[aisle_id] = aisle_counts.get(aisle_id, 0)+1
        
DEPARTMENT_COUNTS = dict(sorted(departament_counts.items(), key=lambda x: x[1], reverse=True))
AISLE_COUNTS = dict(sorted(aisle_counts.items(), key=lambda x: x[1], reverse=True))