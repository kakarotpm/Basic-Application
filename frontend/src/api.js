// All calls to the backend go through this file, so the backend address lives in one place.
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

// Calls the backend and returns the JSON response.
// If the backend returns an error, throws an Error with the backend's message.
export async function request(path, options = {}) {
  const response = await fetch(API_URL + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(await errorMessage(response));
  }
  return response.status === 204 ? null : response.json();
}

// FastAPI sends errors as {"detail": "message"}, or for validation errors,
// {"detail": [{"loc": [..., "email"], "msg": "..."}, ...]}.
async function errorMessage(response) {
  const body = await response.json().catch(() => ({}));
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail)) {
    return body.detail.map((d) => `${d.loc.at(-1)}: ${d.msg}`).join("; ");
  }
  return `Request failed (${response.status})`;
}

export const checkHealth = () => request("/health");
export const getDashboard = () => request("/dashboard");

// ---- Employees ----

export function getEmployees({ search = "", department = "" } = {}) {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (department) params.set("department", department);
  return request(`/employees?${params}`);
}

export const getDepartments = () => request("/employees/departments");
export const getEmployee = (id) => request(`/employees/${id}`);
export const createEmployee = (data) => request("/employees", { method: "POST", body: JSON.stringify(data) });
export const updateEmployee = (id, data) => request(`/employees/${id}`, { method: "PUT", body: JSON.stringify(data) });

// ---- Leave requests ----

export const getLeaveRequests = (status = "") => request(`/leave-requests${status ? `?status=${status}` : ""}`);
export const applyLeave = (data) => request("/leave-requests", { method: "POST", body: JSON.stringify(data) });
export const approveLeave = (id) => request(`/leave-requests/${id}/approve`, { method: "POST" });
export const rejectLeave = (id) => request(`/leave-requests/${id}/reject`, { method: "POST" });
export const deleteEmployee = (id) => request(`/employees/${id}`, { method: "DELETE" });
