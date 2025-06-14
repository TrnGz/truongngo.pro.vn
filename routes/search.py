from flask import Blueprint, render_template, request, flash
from utils.database import get_db_connection
from utils.helpers import getLoginDetails
import sqlite3

search_bp = Blueprint('search', __name__)

@search_bp.route('/search')
def search():
    search_query = request.args.get('searchQuery', '').strip()
    loggedIn, firstName, noOfItems = getLoginDetails()

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Fetch categories ordered by name for sidebar/filter navigation
            cursor.execute("SELECT categoryId, name FROM categories ORDER BY name")
            category_data = cursor.fetchall()

            if search_query:
                # Query products where name or description contains the search query and stock > 0
                cursor.execute("""
                    SELECT productId, name, price, description, image, stock
                    FROM products
                    WHERE (name LIKE ? OR description LIKE ?) AND stock > 0
                    ORDER BY name ASC
                """, (f'%{search_query}%', f'%{search_query}%'))

                products = cursor.fetchall()

                if not products:
                    flash(f'Không tìm thấy sản phẩm nào phù hợp với "{search_query}".', 'info')
            else:
                products = []
                flash("Vui lòng nhập từ khóa tìm kiếm!", "warning")

    except sqlite3.Error as e:
        print(f"Database error during search: {e}")
        flash("Lỗi cơ sở dữ liệu khi tìm kiếm. Vui lòng thử lại.", "error")
        products = []
        category_data = []

    # Render search results page with data and UI variables for elegant, minimal presentation
    return render_template(
        'search_results.html',
        itemData=products,
        loggedIn=loggedIn,
        firstName=firstName,
        noOfItems=noOfItems,
        categoryData=category_data,
        searchQuery=search_query,
        totalResults=len(products)
    )
