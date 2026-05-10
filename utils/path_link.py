
CATEGORY_ROUTES={
    1:"/products/smart_watches.htm",
    2:"/products/metal_watches.htm",
    3:"/products/leather_watches.htm",
    4:"/products/all_earbuds",
}

CATEGORY_PARENT={
    1:("Watches","/products/all_products"),
    2:("Watches","/products/all_products"),
    3:("Watches","/products/all_products"),
    4:("Earbuds","/products/all_earbuds"),
}

def make_links(product):
    cat_id=product['category_id']
    cat_name=product['category_name']

    parent_label,parent_url=CATEGORY_PARENT.get(cat_id, ("Products","/products/all_products"))
    cat_url=CATEGORY_ROUTES.get(cat_id,"/products/all_products")

    result=[
        {"label":"Home","url": "/"},
        {"label":parent_label,"url":parent_url},
        {"label":cat_name,"url":cat_url},
        {"label":product['title'],"url":None},
    ]
    return result