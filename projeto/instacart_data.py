import json, os, time

def get_departments() -> dict[str, str]:
    with open('./data/departments.csv', 'r') as file:
        next(file)
        return {line.strip().split(',')[0]: line.strip().split(',')[1] for line in file}

def get_aisles() -> dict[str, str]:
    with open('./data/aisles.csv', 'r') as file:
        next(file)
        return {line.strip().split(',')[0]: line.strip().split(',')[1] for line in file}

def get_order_products(reload:bool=False) -> dict[str, list[str]]:
    if not os.path.isfile('./data/order_products.json') or reload:
        order_products = {}
        files = ['order_products_prior.csv', 'order_products_train.csv']
        for file in files:
            print(f'Fazendo varredura do arquivo {file} ...')
            with open(f'./data/{file}', 'r') as f:
                next(f)
                for line in f:
                    order_id, product_id, _, _ = line.strip().split(',')
                    
                    if order_id not in order_products.keys():
                        order_products[order_id] = [product_id]
                    else:
                        order_products[order_id].append(product_id)
        print('Salvando dados dos produtos dos pedidos...')
        json.dump(order_products, open('./data/order_products.json', 'w'), indent=4)
        return order_products
    print('Carregando dados dos produtos dos pedidos...')
    return json.load(open('./data/order_products.json', 'r'))

def get_user_orders(reload:bool=False) -> dict[str, list[str]]:
    if not os.path.exists('./data/user_orders.csv') or reload:
        user_orders = {}
        print('Fazendo varredura no arquivo de pedidos...')
        with open('./data/orders.csv', encoding='utf8') as f:
            next(f)
            for line in f:
                order_id, user_id, _ , _, _, _, _ = line.split(',')
                
                if user_id not in user_orders.keys():
                    user_orders[user_id] = [order_id]
                else:
                    user_orders[user_id].append(order_id)
        print('Salvando dados dos pedidos dos usuários...')
        json.dump(user_orders, open('./data/user_orders.json', 'w', encoding='utf8'), indent=4)
        return user_orders
    print('Carregando dados dos pedidos dos usuários...')
    return json.load(open('./data/user_orders.json', 'r', encoding='utf8'))
    
def get_user_products(reload:bool=False) -> dict[str, dict[str, int]]:
    if not os.path.exists('./data/user_products.json') or reload:
        user_orders = get_user_orders()
        order_products = get_order_products()
        
        print('Fazendo levantamento de dados sobre os produtos dos usuários...')
        user_products = {}
        for user_id, orders in user_orders.items():
            user_products[user_id] = {}
            for order_id in orders:
                if order_id in order_products.keys():
                    for product_id in order_products[order_id]:
                        user_products[user_id][product_id] = user_products[user_id].get(product_id, 0) + 1
                # print(f'order {order_id} não encontrada (usuario: {user_id})')
        
        print('Salvando dados dos produtos dos usuários...')
        json.dump(user_products, open('./data/user_products.json', 'w', encoding='utf8'), indent=4)
        return user_products
    print('Carregando dados dos produtos dos usuários...')
    return json.load(open('./data/user_products.json', 'r', encoding='utf8'))

def get_products(reload:bool=False) -> dict[str, dict[str, str|int]]:
    if not os.path.exists('./data/products.json') or reload:
        aisles = get_aisles()
        departments = get_departments()
        user_products = get_user_products()
        
        print('Fazendo varredura no arquivo de produtos...')
        with open('./data/products.csv', 'r', encoding='utf8') as file:
            PRODUCTS = {}
            next(file)
            for line in file:
                if '"' in line:
                    line = line.replace('\""', '')
                    init, product_name, end = line.strip().split('"')
                    line = init + end
                product_id, scrap, aisle_id, department_id = line.strip().split(',')
                if scrap != '': product_name = scrap
                
                PRODUCTS[product_id] = {'name': product_name, 'aisle': aisles[aisle_id], 'department': departments[department_id]}
        
        print('Fazendo levantamento de dados sobre os produtos...')
        products_data = {}
        for products in user_products.values():
            for product_id, count in products.items():
                if product_id not in products_data.keys():
                    products_data[product_id] = {
                        'purchased once': 0, 
                        'purchased more than once': 0, 
                        'number of users purchased': 0,
                        'total purchases': 0,
                        'PRC': 0
                    }
                if count > 1:
                    products_data[product_id]['purchased once'] += 1
                else:
                    products_data[product_id]['purchased more than once'] += 1
                products_data[product_id]['number of users purchased'] += 1
                products_data[product_id]['total purchases'] += count
        
        products = {}
        for product_id, data in products_data.items():
            products_data[product_id]['PRC'] = data['purchased more than once']/data['number of users purchased']
            product_data = PRODUCTS.get(product_id, {'name': 'Error', 'aisle': 'other', 'department': 'other'})
            products[product_id] = {**data, **product_data}
                    
        print('Salvando dados dos produtos...')
        json.dump(products, open('./data/products.json', 'w', encoding='utf8'), indent=4)
        return products
    print('Carregando dados dos produtos...')
    return json.load(open('./data/products.json', 'r', encoding='utf8'))

def gen_edges_data(order_products:dict[str, list[str]], filename:str='edges', reload:bool=False) -> dict[str, int]:
    if not os.path.isfile(f'./data/{filename}.json') or reload:
        edges = {}
        t = time.time()
        print('Gerando dados das arestas...')
        for i, order in enumerate(order_products.values()):
            for productA in order:
                for productB in order:
                    if productA != productB: 
                        A, B = sorted([productA, productB])
                        edge = f'{A},{B}'
                        edges[edge] = edges.get(edge, 0)+1
            
            if time.time()-t > 10:
                t = time.time()
                print(f'{i/len(order_products)*100:.4f}%')
        print('Ordenando arestas por peso...')
        edges = dict(sorted(edges.items(), key=lambda x: x[1], reverse=True))
        print('Salvando dados das arestas...')
        json.dump(edges, open(f'./data/{filename}.json', 'w'), indent=4)
        return edges
    return json.load(open(f'./data/{filename}.json', 'r', encoding='utf8'))


def gen_edges_csv(edgesfilename:str, edges:dict[str, int], threshold:int=0) -> None:
    n = 0
    with open(f'./data/{edgesfilename}.csv', 'w') as file:
        for edge, value in edges.items():
            if value >= threshold:
                file.write(f'{edge},{value}\n')
                n += 1
    print(f'{n} arestas geradas com o threshold de {threshold}')