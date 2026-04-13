import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { getTables, createTable, updateTable, deleteTable, regenerateQr } from "../../api";
import { Plus, Pencil, Trash2, QrCode, RefreshCw, X, Download } from "lucide-react";

function TableModal({ initial, onSave, onClose }) {
  const [form, setForm] = useState(initial || { name: "", is_active: true });
  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-xl">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-semibold">{initial ? "Edit Table" : "New Table"}</h3>
          <button onClick={onClose}><X size={18} /></button>
        </div>
        <div className="space-y-3">
          <input placeholder="Table name (e.g. Table 1)" value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
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

export default function TablesPage() {
  const [tables, setTables] = useState([]);
  const [modal, setModal] = useState(null);

  const load = () => getTables().then(({ data }) => setTables(data));
  useEffect(() => { load(); }, []);

  const save = async (form) => {
    try {
      if (modal === "new") await createTable(form);
      else await updateTable(modal.id, form);
      toast.success("Saved.");
      setModal(null);
      load();
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to save.";
      toast.error(msg);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this table?")) return;
    try { await deleteTable(id); load(); }
    catch { toast.error("Failed to delete."); }
  };

  const handleRegenQr = async (id) => {
    try {
      await regenerateQr(id);
      toast.success("QR code regenerated.");
      load();
    } catch { toast.error("Failed."); }
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-lg font-semibold">Tables & QR Codes</h2>
        <button onClick={() => setModal("new")}
          className="flex items-center gap-1 text-sm bg-orange-500 hover:bg-orange-600 text-white px-3 py-2 rounded-lg">
          <Plus size={14} /> Add Table
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {tables.map((table) => (
          <div key={table.id} className="bg-white rounded-xl shadow-sm p-4 flex flex-col items-center gap-3">
            {table.qr_image_url ? (
              <img src={table.qr_image_url} alt="QR" className="w-32 h-32 rounded" />
            ) : (
              <div className="w-32 h-32 bg-gray-100 rounded flex items-center justify-center">
                <QrCode size={40} className="text-gray-300" />
              </div>
            )}
            <div className="text-center">
              <p className="font-semibold text-gray-800 text-sm">{table.name}</p>
              {!table.is_active && (
                <span className="text-xs text-gray-400">Inactive</span>
              )}
            </div>
            <div className="flex gap-2 w-full">
              {table.qr_image_url && (
                <a href={table.qr_image_url} download={`qr_${table.name}.png`}
                  className="flex-1 flex items-center justify-center gap-1 text-xs border rounded-lg py-1.5 hover:bg-gray-50">
                  <Download size={12} /> QR
                </a>
              )}
              <button onClick={() => handleRegenQr(table.id)}
                className="flex-1 flex items-center justify-center gap-1 text-xs border rounded-lg py-1.5 hover:bg-gray-50">
                <RefreshCw size={12} /> Regen
              </button>
              <button onClick={() => setModal(table)}
                className="p-1.5 rounded-lg border hover:bg-gray-50 text-gray-500">
                <Pencil size={12} />
              </button>
              <button onClick={() => handleDelete(table.id)}
                className="p-1.5 rounded-lg border hover:bg-red-50 text-gray-500 hover:text-red-500">
                <Trash2 size={12} />
              </button>
            </div>
          </div>
        ))}
      </div>

      {modal && (
        <TableModal
          initial={modal !== "new" ? modal : null}
          onSave={save}
          onClose={() => setModal(null)}
        />
      )}
    </div>
  );
}
