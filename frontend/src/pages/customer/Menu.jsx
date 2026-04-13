import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import { getCustomerMenu, getCustomerSession, customerPlaceOrder } from "../../api";
import { ShoppingCart, X, FileText, User } from "lucide-react";

const VEG = "border-green-600";
const NONVEG = "border-red-600";

const STATUS_COLORS = {
  pending: "bg-yellow-100 text-yellow-700",
  confirmed: "bg-blue-100 text-blue-600",
  preparing: "bg-orange-100 text-orange-700",
  ready: "bg-green-100 text-green-700",
  served: "bg-gray-100 text-gray-500",
  cancelled: "bg-red-100 text-red-600",
};

export default function CustomerMenu() {
  const { qrToken } = useParams();
  const navigate = useNavigate();

  const [menuData, setMenuData] = useState(null);
  const [session, setSession] = useState(null);
  const [cart, setCart] = useState({});
  const [specialInstructions, setSpecialInstructions] = useState("");
  const [vegOnly, setVegOnly] = useState(false);
  const [showCart, setShowCart] = useState(false);
  const [showBill, setShowBill] = useState(false);
  const [showGuestModal, setShowGuestModal] = useState(false);
  const [guestName, setGuestName] = useState("");
  const [guestPhone, setGuestPhone] = useState("");
  const [placing, setPlacing] = useState(false);

  useEffect(() => {
    getCustomerMenu(qrToken)
      .then(({ data }) => setMenuData(data))
      .catch(() => toast.error("Table not found or restaurant is closed."));

    const sid = localStorage.getItem(`session_${qrToken}`);
    if (sid) {
      getCustomerSession(qrToken)
        .then(({ data }) => setSession(data))
        .catch(() => localStorage.removeItem(`session_${qrToken}`));
    }
  }, [qrToken]);

  const addToCart = (item) =>
    setCart((c) => ({ ...c, [item.id]: { ...item, qty: (c[item.id]?.qty || 0) + 1 } }));

  const dec = (id) =>
    setCart((c) => {
      const qty = (c[id]?.qty || 0) - 1;
      if (qty <= 0) { const n = { ...c }; delete n[id]; return n; }
      return { ...c, [id]: { ...c[id], qty } };
    });

  const totalQty = Object.values(cart).reduce((s, i) => s + i.qty, 0);
  const totalAmount = Object.values(cart).reduce((s, i) => s + parseFloat(i.price) * i.qty, 0);

  // Called from cart drawer "Place Order" button
  const handlePlaceOrderClick = () => {
    if (!totalQty) return;
    const sid = localStorage.getItem(`session_${qrToken}`);
    if (sid) {
      submitOrder(null, null); // already have a session
    } else {
      setShowCart(false);
      setShowGuestModal(true); // ask optional name/phone
    }
  };

  const submitOrder = async (name, phone) => {
    setPlacing(true);
    try {
      const cartItems = Object.values(cart).map((i) => ({ id: i.id, qty: i.qty }));
      const sid = localStorage.getItem(`session_${qrToken}`);
      const payload = {
        cart: cartItems,
        special_instructions: specialInstructions,
        ...(sid ? {} : {
          customer_name: name || "",
          customer_phone: phone || "",
        }),
      };
      const { data } = await customerPlaceOrder(qrToken, payload);

      // Save session_id returned by backend if it's new
      if (data.session_id && !sid) {
        localStorage.setItem(`session_${qrToken}`, data.session_id);
      }

      setCart({});
      setSpecialInstructions("");
      setShowGuestModal(false);
      toast.success("Order placed!");
      navigate(`/t/${qrToken}/confirmation/${data.id}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to place order.");
    } finally {
      setPlacing(false);
    }
  };

  if (!menuData) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center text-sm text-gray-400">
      Loading menu…
    </div>
  );

  const { restaurant, categories } = menuData;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm px-4 py-3 sticky top-0 z-20 flex items-center justify-between">
        <div>
          <h1 className="font-bold text-gray-800">{restaurant.name}</h1>
          {session
            ? <p className="text-xs text-gray-500">Hi, {session.customer_name}</p>
            : <p className="text-xs text-gray-400">{menuData.table.name}</p>
          }
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setShowBill(true)}
            className="relative flex items-center gap-1 text-sm text-gray-600 border px-3 py-1.5 rounded-lg hover:bg-gray-50">
            <FileText size={14} />
            <span className="text-xs">Bill</span>
            {session?.orders?.length > 0 && (
              <span className="absolute -top-1.5 -right-1.5 bg-orange-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                {session.orders.length}
              </span>
            )}
          </button>
          <button onClick={() => setShowCart(true)}
            className="relative flex items-center gap-1 text-sm bg-orange-500 text-white px-3 py-1.5 rounded-lg">
            <ShoppingCart size={14} />
            {totalQty > 0 && (
              <span className="absolute -top-1.5 -right-1.5 bg-white text-orange-600 border border-orange-200 text-xs rounded-full w-4 h-4 flex items-center justify-center font-bold">
                {totalQty}
              </span>
            )}
          </button>
        </div>
      </header>

      {/* Veg filter */}
      <div className="px-4 py-2 flex items-center gap-2">
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input type="checkbox" checked={vegOnly} onChange={(e) => setVegOnly(e.target.checked)} className="accent-green-600" />
          <span className="text-gray-600">Veg only</span>
        </label>
      </div>

      {/* Categories */}
      <div className="px-4 pb-24">
        {categories.map((cat) => {
          const items = cat.items.filter((i) => !vegOnly || i.is_veg);
          if (!items.length) return null;
          return (
            <div key={cat.id} className="mb-4">
              <h2 className="text-xs font-bold text-gray-500 uppercase mb-2">{cat.name}</h2>
              {items.map((item) => (
                <div key={item.id}
                  className="bg-white rounded-xl p-3 mb-2 flex items-center justify-between shadow-sm">
                  <div className="flex items-start gap-2 flex-1 min-w-0">
                    <span className={`mt-1 inline-block w-3 h-3 rounded-sm border-2 flex-shrink-0 ${item.is_veg ? VEG : NONVEG}`} />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">{item.name}</p>
                      {item.description && (
                        <p className="text-xs text-gray-400 truncate">{item.description}</p>
                      )}
                      <p className="text-sm font-semibold text-gray-700 mt-0.5">₹{item.price}</p>
                    </div>
                  </div>
                  <div className="ml-3 flex-shrink-0">
                    {!cart[item.id] ? (
                      <button onClick={() => addToCart(item)}
                        className="text-xs bg-orange-500 hover:bg-orange-600 text-white px-3 py-1.5 rounded-full font-medium">
                        Add
                      </button>
                    ) : (
                      <div className="flex items-center gap-1">
                        <button onClick={() => dec(item.id)}
                          className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 font-bold">−</button>
                        <span className="text-sm w-5 text-center font-medium">{cart[item.id].qty}</span>
                        <button onClick={() => addToCart(item)}
                          className="w-7 h-7 rounded-full bg-orange-500 flex items-center justify-center text-white font-bold">+</button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          );
        })}
      </div>

      {/* Cart Drawer */}
      {showCart && (
        <div className="fixed inset-0 z-40 flex justify-end">
          <div className="absolute inset-0 bg-black/30" onClick={() => setShowCart(false)} />
          <div className="relative bg-white w-full max-w-sm h-full flex flex-col shadow-xl">
            <div className="flex items-center justify-between px-4 py-3 border-b">
              <h2 className="font-semibold">Your Cart</h2>
              <button onClick={() => setShowCart(false)}><X size={18} /></button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {Object.values(cart).length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-6">Cart is empty.</p>
              ) : (
                Object.values(cart).map((item) => (
                  <div key={item.id} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{item.name}</span>
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-1">
                        <button onClick={() => dec(item.id)}
                          className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 font-bold text-sm">−</button>
                        <span className="text-sm w-4 text-center">{item.qty}</span>
                        <button onClick={() => addToCart(item)}
                          className="w-6 h-6 rounded-full bg-orange-500 flex items-center justify-center text-white font-bold text-sm">+</button>
                      </div>
                      <span className="text-sm font-medium w-14 text-right">₹{(parseFloat(item.price) * item.qty).toFixed(0)}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
            {Object.values(cart).length > 0 && (
              <div className="p-4 border-t space-y-3">
                <input type="text" placeholder="Special instructions (optional)"
                  value={specialInstructions}
                  onChange={(e) => setSpecialInstructions(e.target.value)}
                  className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
                <div className="flex items-center justify-between text-sm font-medium">
                  <span>Total</span>
                  <span>₹{totalAmount.toFixed(0)}</span>
                </div>
                <button onClick={handlePlaceOrderClick} disabled={placing}
                  className="w-full bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white font-semibold py-3 rounded-xl text-sm">
                  {placing ? "Placing order…" : "Place Order"}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Guest Info Modal */}
      {showGuestModal && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
          <div className="absolute inset-0 bg-black/40" onClick={() => setShowGuestModal(false)} />
          <div className="relative bg-white w-full max-w-sm rounded-t-2xl sm:rounded-2xl p-6 shadow-xl">
            <div className="flex items-center gap-2 mb-1">
              <User size={18} className="text-orange-500" />
              <h2 className="font-semibold text-gray-800">Who's ordering?</h2>
            </div>
            <p className="text-xs text-gray-400 mb-4">Optional — helps us call out your order</p>
            <div className="space-y-3">
              <input
                type="text"
                placeholder="Your name (optional)"
                value={guestName}
                onChange={(e) => setGuestName(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
              />
              <input
                type="tel"
                placeholder="Phone number (optional)"
                value={guestPhone}
                onChange={(e) => setGuestPhone(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
              />
              <button
                onClick={() => submitOrder(guestName, guestPhone)}
                disabled={placing}
                className="w-full bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white font-semibold py-3 rounded-xl text-sm"
              >
                {placing ? "Placing order…" : "Confirm Order"}
              </button>
              <button
                onClick={() => submitOrder("", "")}
                disabled={placing}
                className="w-full text-sm text-gray-400 hover:text-gray-600 py-1"
              >
                Skip & order as guest
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bill Drawer */}
      {showBill && (
        <div className="fixed inset-0 z-40 flex justify-end">
          <div className="absolute inset-0 bg-black/30" onClick={() => setShowBill(false)} />
          <div className="relative bg-white w-full max-w-sm h-full flex flex-col shadow-xl">
            <div className="flex items-center justify-between px-4 py-3 border-b">
              <h2 className="font-semibold">My Bill</h2>
              <button onClick={() => setShowBill(false)}><X size={18} /></button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {!session?.orders?.length ? (
                <p className="text-sm text-gray-400 text-center py-6">No orders yet.</p>
              ) : (
                session.orders.map((order) => (
                  <div key={order.id} className="mb-3 bg-gray-50 rounded-xl p-3">
                    <div className="flex justify-between items-center mb-2">
                      <div>
                        <span className="font-bold text-sm">#{order.id}</span>
                        <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[order.status] || ""}`}>
                          {order.status}
                        </span>
                      </div>
                      <span className="text-sm font-medium">₹{order.total_amount}</span>
                    </div>
                    <ul className="text-sm text-gray-600 space-y-0.5">
                      {order.items.map((item) => (
                        <li key={item.id}>{item.quantity}× {item.menu_item_name}</li>
                      ))}
                    </ul>
                  </div>
                ))
              )}
            </div>
            {session && (
              <div className="p-4 border-t">
                <div className="flex justify-between font-bold">
                  <span>Running Total</span>
                  <span className="text-orange-600">₹{session.running_total}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
