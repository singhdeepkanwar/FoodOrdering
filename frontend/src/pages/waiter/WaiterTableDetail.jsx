import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import toast from "react-hot-toast";
import { getWaiterTableDetail, waiterAddItems, waiterMarkServed } from "../../api";
import { ArrowLeft } from "lucide-react";

const STATUS_COLORS = {
  pending: "bg-yellow-100 text-yellow-700",
  confirmed: "bg-blue-100 text-blue-600",
  preparing: "bg-orange-100 text-orange-700",
  ready: "bg-green-100 text-green-700",
  served: "bg-gray-100 text-gray-500",
  cancelled: "bg-red-100 text-red-600",
};

const VEG = "border-green-600";
const NONVEG = "border-red-600";

export default function WaiterTableDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [cart, setCart] = useState({});
  const [specialInstructions, setSpecialInstructions] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [customerPhone, setCustomerPhone] = useState("");

  const load = () => getWaiterTableDetail(id).then(({ data }) => setData(data));
  useEffect(() => { load(); }, [id]);

  const addToCart = (item) => {
    setCart((c) => ({
      ...c,
      [item.id]: { ...item, qty: (c[item.id]?.qty || 0) + 1 },
    }));
  };

  const decFromCart = (itemId) => {
    setCart((c) => {
      const qty = (c[itemId]?.qty || 0) - 1;
      if (qty <= 0) { const n = { ...c }; delete n[itemId]; return n; }
      return { ...c, [itemId]: { ...c[itemId], qty } };
    });
  };

  const totalQty = Object.values(cart).reduce((s, i) => s + i.qty, 0);
  const totalAmount = Object.values(cart).reduce((s, i) => s + i.price * i.qty, 0);

  const handlePlaceOrder = async () => {
    if (!totalQty) return;
    const cartItems = Object.values(cart).map((i) => ({ id: i.id, qty: i.qty }));
    try {
      await waiterAddItems(id, {
        cart: cartItems,
        special_instructions: specialInstructions,
        customer_name: customerName,
        customer_phone: customerPhone,
      });
      toast.success("Order placed.");
      setCart({});
      setSpecialInstructions("");
      setCustomerName("");
      setCustomerPhone("");
      load();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to place order.");
    }
  };

  const handleMarkServed = async (orderId) => {
    try {
      await waiterMarkServed(orderId);
      toast.success("Marked as served.");
      load();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed.");
    }
  };

  if (!data) return <div className="min-h-screen bg-gray-100 p-6 text-sm text-gray-400">Loading…</div>;

  const { table, session, orders, categories } = data;

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm px-4 py-3 flex items-center justify-between sticky top-0 z-20">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/waiter")} className="text-gray-400 hover:text-gray-700">
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="font-bold text-gray-800">{table.name}</h1>
            {session ? (
              <p className="text-xs text-gray-400">{session.customer_name} · {session.customer_phone}</p>
            ) : (
              <p className="text-xs text-yellow-500 font-medium">Vacant — waiter can start an order</p>
            )}
          </div>
        </div>
        {session && (
          <div className="text-right">
            <p className="text-xs text-gray-500">Running bill</p>
            <p className="font-bold text-orange-600">₹{session.running_total}</p>
          </div>
        )}
      </header>

      <div className="p-4 max-w-3xl mx-auto grid md:grid-cols-2 gap-6">
        {/* Orders */}
        <div>
          <h2 className="font-semibold text-gray-700 mb-3">Current Orders</h2>
          {orders.length === 0 ? (
            <div className="bg-white rounded-xl p-8 text-center text-gray-400 shadow-sm">No orders yet.</div>
          ) : (
            orders.map((order) => (
              <div key={order.id} className="bg-white rounded-xl p-4 shadow-sm mb-3">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <span className="font-bold text-gray-800">#{order.id}</span>
                    <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${STATUS_COLORS[order.status] || ""}`}>
                      {order.status}
                    </span>
                  </div>
                  <span className="font-semibold text-gray-700">₹{order.total_amount}</span>
                </div>
                <ul className="text-sm text-gray-600 space-y-0.5 mb-3">
                  {order.items.map((item) => (
                    <li key={item.id}>{item.quantity}× {item.menu_item_name}</li>
                  ))}
                </ul>
                {order.status === "ready" ? (
                  <button onClick={() => handleMarkServed(order.id)}
                    className="w-full bg-green-500 hover:bg-green-600 text-white text-sm font-semibold py-2 rounded-lg">
                    Mark as Served ✓
                  </button>
                ) : order.status === "served" ? (
                  <p className="text-center text-xs text-gray-400 py-1">Served</p>
                ) : (
                  <p className="text-center text-xs text-gray-400 py-1">Kitchen is preparing…</p>
                )}
              </div>
            ))
          )}
        </div>

        {/* Add Items */}
        <div>
          <h2 className="font-semibold text-gray-700 mb-3">Add Items</h2>

          {totalQty > 0 && (
            <div className="bg-orange-50 border border-orange-200 rounded-xl p-3 mb-3 flex justify-between items-center">
              <span className="text-sm text-orange-700 font-medium">
                {totalQty} item(s) · ₹{totalAmount.toFixed(0)}
              </span>
              <button onClick={handlePlaceOrder}
                className="bg-orange-500 hover:bg-orange-600 text-white text-xs font-bold px-4 py-1.5 rounded-lg">
                Place Order
              </button>
            </div>
          )}

          {!session && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-3 mb-3 space-y-2">
              <p className="text-xs font-medium text-yellow-700">
                Table is vacant. A session will be created when you place the order.
              </p>
              <input type="text" placeholder="Customer name (optional)" value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
              <input type="tel" placeholder="Phone number (optional)" value={customerPhone}
                onChange={(e) => setCustomerPhone(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
            </div>
          )}

          <input type="text" placeholder="Special instructions" value={specialInstructions}
            onChange={(e) => setSpecialInstructions(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-orange-400" />

          {categories.map((cat) => (
            <div key={cat.id} className="bg-white rounded-xl shadow-sm mb-3 overflow-hidden">
              <p className="text-xs font-semibold text-gray-500 uppercase px-4 py-2 bg-gray-50">{cat.name}</p>
              {cat.items.filter((i) => i.is_available).map((item) => (
                <div key={item.id} className="flex items-center justify-between px-4 py-2 border-t">
                  <div className="flex items-center gap-2">
                    <span className={`inline-block w-2.5 h-2.5 rounded-sm border-2 ${item.is_veg ? VEG : NONVEG}`} />
                    <div>
                      <span className="text-sm text-gray-800">{item.name}</span>
                      <span className="text-xs text-gray-400 ml-1">₹{item.price}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {!cart[item.id] ? (
                      <button onClick={() => addToCart(item)}
                        className="text-xs bg-orange-500 hover:bg-orange-600 text-white px-3 py-1 rounded-full">
                        Add
                      </button>
                    ) : (
                      <div className="flex items-center gap-1">
                        <button onClick={() => decFromCart(item.id)}
                          className="w-6 h-6 rounded-full bg-gray-100 text-gray-600 text-sm flex items-center justify-center font-bold">
                          −
                        </button>
                        <span className="text-sm w-4 text-center">{cart[item.id].qty}</span>
                        <button onClick={() => addToCart(item)}
                          className="w-6 h-6 rounded-full bg-orange-500 text-white text-sm flex items-center justify-center font-bold">
                          +
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
