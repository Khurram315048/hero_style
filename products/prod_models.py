import math
import random
import re
import MySQLdb.cursors
from utils.db import mysql
from utils.product_filter import build_product_filter



_ALL_IMAGES_SUBQ="""(SELECT GROUP_CONCAT(image_url ORDER BY image_id ASC SEPARATOR '|||')
    FROM product_images
    WHERE product_id=p.product_id AND is_active=1
) AS all_images"""

_FIRST_IMAGE_SUBQ="""(SELECT image_url FROM product_images
    WHERE product_id=p.product_id AND is_active=1
    ORDER BY image_id ASC LIMIT 1
) AS image_url"""

_FIRST_ALT_SUBQ="""(SELECT alt_text FROM product_images
    WHERE product_id=p.product_id AND is_active=1
    ORDER BY image_id ASC LIMIT 1
) AS alt_text"""



def get_page_offset(request, per_page=10):
    
    page=request.args.get('page',1,type=int)
    if page < 1:
        page=1

    offset=(page - 1) * per_page
    return page,per_page,offset




def _get_category_products(category_id,page,per_page,offset):

    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute(f"""
            SELECT p.product_id,p.title,p.base_price,p.sale_price,p.status,
                c.name AS category_name,
                pd.short_description,
                COUNT(DISTINCT r.review_id) AS rating,
                {_ALL_IMAGES_SUBQ},
                {_FIRST_IMAGE_SUBQ},
                {_FIRST_ALT_SUBQ}
            FROM products p
            LEFT JOIN categories c ON p.category_id=c.category_id
            LEFT JOIN product_details pd ON p.product_id=pd.product_id
            LEFT JOIN product_reviews r ON p.product_id=r.product_id
            WHERE p.status='active' AND p.category_id=%s
            GROUP BY p.product_id
            ORDER BY p.product_id
            LIMIT %s OFFSET %s
        """,(category_id,per_page,offset))
        products=list(cursor.fetchall())
        random.shuffle(products)

        cursor.execute("""
            SELECT COUNT(product_id) AS total_count
            FROM products
            WHERE category_id=%s AND status='active'
        """, (category_id,))
        total_rows=cursor.fetchone()['total_count']
        total_pages=math.ceil(total_rows / per_page)

        return products,total_pages
    finally:
        cursor.close()


def get_smart_watches(request):
    
    page,per_page,offset=get_page_offset(request)
    products,total_pages=_get_category_products(1,page,per_page,offset)
    return products,page,total_pages


def get_leather_watches(request):
    
    page,per_page,offset=get_page_offset(request)
    products,total_pages=_get_category_products(3,page,per_page,offset)
    return products, page, total_pages


def get_metal_watches(request):
    """Model for /metal_watches (category_id=2)."""
    page,per_page,offset=get_page_offset(request)
    products,total_pages=_get_category_products(2,page,per_page,offset)
    return products,page,total_pages




def get_all_products(request):
   
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        filters=build_product_filter(request,exclude_category=4)
        page,per_page,offset=get_page_offset(request)

        cursor.execute(f"""
            SELECT p.product_id,p.product_no,p.title,p.category_id,p.stock_quantity,
                p.base_price,p.sale_price,p.status,c.name AS category_name,
                pd.short_description,pd.long_description,
                {_ALL_IMAGES_SUBQ},
                {_FIRST_IMAGE_SUBQ},
                {_FIRST_ALT_SUBQ},
                pd.display_type,pd.display_size,pd.brightness_nits,pd.battery_life,
                pd.connectivity, pd.strap_material,pd.case_material,pd.water_resistance,
                pd.warranty_months, pd.weight,
                COUNT(r.review_id) AS rating
            FROM products p
            LEFT JOIN categories c ON p.category_id=c.category_id
            LEFT JOIN product_details pd ON p.product_id=pd.product_id
            LEFT JOIN product_reviews r ON p.product_id=r.product_id
            WHERE {filters['where_str']}
            GROUP BY p.product_id
            ORDER BY {filters['order_clause']}
            LIMIT %s OFFSET %s
        """,filters['params'] + [per_page, offset])
        products=cursor.fetchall()

        if not products:
            return None

        cursor.execute("SELECT category_id,name FROM categories WHERE is_active=1 AND category_id !=4")
        categories=cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(product_id) AS total_count
            FROM products
            WHERE status='active' AND category_id != 4
        """)
        total_rows=cursor.fetchone()['total_count']
        total_pages=math.ceil(total_rows / per_page)

        return products,categories,page,total_pages
    finally:
        cursor.close()




def get_all_earbuds(request):
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        page,per_page,offset=get_page_offset(request)

        cursor.execute("""
            SELECT p.product_id,p.product_no,p.title,p.category_id,p.stock_quantity,
                p.base_price,p.sale_price,p.status,c.name AS category_name,
                pd.short_description,pd.long_description,
                (SELECT GROUP_CONCAT(image_url ORDER BY image_id ASC SEPARATOR '|||')
                    FROM product_images WHERE product_id=p.product_id AND is_active=1
                ) AS all_images,
                (SELECT image_url FROM product_images
                    WHERE product_id=p.product_id AND is_active=1 ORDER BY image_id ASC LIMIT 1
                ) AS image_url,
                (SELECT alt_text FROM product_images
                    WHERE product_id=p.product_id AND is_active=1 ORDER BY image_id ASC LIMIT 1
                ) AS alt_text,
                pd.display_type,pd.display_size,pd.brightness_nits,pd.battery_life,
                pd.connectivity,pd.strap_material,pd.case_material,pd.water_resistance,
                pd.warranty_months,pd.weight,
                COUNT(DISTINCT r.review_id) AS rating
            FROM products p
            LEFT JOIN categories c ON p.category_id=c.category_id
            LEFT JOIN product_details pd ON p.product_id=pd.product_id
            LEFT JOIN product_reviews r ON p.product_id=r.product_id
            WHERE p.status='active' AND p.category_id=4
            GROUP BY p.product_id
            ORDER BY p.product_id
            LIMIT %s OFFSET %s
        """,(per_page,offset))
        products=list(cursor.fetchall())
        random.shuffle(products)

        if not products:
            return None

        cursor.execute("""
            SELECT COUNT(product_id) AS total_count
            FROM products
            WHERE category_id=4 AND status='active'
        """)
        total_rows=cursor.fetchone()['total_count']
        total_pages=math.ceil(total_rows / per_page)

        return products,page,total_pages
    finally:
        cursor.close()




def get_mix_products(request):
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        filters=build_product_filter(request)
        page,per_page,offset=get_page_offset(request)

        cursor.execute(f"""
            SELECT p.product_id,p.product_no,p.title,p.category_id,p.stock_quantity,
                p.base_price,p.sale_price,p.status,c.name AS category_name,
                pd.short_description,pd.long_description,
                (SELECT GROUP_CONCAT(image_url ORDER BY image_id ASC SEPARATOR '|||')
                    FROM product_images WHERE product_id=p.product_id AND is_active=1
                ) AS all_images,
                (SELECT image_url FROM product_images
                    WHERE product_id=p.product_id AND is_active=1 ORDER BY image_id ASC LIMIT 1
                ) AS image_url,
                (SELECT alt_text FROM product_images
                    WHERE product_id=p.product_id AND is_active=1 ORDER BY image_id ASC LIMIT 1
                ) AS alt_text,
                pd.display_type,pd.display_size,pd.brightness_nits,pd.battery_life,
                pd.connectivity, pd.strap_material,pd.case_material,pd.water_resistance,
                pd.warranty_months,pd.weight,
                COUNT(r.review_id) AS rating
            FROM products p
            LEFT JOIN categories c ON p.category_id=c.category_id
            LEFT JOIN product_details pd ON p.product_id=pd.product_id
            LEFT JOIN product_reviews r ON p.product_id=r.product_id
            WHERE {filters['where_str']}
            GROUP BY p.product_id
            ORDER BY {filters['order_clause']}
            LIMIT %s OFFSET %s
        """,filters['params'] + [per_page, offset])
        products=cursor.fetchall()

        if not products:
            return None

    
        cursor.execute("SELECT COUNT(product_id) AS total_count FROM products WHERE status='active'")
        total_rows=cursor.fetchone()['total_count']
        total_pages=math.ceil(total_rows / per_page)

        return products,page,total_pages
    finally:
        cursor.close()




def search_products(q):
    if not q:
        return []

    
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""
            SELECT p.product_id,p.title,p.base_price,p.sale_price,
                pi.image_url,pi.alt_text,c.name AS category_name,
                pd.short_description
            FROM products p
            LEFT JOIN product_images pi ON p.product_id=pi.product_id AND pi.is_active=1
            LEFT JOIN categories c ON p.category_id=c.category_id
            LEFT JOIN product_details pd ON p.product_id=pd.product_id
            WHERE p.status='active'
            AND (
                p.title LIKE %s OR
                p.product_no LIKE %s OR
                c.name LIKE %s OR
                pd.short_description LIKE %s
            )
            GROUP BY p.product_id
            ORDER BY
                CASE
                    WHEN p.title LIKE %s THEN 1
                    WHEN c.name LIKE %s THEN 2
                    WHEN p.product_no LIKE %s THEN 3
                    ELSE 4
                END
            LIMIT 20
        """,(f'%{q}%',f'%{q}%',f'%{q}%',f'%{q}%',
              f'%{q}%',f'%{q}%',f'%{q}%'))

        products=cursor.fetchall()

       
        safe=[]
        for row in products:
            row=dict(row)
            if row.get('base_price') is not None:
                row['base_price']=float(row['base_price'])

            if row.get('sale_price') is not None:
                row['sale_price']=float(row['sale_price'])
            safe.append(row)

        return safe
    finally:
        cursor.close()




def get_product_by_slug(slug):

    match=re.search(r'-(\d+)$', slug)
    if not match:
        return None

    product_id=int(match.group(1))
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("""
            SELECT p.product_id,p.product_no,p.title,p.category_id,p.stock_quantity,
                p.base_price,p.sale_price,p.status,c.name AS category_name,
                pd.short_description,pd.long_description,pi.image_url,pi.alt_text,
                pd.display_type,pd.display_size,pd.brightness_nits,pd.battery_life,
                pd.connectivity,pd.strap_material,pd.case_material,pd.water_resistance,
                pd.warranty_months,pd.weight,
                COUNT(r.review_id) AS total_rating
            FROM products p
            LEFT JOIN categories c ON p.category_id=c.category_id
            LEFT JOIN product_details pd ON p.product_id=pd.product_id
            LEFT JOIN product_images pi ON p.product_id=pi.product_id AND pi.is_active=1
            LEFT JOIN product_reviews r ON p.product_id=r.product_id
            WHERE p.status='active' AND p.product_id=%s
            GROUP BY p.product_id,p.product_no,p.title,p.category_id,p.stock_quantity,
                p.base_price,p.sale_price,p.status,c.name,
                pd.short_description,pd.long_description,pi.image_url,pi.alt_text,
                pd.display_type,pd.display_size,pd.brightness_nits,pd.battery_life,
                pd.connectivity,pd.strap_material,pd.case_material,pd.water_resistance,
                pd.warranty_months,pd.weight
        """,(product_id,))
        product=cursor.fetchone()

        if not product:
            return None

        
        cursor.execute("""
            SELECT image_url,alt_text
            FROM product_images
            WHERE product_id=%s AND is_active=1
            ORDER BY image_id ASC
        """,(product_id,))
        product_images=cursor.fetchall()

    
        cursor.execute("""
            SELECT p.product_id,p.title,p.base_price,p.sale_price,p.category_id,
                pi.image_url,pi.alt_text,
                (SELECT GROUP_CONCAT(image_url ORDER BY image_id ASC SEPARATOR '|||')
                    FROM product_images WHERE product_id=p.product_id AND is_active=1
                ) AS all_images
            FROM products p
            LEFT JOIN product_images pi ON p.product_id=pi.product_id AND pi.is_active=1
            WHERE p.status='active' AND p.category_id=%s AND p.product_id !=%s
            GROUP BY p.product_id
            ORDER BY p.product_id
            LIMIT 4
        """,(product['category_id'], product_id))
        relateds=list(cursor.fetchall())
        random.shuffle(relateds)

        cursor.execute("""
            SELECT us.first_name,us.last_name,r.user_id,r.product_id,
                r.rating,r.comment,r.status,r.created_at
            FROM product_reviews r
            JOIN users us ON r.user_id=us.user_id
            WHERE r.status='approved' AND r.product_id=%s
        """, (product_id,))
        reviews=cursor.fetchall()

        return product, product_images, relateds, reviews
    finally:
        cursor.close()