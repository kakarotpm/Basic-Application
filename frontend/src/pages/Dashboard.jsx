// Dashboard: summary cards plus two bar charts by department.
// All the numbers come from plain SQL queries in backend/app/services/dashboard.py.
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getDashboard } from "../api.js";
import { formatLakhs, formatMoney } from "../format.js";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getDashboard()
      .then(setData)
      .catch((err) => setError(`Couldn't load the dashboard: ${err.message}. Is the backend server running?`));
  }, []);

  if (error) return <p className="rounded bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>;
  if (!data) return <p className="text-gray-500">Loading…</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
      <p className="mt-1 text-sm text-gray-500">Figures include Active employees only, except Total employees.</p>

      {/* Summary cards */}
      <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
        <Card label="Total employees" value={data.total_employees} />
        <Card label="Active employees" value={data.active_employees} />
        <Card label="Departments" value={data.department_count} />
        <Card label="Average salary" value={formatMoney(data.average_salary)} />
        <Link to="/leave" className="block">
          <Card label="Pending leave requests" value={data.pending_leave_requests} highlight={data.pending_leave_requests > 0} />
        </Link>
      </div>

      {/* Charts */}
      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <ChartPanel title="Employees by department">
          <BarChart data={data.employees_by_department} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="department" tick={{ fontSize: 12 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
            <Tooltip formatter={(value) => [value, "Employees"]} cursor={{ fill: "#eef2ff" }} />
            <Bar dataKey="employee_count" fill="#4f46e5" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ChartPanel>

        <ChartPanel title="Average salary by department">
          <BarChart data={data.average_salary_by_department} margin={{ top: 8, right: 8, left: 8, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="department" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={formatLakhs} tick={{ fontSize: 12 }} />
            <Tooltip formatter={(value) => [formatMoney(value), "Average salary"]} cursor={{ fill: "#ecfdf5" }} />
            <Bar dataKey="average_salary" fill="#059669" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ChartPanel>
      </div>
    </div>
  );
}

function Card({ label, value, highlight = false }) {
  return (
    <div className={`h-full rounded-lg border bg-white p-4 shadow-sm ${highlight ? "border-amber-300" : "border-gray-200"}`}>
      <p className="text-sm text-gray-500">{label}</p>
      <p className={`mt-1 text-2xl font-semibold tabular-nums ${highlight ? "text-amber-600" : "text-gray-900"}`}>{value}</p>
    </div>
  );
}

function ChartPanel({ title, children }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h2 className="mb-4 font-semibold text-gray-800">{title}</h2>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
