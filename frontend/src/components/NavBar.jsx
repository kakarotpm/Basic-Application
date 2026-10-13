// The navigation bar shown at the top of every page.
import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/employees", label: "Employees" },
  { to: "/employees/new", label: "Add Employee" },
  { to: "/leave", label: "Leave" },
];

export default function NavBar() {
  return (
    <nav className="bg-indigo-700 text-white shadow">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3">
        <span className="text-lg font-semibold">Employee Management</span>
        <div className="flex flex-wrap gap-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end // highlight "Employees" only on /employees, not on /employees/new
              className={({ isActive }) =>
                `rounded px-3 py-1.5 text-sm font-medium ${isActive ? "bg-indigo-900" : "hover:bg-indigo-600"}`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
}
