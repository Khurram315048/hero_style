from flask import render_template,request,jsonify
from products import prod_bp
from utils.db import mysql
from utils.path_link import make_links

from utils.product_filter import build_product_filter
import MySQLdb.cursors




@prod_bp.route('/smart_watches.htm')
def smart_watches():
    cursor=mysql.connection.cursor()
 
    cursor.execute(""" SELECT p.product_id,p.product_no,p.title,p.stock_quantity,
            p.base_price,p.sale_price,p.status,c.name  AS category_name,
            pd.short_description,pi.image_url,pi.alt_text
        FROM products p
        LEFT JOIN categories c  ON p.category_id=c.category_id
        LEFT JOIN product_details pd ON p.product_id=pd.product_id
        LEFT JOIN product_images pi  ON p.product_id=pi.product_id
        AND pi.is_active=1
        WHERE p.status='active' AND p.category_id=1         
        GROUP BY p.product_id
        ORDER BY p.product_id ASC
        LIMIT 5
    """)
 
    products=cursor.fetchall()
    cursor.close()
    return render_template('smart_watches.htm',products=products)



@prod_bp.route('/leather_watches.htm')
def leather_watches():
    cursor=mysql.connection.cursor()
 
    cursor.execute(""" SELECT p.product_id,p.product_no,p.title,
            p.base_price,p.sale_price,p.status,c.name  AS category_name,
            pd.short_description,pi.image_url,pi.alt_text
        FROM products p
        LEFT JOIN categories c  ON p.category_id=c.category_id
        LEFT JOIN product_details pd ON p.product_id=pd.product_id
        LEFT JOIN product_images pi  ON p.product_id=pi.product_id
        AND pi.is_active=1
        WHERE p.status='active' AND p.category_id=3         
        GROUP BY p.product_id
        ORDER BY p.product_id ASC
        LIMIT 5
    """)
 
    products=cursor.fetchall()
    cursor.close()
    return render_template('leather_watches.htm',products=products)    


@prod_bp.route('/metal_watches.htm')
def metal_watches():
    cursor=mysql.connection.cursor()
 
    cursor.execute(""" SELECT p.product_id,p.product_no,p.title,
            p.base_price,p.sale_price,p.status,c.name  AS category_name,
            pd.short_description,pi.image_url,pi.alt_text
        FROM products p
        LEFT JOIN categories c  ON p.category_id=c.category_id
        LEFT JOIN product_details pd ON p.product_id=pd.product_id
        LEFT JOIN product_images pi  ON p.product_id=pi.product_id
        AND pi.is_active=1
        WHERE p.status='active' AND p.category_id=2         
        GROUP BY p.product_id
        ORDER BY p.product_id ASC
        LIMIT 5
    """)
 
    products=cursor.fetchall()
    cursor.close()
    return render_template('metal_watches.htm',products=products)    


@prod_bp.route('/<int:id>',methods=['GET'])
def product_page(id):
    cursor=mysql.connection.cursor()
    
    cursor.execute("""
        SELECT p.product_id,p.product_no,p.title,p.category_id,p.stock_quantity,
               p.base_price,p.sale_price,p.status,c.name AS category_name,r.rating,r.comment, COUNT(r.review_id) AS total_rating,
               pd.short_description,pd.long_description,pi.image_url,pi.alt_text,
               pd.display_type,pd.display_size,pd.brightness_nits,pd.battery_life,pd.connectivity,
               pd.strap_material,pd.case_material,pd.water_resistance,pd.warranty_months,pd.weight
        FROM products p
        LEFT JOIN categories c ON p.category_id=c.category_id
        LEFT JOIN product_details pd ON p.product_id=pd.product_id
        LEFT JOIN product_images pi ON p.product_id=pi.product_id AND pi.is_active=1
        LEFT JOIN product_reviews r ON p.product_id=r.product_id
        WHERE p.status='active' AND p.product_id=%s 
        GROUP BY p.product_id,p.product_no,p.title,p.category_id,p.stock_quantity,
            p.base_price,p.sale_price,p.status,c.name,
            r.rating,r.comment,
            pd.short_description,pd.long_description,pi.image_url,pi.alt_text,
            pd.display_type,pd.display_size,pd.brightness_nits,pd.battery_life,
            pd.connectivity,pd.strap_material,pd.case_material,
            pd.water_resistance,pd.warranty_months,pd.weight""",(id,))
    product=cursor.fetchone()

    if not product:
        return render_template('404.htm'), 404


    rel_links=make_links(product)  

    cursor.execute("""
        SELECT p.product_id,p.title,p.base_price,p.sale_price,p.category_id,
               pi.image_url,pi.alt_text
        FROM products p
        LEFT JOIN product_images pi ON p.product_id=pi.product_id AND pi.is_active=1
        WHERE p.status='active' AND p.category_id=%s AND p.product_id != %s
        GROUP BY p.product_id
        ORDER BY RAND()
        LIMIT 4
    """, (product['category_id'],product['product_id']))
    relateds=cursor.fetchall()

    cursor.execute("""
        SELECT us.first_name,us.last_name,r.user_id,r.product_id,
               r.rating,r.comment,r.status,r.created_at
        FROM product_reviews r
        JOIN users us ON r.user_id=us.user_id
        WHERE r.status='approved' AND r.product_id=%s
    """,(id,))
    reviews=cursor.fetchall()

    cursor.close()

    return render_template('product_page.htm',product=product,
                           relateds=relateds,reviews=reviews,rel_links=rel_links)
       
    
   

@prod_bp.route('/all_products',methods=['GET'])
def all_products():
    cursor=mysql.connection.cursor()

    filters = build_product_filter(request, exclude_category=4)

    cursor.execute(f"""
        SELECT p.product_id,p.product_no,p.title,p.category_id,p.stock_quantity,
            p.base_price,p.sale_price,p.status,c.name AS category_name,
            pd.short_description,pd.long_description,pi.image_url,pi.alt_text,
            pd.display_type,pd.display_size,pd.brightness_nits,pd.battery_life,pd.connectivity,
            pd.strap_material,pd.case_material,pd.water_resistance,pd.warranty_months,pd.weight
        FROM products p
        LEFT JOIN categories c ON p.category_id=c.category_id
        LEFT JOIN product_details pd ON p.product_id=pd.product_id
        LEFT JOIN product_images pi ON p.product_id=pi.product_id
        AND pi.is_active=1
        WHERE {filters['where_str']}
        GROUP BY p.product_id
        ORDER BY {filters['order_clause']}
    """, filters['params'])
    products=cursor.fetchall()
    cursor.execute("SELECT category_id, name FROM categories WHERE is_active=1 AND category_id != 4")
    categories=cursor.fetchall()

    cursor.close()
    
    if not products:
        return render_template('404.htm'), 404
    
    return render_template('all_products.htm',products=products,categories=categories)


@prod_bp.route('/all_earbuds',methods=['GET'])
def all_earbuds():
    cursor=mysql.connection.cursor()
    cursor.execute("""
        SELECT p.product_id,p.product_no,p.title,p.category_id,p.stock_quantity,
            p.base_price,p.sale_price,p.status,c.name AS category_name,
            pd.short_description,pd.long_description,pi.image_url,pi.alt_text,
            pd.display_type,pd.display_size,pd.brightness_nits,pd.battery_life,pd.connectivity,
            pd.strap_material,pd.case_material,pd.water_resistance,pd.warranty_months,pd.weight
        FROM products p
        LEFT JOIN categories c ON p.category_id=c.category_id
        LEFT JOIN product_details pd ON p.product_id=pd.product_id
        LEFT JOIN product_images pi ON p.product_id=pi.product_id
        AND pi.is_active=1
        WHERE p.status='active' AND p.category_id=4
        ORDER BY RAND()
    """)
    products=cursor.fetchall()
    cursor.close()
    
    if not products:
        return render_template('404.htm'), 404
    
    return render_template('all_earbuds.htm',products=products)


@prod_bp.route('/mix_products',methods=['GET'])
def mix_products():
    cursor=mysql.connection.cursor()
    cursor.execute("""
        SELECT p.product_id,p.product_no,p.title,p.category_id,p.stock_quantity,
            p.base_price,p.sale_price,p.status,c.name AS category_name,
            pd.short_description,pd.long_description,pi.image_url,pi.alt_text,
            pd.display_type,pd.display_size,pd.brightness_nits,pd.battery_life,pd.connectivity,
            pd.strap_material,pd.case_material,pd.water_resistance,pd.warranty_months,pd.weight
        FROM products p
        LEFT JOIN categories c ON p.category_id=c.category_id
        LEFT JOIN product_details pd ON p.product_id=pd.product_id
        LEFT JOIN product_images pi ON p.product_id=pi.product_id
        AND pi.is_active=1
        WHERE p.status='active'
        ORDER BY RAND()
    """)
    products=cursor.fetchall()
    cursor.close()
    if not products:
        return render_template('404.htm'), 404
    
    return render_template('mix_products.htm',products=products)






@prod_bp.route('/search')
def search():
    q=request.args.get('q', '').strip()
    fmt=request.args.get('format', 'html')

    if not q:
        if fmt == 'json':
            return jsonify([])
        return render_template('all_products.htm',products=[],categories=[])

    cursor=mysql.connection.cursor()
    cursor.execute("""
    SELECT p.product_id,p.title,p.base_price,p.sale_price,
           pi.image_url,pi.alt_text,
           c.name AS category_name,
           pd.short_description
    FROM products p
    LEFT JOIN product_images pi 
        ON p.product_id=pi.product_id AND pi.is_active=1
    LEFT JOIN categories c 
        ON p.category_id=c.category_id
    LEFT JOIN product_details pd
        ON p.product_id=pd.product_id
    WHERE p.status='active'
    AND (p.title LIKE %s OR p.product_no LIKE %s)
    GROUP BY p.product_id
    LIMIT 20
    """, (f'%{q}%', f'%{q}%'))
    
    products=cursor.fetchall()
    cursor.close()

    if fmt == 'json':
        
        safe=[]
        for p in products:
            row = dict(p)
            if row.get('base_price') is not None:
                row['base_price'] = float(row['base_price'])
            if row.get('sale_price') is not None:
                row['sale_price'] = float(row['sale_price'])
            safe.append(row)
        return jsonify(safe)

    return render_template('all_products.htm',products=products,categories=[])

