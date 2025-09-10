from .expense import ExpenseBase, ExpenseCreate, ExpenseUpdate, ExpenseOut
from .order import OrderBase, OrderCreate, OrderUpdate, OrderOut
from .user import UserLogin

# Ana dosyalarda "LoginRequest" olarak kullanmak istersen alias
LoginRequest = UserLogin