import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getWaiterTables } from "../../api";
import { useAuth } from "../../contexts/AuthContext";
import { LogOut, ChevronRight } from "lucide-react";

export default function WaiterTables() {
  const [tables, setTables] = useState([]);
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    getWaiterTables().then(({ data }) => setTables(data));
  }, []);

  const handleLogout = () => { logout(); navigate("/login"); };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm px-6 py-4 flex items-center justify-between sticky top-0 z-10">
        <h1 className="font-bold text-orange-600 text-lg">Waiter — Tables</h1>
        <button onClick={handleLogout}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-red-600">
          <LogOut size={14} /> Logout
        </button>
      </header>

      <div className="p-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {tables.map(({ table, session, pending_orders }) => (
          <button
            key={table.id}
            onClick={() => navigate(`/waiter/table/${table.id}`)}
            className="bg-white rounded-xl p-4 shadow-sm text-left hover:shadow-md transition-shadow flex flex-col gap-2"
          >
            <div className="flex justify-between items-start">
              <span className="font-bold text-gray-800">{table.name}</span>
              <ChevronRight size={16} className="text-gray-400" />
            </div>

            {session ? (
              <div>
                <p className="text-sm text-gray-700">{session.customer_name}</p>
                <p className="text-xs text-gray-400">{session.customer_phone}</p>
                <p className="text-xs text-orange-600 font-medium mt-1">Running: ₹{session.running_total}</p>
              </div>
            ) : (
              <p className="text-xs text-gray-400">Vacant</p>
            )}

            {pending_orders > 0 && (
              <span className="text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded-full self-start">
                {pending_orders} pending
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
