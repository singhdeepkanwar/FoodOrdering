import api from "./axios";

// ── Auth ──────────────────────────────────────────────────────────────────────
export const login = (username, password) =>
  api.post("/auth/token/", { username, password });

export const register = (data) => api.post("/auth/register/", data);

export const getMe = () => api.get("/auth/me/");

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const getDashboard = () => api.get("/dashboard/");

// ── Menu ──────────────────────────────────────────────────────────────────────
export const getCategories = () => api.get("/menu/categories/");
export const createCategory = (data) => api.post("/menu/categories/", data);
export const updateCategory = (id, data) => api.put(`/menu/categories/${id}/`, data);
export const deleteCategory = (id) => api.delete(`/menu/categories/${id}/`);

export const getItems = () => api.get("/menu/items/");
export const createItem = (data) => api.post("/menu/items/", data);
export const updateItem = (id, data) => api.put(`/menu/items/${id}/`, data);
export const deleteItem = (id) => api.delete(`/menu/items/${id}/`);
export const toggleItem = (id) => api.post(`/menu/items/${id}/toggle/`);

// ── Tables ────────────────────────────────────────────────────────────────────
export const getTables = () => api.get("/tables/");
export const createTable = (data) => api.post("/tables/", data);
export const updateTable = (id, data) => api.put(`/tables/${id}/`, data);
export const deleteTable = (id) => api.delete(`/tables/${id}/`);
export const regenerateQr = (id) => api.post(`/tables/${id}/qr/`);

// ── Orders ────────────────────────────────────────────────────────────────────
export const getOrders = (params) => api.get("/orders/", { params });
export const markPaid = (id) => api.post(`/orders/${id}/mark-paid/`);

// ── Kitchen ───────────────────────────────────────────────────────────────────
export const getKitchenOrders = () => api.get("/kitchen/orders/");
export const advanceOrder = (id) => api.post(`/kitchen/orders/${id}/advance/`);
export const cancelOrder = (id) => api.post(`/kitchen/orders/${id}/cancel/`);

// ── Waiter ────────────────────────────────────────────────────────────────────
export const getWaiterTables = () => api.get("/waiter/tables/");
export const getWaiterTableDetail = (id) => api.get(`/waiter/tables/${id}/`);
export const waiterAddItems = (id, data) => api.post(`/waiter/tables/${id}/add-items/`, data);
export const waiterMarkServed = (id) => api.post(`/waiter/orders/${id}/mark-served/`);

// ── Customer (public) — uses session header ───────────────────────────────────
import axios from "axios";

const PUBLIC_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : "/api";

const pub = axios.create({ baseURL: PUBLIC_BASE });

const sessionHeader = (qrToken) => {
  const sid = localStorage.getItem(`session_${qrToken}`);
  return sid ? { "X-Session-Id": sid } : {};
};

export const getCustomerMenu = (qrToken) =>
  pub.get(`/customer/${qrToken}/menu/`);

export const customerCheckin = (qrToken, data) =>
  pub.post(`/customer/${qrToken}/checkin/`, data);

export const getCustomerSession = (qrToken) =>
  pub.get(`/customer/${qrToken}/session/`, { headers: sessionHeader(qrToken) });

export const customerPlaceOrder = (qrToken, data) =>
  pub.post(`/customer/${qrToken}/order/`, data, {
    headers: sessionHeader(qrToken),
  });

export const trackOrder = (qrToken, orderId) =>
  pub.get(`/customer/${qrToken}/order/${orderId}/`);

// ── Analytics ─────────────────────────────────────────────────────────────────
export const getAnalytics = () => api.get("/analytics/");

// ── Billing ───────────────────────────────────────────────────────────────────
export const getBilling = () => api.get("/billing/");
export const changePlan = (planId) => api.post(`/billing/change-plan/${planId}/`);
