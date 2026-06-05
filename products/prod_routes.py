from flask import render_template, request, jsonify
from products import prod_bp
from products.prod_models import (
    get_smart_watches, get_leather_watches, get_metal_watches,
    get_all_products, get_all_earbuds, get_mix_products,
    search_products, get_product_by_slug
)


@prod_bp.route('/smart_watches')
def smart_watches():
    products,page,total_pages=get_smart_watches(request)
    return render_template('smart_watches.htm',products=products,page=page, 
                           total_pages=total_pages)


@prod_bp.route('/leather_watches')
def leather_watches():
    products,page,total_pages=get_leather_watches(request)
    return render_template('leather_watches.htm',products=products, 
                           page=page,total_pages=total_pages)


@prod_bp.route('/metal_watches')
def metal_watches():
    products,page,total_pages=get_metal_watches(request)
    return render_template('metal_watches.htm',products=products,
                           page=page,total_pages=total_pages)


@prod_bp.route('/all_products',methods=['GET'])
def all_products():
    result=get_all_products(request)
    if not result:
        return render_template('404.htm'), 404
    
    products,categories,page,total_pages=result
    return render_template('all_products.htm',products=products,
                           categories=categories,page=page,total_pages=total_pages)


@prod_bp.route('/all_earbuds',methods=['GET'])
def all_earbuds():
    result=get_all_earbuds(request)
    if not result:
        return render_template('404.htm'), 404
    
    products,page,total_pages=result
    return render_template('all_earbuds.htm',products=products,
                           page=page,total_pages=total_pages)


@prod_bp.route('/mix_products',methods=['GET'])
def mix_products():
    result=get_mix_products(request)
    if not result:
        return render_template('404.htm'), 404
    
    products,page,total_pages=result
    return render_template('mix_products.htm',products=products, 
                           page=page,total_pages=total_pages)


@prod_bp.route('/search')
def search():
    q=request.args.get('q', '').strip()
    fmt=request.args.get('format','html')

    if not q:
        if fmt=='json':
            return jsonify([])
        
        return render_template('all_products.htm',products=[],categories=[])

    products=search_products(q)

    if fmt=='json':
        return jsonify(products)

    return render_template('all_products.htm',products=products,categories=[])


@prod_bp.route('/<slug>',methods=['GET'])
def product_page(slug):
    result=get_product_by_slug(slug)
    if not result:
        return render_template('404.htm'), 404
    
    product,product_images,relateds,reviews=result
    return render_template('product_page.htm',product=product,relateds=relateds,
                           reviews=reviews,product_images=product_images)