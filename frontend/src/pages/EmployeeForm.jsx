// Add/Edit Employee: one form for both.
// At /employees/new it adds a new employee; at /employees/5/edit it edits employee 5.
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { createEmployee, getDepartments, getEmployee, updateEmployee } from "../api.js";

const EMPTY_FORM = {
  name: "",
  email: "",
  department: "",
  job_title: "",
  salary: "",
  join_date: "",
  status: "Active",
};

// Same rules as the backend, checked in the browser first so the user gets instant feedback.
function validate(form) {
  const errors = {};
  if (!form.name.trim()) errors.name = "Name is required.";
  if (!form.email.trim()) errors.email = "Email is required.";
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) errors.email = "Enter a valid email, like name@company.com.";
  if (!form.department.trim()) errors.department = "Department is required.";
  if (!form.job_title.trim()) errors.job_title = "Job title is required.";
  if (form.salary === "") errors.salary = "Salary is required.";
  else if (Number(form.salary) <= 0) errors.salary = "Salary must be greater than 0.";
  if (!form.join_date) errors.join_date = "Join date is required.";
  return errors;
}

export default function EmployeeForm() {
  const { id } = useParams(); // undefined when adding
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getDepartments().then(setDepartments).catch(() => {});
  }, []);

  // When editing, fill the form with the employee's current details.
  useEffect(() => {
    if (!isEdit) return;
    setLoading(true);
    getEmployee(id)
      .then((emp) => setForm({ ...emp, salary: String(emp.salary) }))
      .catch((err) => setServerError(err.message))
      .finally(() => setLoading(false));
  }, [id, isEdit]);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
    setErrors({ ...errors, [name]: undefined }); // clear that field's error as the user fixes it
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setServerError("");
    const foundErrors = validate(form);
    setErrors(foundErrors);
    if (Object.keys(foundErrors).length > 0) return;

    const data = {
      name: form.name,
      email: form.email,
      department: form.department,
      job_title: form.job_title,
      salary: Number(form.salary),
      join_date: form.join_date,
      status: form.status,
    };
    setSaving(true);
    try {
      if (isEdit) await updateEmployee(id, data);
      else await createEmployee(data);
      navigate("/employees");
    } catch (err) {
      setServerError(err.message); // e.g. "An employee with email ... already exists."
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="text-gray-500">Loading…</p>;

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900">{isEdit ? "Edit Employee" : "Add Employee"}</h1>

      {serverError && <p className="mt-4 rounded bg-red-50 px-4 py-3 text-sm text-red-700">{serverError}</p>}

      <form onSubmit={handleSubmit} noValidate className="mt-6 rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <div className="grid gap-5 sm:grid-cols-2">
          <Field label="Full name" error={errors.name}>
            <input name="name" value={form.name} onChange={handleChange} className={inputClass(errors.name)} />
          </Field>

          <Field label="Email" error={errors.email}>
            <input name="email" type="email" value={form.email} onChange={handleChange} className={inputClass(errors.email)} />
          </Field>

          <Field label="Department" error={errors.department} hint="Pick one or type a new department.">
            <input
              name="department"
              list="department-options"
              value={form.department}
              onChange={handleChange}
              className={inputClass(errors.department)}
            />
            <datalist id="department-options">
              {departments.map((d) => (
                <option key={d} value={d} />
              ))}
            </datalist>
          </Field>

          <Field label="Job title" error={errors.job_title}>
            <input name="job_title" value={form.job_title} onChange={handleChange} className={inputClass(errors.job_title)} />
          </Field>

          <Field label="Annual salary (₹ INR)" error={errors.salary}>
            <input
              name="salary"
              type="number"
              min="1"
              step="10000"
              value={form.salary}
              onChange={handleChange}
              className={inputClass(errors.salary)}
            />
          </Field>

          <Field label="Join date" error={errors.join_date}>
            <input name="join_date" type="date" value={form.join_date} onChange={handleChange} className={inputClass(errors.join_date)} />
          </Field>

          <Field label="Status">
            <select name="status" value={form.status} onChange={handleChange} className={inputClass()}>
              <option>Active</option>
              <option>Inactive</option>
            </select>
          </Field>
        </div>

        <div className="mt-8 flex gap-3">
          <button
            type="submit"
            disabled={saving}
            className="rounded bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? "Saving…" : isEdit ? "Save changes" : "Add employee"}
          </button>
          <Link to="/employees" className="rounded border border-gray-300 px-5 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}

// A label + input + error message, so every field looks the same.
function Field({ label, error, hint, children }) {
  return (
    <label className="block">
      <span className="text-sm font-medium text-gray-700">{label}</span>
      <div className="mt-1">{children}</div>
      {error ? <p className="mt-1 text-xs text-red-600">{error}</p> : hint && <p className="mt-1 text-xs text-gray-500">{hint}</p>}
    </label>
  );
}

function inputClass(error) {
  return `w-full rounded border px-3 py-2 text-sm focus:outline-none ${
    error ? "border-red-400 focus:border-red-500" : "border-gray-300 focus:border-indigo-500"
  } bg-white`;
}
