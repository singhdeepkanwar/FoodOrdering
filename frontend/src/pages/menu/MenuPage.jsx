import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import {
  getCategories, createCategory, updateCategory, deleteCategory,
  createItem, updateItem, deleteItem, toggleItem,
} from "../../api";
import { Plus, Pencil, Trash2, ToggleLeft, ToggleRight, X } from "lucide-react";

const VEG_DOT = "border-green-600";
const NONVEG_DOT = "border-red-600";

function CategoryModal({ initial, onSave, onClose }) {
  const [form, setForm] = useState(initial || { name: "", display_order: 0, is_active: true });
  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-xl">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold">{initial ? "Edit Category" : "New Category"}</h3>
          <button onClick={onClose}><X size={18} /></button>
        </div>
        <div className="space-y-3">
          <input placeholder="Category name" value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
          <input type="number" placeholder="Display order" value={form.display_order}
            onChange={(e) => setForm({ ...form, display_order: parseInt(e.target.value) || 0 })}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={form.is_active}
              onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />
            Active
          </label>
        </div>
        <div className="flex gap-2 mt-4">
          <button onClick={() => onSave(form)}
            className="flex-1 bg-orange-500 hover:bg-orange-600 text-white font-semibold py-2 rounded-lg text-sm">
            Save
          </button>
          <button onClick={onClose}
            className="flex-1 border py-2 rounded-lg text-sm hover:bg-gray-50">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

function ItemModal({ initial, categories, onSave, onClose }) {
  const [form, setForm] = useState(
    initial || {
      name: "", description: "", price: "", is_veg: true,
      is_available: true, display_order: 0,
      category: categories[0]?.id || "",
    }
  );
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold">{initial ? "Edit Item" : "New Item"}</h3>
          <button onClick={onClose}><X size={18} /></button>
        </div>
        <div className="space-y-3">
          <select value={form.category} onChange={set("category")}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400">
            {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <input placeholder="Item name" value={form.name} onChange={set("name")}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
          <textarea placeholder="Description" value={form.description} onChange={set("description")} rows={2}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
          <div className="grid grid-cols-2 gap-3">
            <input type="number" placeholder="Price (₹)" value={form.price} onChange={set("price")}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
            <input type="number" placeholder="Display order" value={form.display_order} onChange={set("display_order")}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
          </div>
          <div className="flex gap-4 text-sm">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={form.is_veg}
                onChange={(e) => setForm({ ...form, is_veg: e.target.checked })} />
              Veg
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={form.is_available}
                onChange={(e) => setForm({ ...form, is_available: e.target.checked })} />
              Available
            </label>
          </div>
        </div>
        <div className="flex gap-2 mt-4">
          <button onClick={() => onSave(form)}
            className="flex-1 bg-orange-500 hover:bg-orange-600 text-white font-semibold py-2 rounded-lg text-sm">
            Save
          </button>
          <button onClick={onClose}
            className="flex-1 border py-2 rounded-lg text-sm hover:bg-gray-50">
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default function MenuPage() {
  const [categories, setCategories] = useState([]);
  const [catModal, setCatModal] = useState(null); // null | "new" | category obj
  const [itemModal, setItemModal] = useState(null);

  const load = () => getCategories().then(({ data }) => setCategories(data));
  useEffect(() => { load(); }, []);

  const saveCat = async (form) => {
    try {
      if (catModal === "new") await createCategory(form);
      else await updateCategory(catModal.id, form);
      toast.success("Saved.");
      setCatModal(null);
      load();
    } catch { toast.error("Failed to save."); }
  };

  const deleteCat = async (id) => {
    if (!confirm("Delete this category and all its items?")) return;
    try { await deleteCategory(id); load(); }
    catch { toast.error("Failed to delete."); }
  };

  const saveItem = async (form) => {
    try {
      if (itemModal === "new") await createItem({ ...form, price: parseFloat(form.price) });
      else await updateItem(itemModal.id, { ...form, price: parseFloat(form.price) });
      toast.success("Saved.");
      setItemModal(null);
      load();
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to save.";
      toast.error(msg);
    }
  };

  const handleDeleteItem = async (id) => {
    if (!confirm("Delete this item?")) return;
    try { await deleteItem(id); load(); }
    catch { toast.error("Failed to delete."); }
  };

  const handleToggle = async (id) => {
    try { await toggleItem(id); load(); }
    catch { toast.error("Failed to toggle."); }
  };

  const allCats = categories.map((c) => ({ id: c.id, name: c.name }));

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-lg font-semibold">Menu</h2>
        <div className="flex gap-2">
          <button onClick={() => setCatModal("new")}
            className="flex items-center gap-1 text-sm border px-3 py-2 rounded-lg hover:bg-gray-50">
            <Plus size={14} /> Category
          </button>
          <button onClick={() => setItemModal("new")}
            className="flex items-center gap-1 text-sm bg-orange-500 hover:bg-orange-600 text-white px-3 py-2 rounded-lg">
            <Plus size={14} /> Item
          </button>
        </div>
      </div>

      {categories.map((cat) => (
        <div key={cat.id} className="bg-white rounded-xl shadow-sm mb-4 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-sm text-gray-700">{cat.name}</span>
              {!cat.is_active && (
                <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">Inactive</span>
              )}
            </div>
            <div className="flex gap-2">
              <button onClick={() => setCatModal(cat)} className="text-gray-400 hover:text-gray-700">
                <Pencil size={14} />
              </button>
              <button onClick={() => deleteCat(cat.id)} className="text-gray-400 hover:text-red-600">
                <Trash2 size={14} />
              </button>
            </div>
          </div>

          {cat.items.length === 0 ? (
            <p className="text-sm text-gray-400 px-4 py-3">No items.</p>
          ) : (
            cat.items.map((item) => (
              <div key={item.id} className="flex items-center justify-between px-4 py-2 border-b last:border-0">
                <div className="flex items-center gap-2">
                  <span className={`inline-block w-2.5 h-2.5 rounded-sm border-2 ${item.is_veg ? VEG_DOT : NONVEG_DOT}`} />
                  <div>
                    <span className="text-sm text-gray-800">{item.name}</span>
                    <span className="text-xs text-gray-400 ml-2">₹{item.price}</span>
                    {!item.is_available && (
                      <span className="text-xs text-red-500 ml-2">Unavailable</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => handleToggle(item.id)} className="text-gray-400 hover:text-orange-500">
                    {item.is_available ? <ToggleRight size={18} className="text-green-500" /> : <ToggleLeft size={18} />}
                  </button>
                  <button onClick={() => setItemModal(item)} className="text-gray-400 hover:text-gray-700">
                    <Pencil size={14} />
                  </button>
                  <button onClick={() => handleDeleteItem(item.id)} className="text-gray-400 hover:text-red-600">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      ))}

      {catModal && (
        <CategoryModal
          initial={catModal !== "new" ? catModal : null}
          onSave={saveCat}
          onClose={() => setCatModal(null)}
        />
      )}

      {itemModal && (
        <ItemModal
          initial={itemModal !== "new" ? itemModal : null}
          categories={allCats}
          onSave={saveItem}
          onClose={() => setItemModal(null)}
        />
      )}
    </div>
  );
}
