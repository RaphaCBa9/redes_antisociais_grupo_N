import graph_tool_extras as gte
import pandas as pd
import scipy
from instacart_data import get_products

PRODUCTS = get_products()

def get_or_add_vertex(g, id):
    v = g.vertex_by_id(id)
    if v is None:
        v = g.add_vertex_by_id(id)
        p = PRODUCTS[str(id)]
        v['aisle'] = p['aisle']
        v['department'] = v['department']
        v['name'] = p['name']
        v['purchased once'] = p['purchased once']
        v['purchased more than once'] = p['purchased more than once']
        v['number of users purchased'] = p['number of users purchased']
        v['total purchases'] = p['total purchases']
        v['PRC'] = p['PRC']
    return v

def get_or_add_edge(g, a, b, v):
    e = g.edge_by_ids(a, b)
    if e is None:
        e = g.add_edge_by_ids(a, b)
        e['orders'] = v
    return e


def gen_net(edgesfilename:str):
    g = gte.Graph(directed=False)
    g.add_ep('orders')
    
    g.add_vp('aisle')
    g.add_vp('department')
    g.add_vp('name')
    g.add_vp('purchased once')
    g.add_vp('purchased more than once')
    g.add_vp('number of users purchased')
    g.add_vp('total purchases')
    g.add_vp('PRC')
    
    with open(f'./data/{edgesfilename}.csv') as file:
        for line in file:
            a, b, v = [int(x) for x in line.strip().replace('\n', '').split(',')]
            vA = get_or_add_vertex(g, a)
            vB = get_or_add_vertex(g, b)
        
            e = get_or_add_edge(g, a, b, v)
    
    return g

def from_net_to_dataframe(net):
    data = {}
    for v in net.vertices():
        for key, value in v.items():
            key = key.replace(' ', '_')
            if key not in data.keys():
                data[key] = []
            data[key].append(value)
    return pd.DataFrame(data)

def pearsonr(x, y, ndigits=10):
    statistic, p_value = scipy.stats.pearsonr(x, y)
    
    asterisk = ''
    statistic = round(statistic, ndigits)
    
    if statistic == 1: 
        asterisk = ' (óbvio)'
    elif p_value < 0.01: 
        asterisk = ' ***'
    elif p_value < 0.05: 
        asterisk = ' **'
    elif p_value < 0.1: 
        asterisk = ' *'
        
    return f'{statistic} {asterisk}'