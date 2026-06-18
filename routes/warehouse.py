from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime

warehouse_bp = Blueprint(
    "warehouse",
    __name__
)

DB_NAME = "finance.db"


def get_conn():

    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn


# ====================================
# GET PRODUCTS
# ====================================

@warehouse_bp.route(
    "/api/products/<user_id>",
    methods=["GET"]
)
def get_products(user_id):

    conn = get_conn()

    products = conn.execute(
        """
        SELECT *
        FROM products
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    result = []

    for p in products:

        result.append({

            "id": p["id"],

            "name": p["name"],

            "category": p["category"],

            "quantity": p["quantity"],

            "buy_price": p["buy_price"],

            "sell_price": p["sell_price"],

            "barcode": p["barcode"],

            "created_at": p["created_at"]

        })

    return jsonify(result)


# ====================================
# ADD PRODUCT
# ====================================

@warehouse_bp.route(
    "/api/products",
    methods=["POST"]
)
def add_product():

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    name = data.get(
        "name",
        ""
    )

    category = data.get(
        "category",
        "Другое"
    )

    quantity = float(
        data.get(
            "quantity",
            0
        )
    )

    buy_price = float(
        data.get(
            "buy_price",
            0
        )
    )

    sell_price = float(
        data.get(
            "sell_price",
            0
        )
    )

    barcode = data.get(
        "barcode",
        ""
    )

    conn = get_conn()

    conn.execute(
        """
        INSERT INTO products
        (
            user_id,
            name,
            category,
            quantity,
            buy_price,
            sell_price,
            barcode,
            created_at
        )
        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            name,
            category,
            quantity,
            buy_price,
            sell_price,
            barcode,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })


# ====================================
# DELETE PRODUCT
# ====================================

@warehouse_bp.route(
    "/api/products/<int:product_id>",
    methods=["DELETE"]
)
def delete_product(product_id):

    data = request.json or {}

    user_id = str(
        data.get("user_id", "")
    )

    conn = get_conn()

    conn.execute(
        """
        DELETE FROM products
        WHERE id = ?
        AND user_id = ?
        """,
        (
            product_id,
            user_id
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })


# ====================================
# UPDATE PRODUCT
# ====================================

@warehouse_bp.route(
    "/api/products/<int:product_id>",
    methods=["PUT"]
)
def update_product(product_id):

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    conn = get_conn()

    conn.execute(
        """
        UPDATE products
        SET
            name = ?,
            category = ?,
            quantity = ?,
            buy_price = ?,
            sell_price = ?
        WHERE id = ?
        AND user_id = ?
        """,
        (
            data.get("name"),
            data.get("category"),
            data.get("quantity"),
            data.get("buy_price"),
            data.get("sell_price"),
            product_id,
            user_id
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })


# ====================================
# CHANGE STOCK
# ====================================

@warehouse_bp.route(
    "/api/products/<int:product_id>/stock",
    methods=["POST"]
)
def change_stock(product_id):

    data = request.json

    user_id = str(
        data.get("user_id")
    )

    qty = float(
        data.get(
            "quantity",
            0
        )
    )

    conn = get_conn()

    product = conn.execute(
        """
        SELECT quantity
        FROM products
        WHERE id = ?
        AND user_id = ?
        """,
        (
            product_id,
            user_id
        )
    ).fetchone()

    if not product:

        conn.close()

        return jsonify({
            "success": False
        }), 404

    current_qty = float(
        product["quantity"] or 0
    )

    new_qty = current_qty + qty

    if new_qty < 0:
        new_qty = 0

    conn.execute(
        """
        UPDATE products
        SET quantity = ?
        WHERE id = ?
        AND user_id = ?
        """,
        (
            new_qty,
            product_id,
            user_id
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })


# ====================================
# STATS
# ====================================

@warehouse_bp.route(
    "/api/warehouse/stats/<user_id>",
    methods=["GET"]
)
def warehouse_stats(user_id):

    conn = get_conn()

    products = conn.execute(
        """
        SELECT *
        FROM products
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    total_products = len(products)

    stock_value = 0

    profit_value = 0

    for p in products:

        qty = float(
            p["quantity"] or 0
        )

        buy_price = float(
            p["buy_price"] or 0
        )

        sell_price = float(
            p["sell_price"] or 0
        )

        stock_value += qty * buy_price

        profit_value += qty * (
            sell_price - buy_price
        )

    return jsonify({

        "total_products":
        total_products,

        "stock_value":
        round(stock_value, 2),

        "profit_value":
        round(profit_value, 2)

    })
