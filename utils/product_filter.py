from flask import request as _unused  


def build_product_filter(request,exclude_category=None):
    
    q=request.args.get('q', '').strip()
    category=request.args.get('category', '')
    min_price=request.args.get('min_price', 0,type=int)
    max_price=request.args.get('max_price', 60000,type=int)
    in_stock=request.args.get('in_stock', '')
    on_sale=request.args.get('on_sale', '')
    sort=request.args.get('sort', 'newest')

    conditions=["p.status='active'"]
    params=[]

    if exclude_category is not None:
        conditions.append(f"p.category_id != {int(exclude_category)}")

    if q:
        conditions.append("(p.title LIKE %s OR p.product_no LIKE %s)")
        params.extend([f'%{q}%', f'%{q}%'])

    if category:
        conditions.append("p.category_id=%s")
        params.append(category)

    if min_price:
        conditions.append("COALESCE(p.sale_price, p.base_price) >= %s")
        params.append(min_price)

    if max_price < 60000:
        conditions.append("COALESCE(p.sale_price, p.base_price) <= %s")
        params.append(max_price)

    if in_stock:
        conditions.append("p.stock_quantity > 0")

    if on_sale:
        conditions.append("p.sale_price IS NOT NULL AND p.sale_price < p.base_price")

    
    order_map={
        'price_asc':'COALESCE(p.sale_price, p.base_price) ASC',
        'price_desc':'COALESCE(p.sale_price, p.base_price) DESC',
        'popular':'p.product_id DESC',
        'name_asc':'p.title ASC',
        'newest':'p.created_at DESC',
    }
    order_clause=order_map.get(sort,'p.created_at DESC')

    where_str=' AND '.join(conditions)

    return{
        'where_str':where_str,
        'params':params,
        'order_clause':order_clause,
        'values':{
            'q':q,
            'category':category,
            'min_price':min_price,
            'max_price':max_price,
            'in_stock':in_stock,
            'on_sale':on_sale,
            'sort':sort,
        },
    }
