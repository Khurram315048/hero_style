from flask import render_template
from products import prod_bp
from utils.db import mysql



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


@prod_bp.route('/<int:id>', methods=['GET'])
def product_page(id):
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
        WHERE p.status='active' AND p.product_id=%s
        GROUP BY p.product_id
    """, (id,))
    product=cursor.fetchone()
    
    if not product:
        return render_template('404.htm'), 404
    
   
    cursor.execute("""
        SELECT p.product_id,p.title,p.base_price,p.sale_price,p.category_id,
            pi.image_url,pi.alt_text
        FROM products p
        LEFT JOIN product_images pi ON p.product_id=pi.product_id
        AND pi.is_active=1
        WHERE p.status='active' AND p.category_id=%s AND p.product_id!=%s
        GROUP BY p.product_id
        ORDER BY RAND()
        LIMIT 4
    """,(product['category_id'],product['product_id']))
    
    relateds=cursor.fetchall()
    cursor.close()
    
    return render_template('product_page.htm',product=product,relateds=relateds)




@prod_bp.route('/all_products',methods=['GET'])
def all_products():
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
    
    
    
    return render_template('all_products.htm',products=products)