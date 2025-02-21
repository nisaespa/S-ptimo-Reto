import json
import queue
from collections import namedtuple

# NamedTuple para representar ítems del menú
MenuItem = namedtuple("MenuItem", ["name", "price", "tax", "tip", "category"])

class Menu:
    def __init__(self, filename="menu.json"):
        self.filename = filename
        self.items = self.load_menu()
    
    def load_menu(self):
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_menu(self):
        with open(self.filename, "w") as file:
            json.dump(self.items, file, indent=4)
    
    def add_item(self, name, price, tax, tip, category):
        if name in self.items:
            raise ValueError(f"El ítem '{name}' ya existe en el menú.")
        self.items[name] = {"price": price, "tax": tax, "tip": tip, "category": category}
        self.save_menu()
    
    def update_item(self, name, price=None, tax=None, tip=None, category=None):
        if name not in self.items:
            raise KeyError(f"El ítem '{name}' no está en el menú.")
        if price is not None:
            self.items[name]["price"] = price
        if tax is not None:
            self.items[name]["tax"] = tax
        if tip is not None:
            self.items[name]["tip"] = tip
        if category is not None:
            self.items[name]["category"] = category
        self.save_menu()
    
    def delete_item(self, name):
        if name not in self.items:
            raise KeyError(f"El ítem '{name}' no existe en el menú.")
        del self.items[name]
        self.save_menu()

    def get_item(self, name):
        if name not in self.items:
            raise KeyError(f"El ítem '{name}' no está en el menú.")
        data = self.items[name]
        return MenuItem(name, data["price"], data["tax"], data["tip"], data["category"])


class Order:
    def __init__(self):
        self.orders = queue.Queue()  # FIFO para manejar múltiples órdenes
    
    def create_order(self):
        return []  # Retorna una nueva lista de ítems para la orden
    
    def add_item_to_order(self, order, item):
        if not isinstance(item, MenuItem):
            raise TypeError("Error: El ítem agregado no es válido.")
        order.append(item)

    def queue_order(self, order):
        if not order:
            raise ValueError("No se puede agregar una orden vacía a la cola.")
        self.orders.put(order)

    def process_next_order(self):
        if self.orders.empty():
            print("No hay órdenes pendientes.")
            return
        order = self.orders.get()
        print("Procesando orden:")
        self.print_invoice(order)

    def calculate_total(self, order):
        if not order:
            return 0
        
        main_course_ordered = any(item.category == "Main Course" for item in order)
        total = 0
        for item in order:
            item_total = item.price + (item.price * item.tax) + (item.price * item.tip)
            if item.category == "Drink" and main_course_ordered:
                item_total *= 0.9  # 10% de descuento en bebidas si hay un plato principal
            total += item_total
        return total

    def print_invoice(self, order):
        if not order:
            print("Orden vacía.")
            return
        for item in order:
            print(f"{item.name} - ${item.price:.2f}")
        print(f"Total: ${self.calculate_total(order):.2f}")

class Payment:
    def __init__(self, total, method):
        self.total = total
        self.method = method
    
    def process_payment(self):
        raise NotImplementedError("Este método debe ser implementado en las subclases.")

class CashPayment(Payment):
    def __init__(self, total, cash_received):
        super().__init__(total, "Cash")
        self.cash_received = cash_received
    
    def process_payment(self):
        if self.cash_received < self.total:
            raise ValueError("El efectivo recibido no es suficiente para pagar la cuenta.")
        return self.cash_received - self.total

class CardPayment(Payment):
    def __init__(self, total, card_number, exp_date, cvv):
        super().__init__(total, "Card")
        self.card_number = card_number
        self.exp_date = exp_date
        self.cvv = cvv
    
    def process_payment(self):
        # Simulación de validación de tarjeta
        if len(self.card_number) < 12 or len(self.cvv) != 3:
            raise ValueError("Datos de tarjeta inválidos.")
        return True

# Ejemplo de uso
order_system = Order()
menu = Menu()

# Agregar ítems al menú
menu.add_item("Spaghetti", 50000, 0.07, 0.1, "Main Course")
menu.add_item("Lemonade", 10000, 0.07, 0.1, "Drink")
menu.add_item("Chocolate Cake", 20000, 0.07, 0.1, "Dessert")

# Crear órdenes
order1 = order_system.create_order()
order_system.add_item_to_order(order1, menu.get_item("Spaghetti"))
order_system.add_item_to_order(order1, menu.get_item("Lemonade"))
order_system.queue_order(order1)

order2 = order_system.create_order()
order_system.add_item_to_order(order2, menu.get_item("Chocolate Cake"))
order_system.queue_order(order2)

# Procesar órdenes
while not order_system.orders.empty():
    order_system.process_next_order()
    print()