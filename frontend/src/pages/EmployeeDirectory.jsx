// Employee Directory: a searchable, filterable table of employees with Edit and Delete.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { deleteEmployee, getDepartments, getEmployees } from "../api.js";
import { formatDate, formatMoney } from "../format.js";

export default function EmployeeDirectory() {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  function loadEmployees() {
    setLoading(true);
    setError("");
    getEmployees({ search, department })
      .then(setEmployees)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  // Load the department list once, for the filter dropdown.
  useEffect(() => {
    getDepartments().then(setDepartments).catch(() => {});
  }, []);

  // Reload the table whenever the search or filter changes.
  // The short delay waits for the user to stop typing before asking the backend.
  useEffect(() => {
    const timer = setTimeout(loadEmployees, 250);
    return () => clearTimeout(timer);
  }, [search, department]);

  async function handleDelete(employee) {
    const confirmed = window.confirm(
      `Delete ${employee.name}?\n\nThis also deletes their leave requests and cannot be undone.`,
    );
    if (!confirmed) return;
    try {
      await deleteEmployee(employee.id);
      loadEmployees();
      getDepartments().then(setDepartments).catch(() => {}); // a department may now be empty
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-gray-900">Employees</h1>
        <Link to="/employees/new" className="rounded bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
          + Add Employee
        </Link>
      </div>

      {/* Search and filter */}
      <div className="mt-6 flex flex-wrap gap-3">
        <input
          type="search"
          placeholder="Search name, email or job title…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-sm rounded border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
        />
        <select
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          className="rounded border border-gray-300 bg-white px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
        >
          <option value="">All departments</option>
          {departments.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>

      {error && <p className="mt-4 rounded bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

      {/* Table */}
      <div className="mt-4 overflow-x-auto rounded-lg border border-gray-200 bg-white shadow-sm">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-gray-100 text-xs uppercase tracking-wide text-gray-600">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Department</th>
              <th className="px-4 py-3">Job Title</th>
              <th className="px-4 py-3 text-right">Salary</th>
              <th className="px-4 py-3">Joined</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {employees.map((emp) => (
              <tr key={emp.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="font-medium text-gray-900">{emp.name}</div>
                  <div className="text-xs text-gray-500">{emp.email}</div>
                </td>
                <td className="px-4 py-3">{emp.department}</td>
                <td className="px-4 py-3">{emp.job_title}</td>
                <td className="px-4 py-3 text-right tabular-nums">{formatMoney(emp.salary)}</td>
                <td className="px-4 py-3 whitespace-nowrap">{formatDate(emp.join_date)}</td>
                <td className="px-4 py-3">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      emp.status === "Active" ? "bg-green-100 text-green-800" : "bg-gray-200 text-gray-700"
                    }`}
                  >
                    {emp.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-right whitespace-nowrap">
                  <Link to={`/employees/${emp.id}/edit`} className="font-medium text-indigo-600 hover:underline">
                    Edit
                  </Link>
                  <button onClick={() => handleDelete(emp)} className="ml-4 font-medium text-red-600 hover:underline">
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {!loading && employees.length === 0 && (
          <p className="px-4 py-8 text-center text-gray-500">No employees match your search.</p>
        )}
      </div>

      <p className="mt-3 text-sm text-gray-500">
        {loading ? "Loading…" : `Showing ${employees.length} employee${employees.length === 1 ? "" : "s"}`}
      </p>
    </div>
  );
}
