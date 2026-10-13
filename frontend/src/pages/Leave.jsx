// Leave: a form to apply for leave, and a list of requests with Approve/Reject.
import { useEffect, useState } from "react";
import { applyLeave, approveLeave, getEmployees, getLeaveRequests, rejectLeave } from "../api.js";
import { formatDate } from "../format.js";

const EMPTY_FORM = { employee_id: "", leave_type: "", start_date: "", end_date: "", reason: "" };
const STATUS_FILTERS = ["All", "Pending", "Approved", "Rejected"];
const STATUS_COLORS = {
  Pending: "bg-amber-100 text-amber-800",
  Approved: "bg-green-100 text-green-800",
  Rejected: "bg-red-100 text-red-800",
};

// Same rules as the backend, checked in the browser first for instant feedback.
function validate(form) {
  const errors = {};
  if (!form.employee_id) errors.employee_id = "Choose an employee.";
  if (!form.leave_type) errors.leave_type = "Choose a leave type.";
  if (!form.start_date) errors.start_date = "Start date is required.";
  if (!form.end_date) errors.end_date = "End date is required.";
  else if (form.start_date && form.end_date < form.start_date) errors.end_date = "End date can't be before the start date.";
  if (!form.reason.trim()) errors.reason = "Please give a reason.";
  return errors;
}

export default function Leave() {
  const [employees, setEmployees] = useState([]);
  const [requests, setRequests] = useState([]);
  const [statusFilter, setStatusFilter] = useState("All");
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [formMessage, setFormMessage] = useState(null); // { type: "success" | "error", text }
  const [listError, setListError] = useState("");
  const [saving, setSaving] = useState(false);

  // Only Active employees can apply for leave, so only they appear in the dropdown.
  useEffect(() => {
    getEmployees()
      .then((all) => setEmployees(all.filter((e) => e.status === "Active")))
      .catch(() => {});
  }, []);

  function loadRequests() {
    setListError("");
    getLeaveRequests(statusFilter === "All" ? "" : statusFilter)
      .then(setRequests)
      .catch((err) => setListError(err.message));
  }

  useEffect(loadRequests, [statusFilter]);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    setErrors({ ...errors, [name]: undefined });
    setFormMessage(null);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const foundErrors = validate(form);
    setErrors(foundErrors);
    if (Object.keys(foundErrors).length > 0) return;

    setSaving(true);
    try {
      const created = await applyLeave({ ...form, employee_id: Number(form.employee_id) });
      setForm(EMPTY_FORM);
      setFormMessage({ type: "success", text: `Leave request submitted for ${created.employee_name} (${created.days} day${created.days === 1 ? "" : "s"}).` });
      loadRequests();
    } catch (err) {
      setFormMessage({ type: "error", text: err.message });
    } finally {
      setSaving(false);
    }
  }

  async function handleDecision(action, leave) {
    try {
      await action(leave.id);
      loadRequests();
    } catch (err) {
      setListError(err.message); // e.g. "This request is already Approved."
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Leave</h1>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        {/* Apply form */}
        <form onSubmit={handleSubmit} noValidate className="h-fit rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <h2 className="font-semibold text-gray-800">Apply for leave</h2>

          {formMessage && (
            <p className={`mt-3 rounded px-3 py-2 text-sm ${formMessage.type === "success" ? "bg-green-50 text-green-800" : "bg-red-50 text-red-700"}`}>
              {formMessage.text}
            </p>
          )}

          <div className="mt-4 space-y-4">
            <Field label="Employee" error={errors.employee_id}>
              <select name="employee_id" value={form.employee_id} onChange={handleChange} className={inputClass(errors.employee_id)}>
                <option value="">Select an employee…</option>
                {employees.map((emp) => (
                  <option key={emp.id} value={emp.id}>
                    {emp.name} ({emp.department})
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Leave type" error={errors.leave_type}>
              <select name="leave_type" value={form.leave_type} onChange={handleChange} className={inputClass(errors.leave_type)}>
                <option value="">Select a type…</option>
                <option>Sick</option>
                <option>Casual</option>
                <option>Annual</option>
              </select>
            </Field>

            <div className="grid grid-cols-2 gap-3">
              <Field label="Start date" error={errors.start_date}>
                <input name="start_date" type="date" value={form.start_date} onChange={handleChange} className={inputClass(errors.start_date)} />
              </Field>
              <Field label="End date" error={errors.end_date}>
                <input
                  name="end_date"
                  type="date"
                  min={form.start_date || undefined}
                  value={form.end_date}
                  onChange={handleChange}
                  className={inputClass(errors.end_date)}
                />
              </Field>
            </div>

            <Field label="Reason" error={errors.reason}>
              <textarea name="reason" rows={3} value={form.reason} onChange={handleChange} className={inputClass(errors.reason)} />
            </Field>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="mt-5 w-full rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? "Submitting…" : "Submit request"}
          </button>
        </form>

        {/* Requests list */}
        <div className="lg:col-span-2">
          <div className="flex flex-wrap gap-2">
            {STATUS_FILTERS.map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`rounded-full px-3 py-1 text-sm font-medium ${
                  statusFilter === status ? "bg-indigo-600 text-white" : "bg-white text-gray-700 ring-1 ring-gray-300 hover:bg-gray-50"
                }`}
              >
                {status}
              </button>
            ))}
          </div>

          {listError && <p className="mt-3 rounded bg-red-50 px-4 py-3 text-sm text-red-700">{listError}</p>}

          <div className="mt-3 overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-gray-100 text-xs uppercase tracking-wide text-gray-600">
                <tr>
                  <th className="px-4 py-3">Employee</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Dates</th>
                  <th className="px-4 py-3">Reason</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {requests.map((leave) => (
                  <tr key={leave.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{leave.employee_name}</td>
                    <td className="px-4 py-3">{leave.leave_type}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {formatDate(leave.start_date)}
                      {leave.end_date !== leave.start_date && ` – ${formatDate(leave.end_date)}`}
                      <div className="text-xs text-gray-500">
                        {leave.days} day{leave.days === 1 ? "" : "s"}
                      </div>
                    </td>
                    <td className="max-w-xs px-4 py-3 text-gray-700">{leave.reason}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[leave.status]}`}>{leave.status}</span>
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      {leave.status === "Pending" ? (
                        <>
                          <button onClick={() => handleDecision(approveLeave, leave)} className="font-medium text-green-700 hover:underline">
                            Approve
                          </button>
                          <button onClick={() => handleDecision(rejectLeave, leave)} className="ml-4 font-medium text-red-600 hover:underline">
                            Reject
                          </button>
                        </>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {requests.length === 0 && !listError && (
              <p className="px-4 py-8 text-center text-gray-500">
                No {statusFilter === "All" ? "" : statusFilter.toLowerCase() + " "}leave requests.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// A label + input + error message, so every field looks the same.
function Field({ label, error, children }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-gray-700">{label}</span>
      <div className="mt-1">{children}</div>
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </label>
  );
}

function inputClass(error) {
  return `w-full rounded border bg-white px-3 py-2 text-sm focus:outline-none ${
    error ? "border-red-400 focus:border-red-500" : "border-gray-300 focus:border-indigo-500"
  }`;
}
