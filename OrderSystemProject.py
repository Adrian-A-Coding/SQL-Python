import sqlite3


def viewingOrders(cursor):  # Displays the current orders in the system using the orders table
    cursor.execute('SELECT * FROM orders')
    results = cursor.fetchall()

    print("Here are all current orders:")
    for row in results:
        print("Order ID: {}, Order Number: {}, Customer Name: {}, Order Price: ${}"
              .format(row[0], row[1], row[2], row[3]))

    cursor.execute('SELECT * FROM customers')
    cResults = cursor.fetchall()
    print("Here are all customers who've ordered: ")
    for row in cResults:
        print("Customer ID: {}, Customer Name: {}".format(row[0], row[1]))


def addingToDB(idOrder, idCustomer, cursor,
               connection):  # Will allow the user to add information to the database which includes all tables, uses order object
    companyName, orderPrice, orderNum = (
    input("Enter your company's name: "), input("Enter the total price of your order: "),
    input("Verify your order number(i.e. 0-099): "))
    productList = []
    adding = "y"

    while adding != "n":
        products = input(
            "Enter your purchased product details seperated by comma as the name, price, and quantity: ").split(",")
        productList.append(products)
        adding = input("Would you like to add another product? (y/n): ")
    newOrder = Order(companyName, productList, orderPrice, idCustomer, idOrder, orderNum)

    cursor.execute('INSERT INTO customers VALUES (?, ?)', (newOrder.companyId, newOrder.company))
    cursor.execute('INSERT INTO orders VALUES (?, ?, ?, ?)',
                   (newOrder.orderId, newOrder.orderNum, newOrder.company, newOrder.totalPrice))
    for product in productList:
        cursor.execute('INSERT INTO products VALUES (?, ?, ?, ?)',
                       (product[0], product[1], product[2], newOrder.orderId))
    connection.commit()


def removeFromDB(cursor, connection):  # Opposite of preivous method also using the order object
    removeOrder = input("Enter the order ID you want to remove (i.e '1'): ")
    cursor.execute('DELETE FROM orders WHERE OrderID=' + removeOrder)
    cursor.execute('DELETE FROM products WHERE OrderID NOT IN (SELECT OrderID FROM orders)')
    cursor.execute('DELETE FROM customers WHERE CompanyName NOT IN (SELECT CompanyName FROM orders)')


class Order:
    def __init__(self, company, products, totalPrice, companyId, orderId, orderNum):
        self.company = company
        self.products = products  # Will need to be iterated over and inserted into the product table, should be dictionary
        self.totalPrice = totalPrice
        self.companyId = companyId
        self.orderId = orderId
        self.orderNum = orderNum


def main():
    conn = sqlite3.connect('OrderSystem.db')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS customers(CustomerID INTEGER NOT NULL, CompanyName TEXT NOT NULL, 
                Primary Key (CustomerID, CompanyName))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS orders(OrderID INTEGER NOT NULL PRIMARY KEY, OrderNumber TEXT, 
                CompanyName TEXT, OverallPrice DECIMAL(5,2), FOREIGN KEY (CompanyName) REFERENCES customers(CompanyName))''')
    cur.execute('''CREATE TABLE IF NOT EXISTS products(ProductName TEXT, Price DECIMAL(5,2), ProductAmount INT, 
                OrderID INTEGER, FOREIGN KEY (OrderID) REFERENCES orders(OrderID))''')
    conn.commit()

    cur.execute('SELECT * FROM orders ORDER BY OrderID DESC LIMIT 1')
    ids = cur.fetchone()
    if (ids is None):
        orderId = 0
    else:
        orderId = ids[0] + 1
    cur.execute('SELECT * FROM customers ORDER BY CustomerID DESC LIMIT 1')
    ids = cur.fetchone()
    if (ids is None):
        customerId = 0
    else:
        customerId = ids[0] + 1

    print("Welcome to the order system! What would you like to do with the current order table and its orders?")
    viewingOrders(cur)
    state = input(
        "Enter any selection regarding orders in the table: View(V), Add(A), Remove(R) or Exit(E) to leave: ").lower()
    while state != "e":
        match state:
            case "v":
                viewingOrders(cur)
            case "a":
                addingToDB(orderId, customerId, cur, conn)
            case "r":
                removeFromDB(cur, conn)
            case _:
                print("Please enter a valid selection.")
        state = input("Enter your next command; View(V), Add(A), Remove(R), Exit(E): ").lower()

    conn.commit()
    conn.close()


main()