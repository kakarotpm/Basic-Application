// The app's layout: the navigation bar on top, and the current page below it.
// Each <Route> maps a web address to a page.
import { Route, Routes } from "react-router-dom";
import NavBar from "./components/NavBar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import EmployeeDirectory from "./pages/EmployeeDirectory.jsx";
import EmployeeForm from "./pages/EmployeeForm.jsx";
import Leave from "./pages/Leave.jsx";

export default function App() {
  return (
    <div className="min-h-screen">
      <NavBar />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/employees" element={<EmployeeDirectory />} />
          {/* Different keys give Add and Edit a fresh, empty form when switching between them */}
          <Route path="/employees/new" element={<EmployeeForm key="new" />} />
          <Route path="/employees/:id/edit" element={<EmployeeForm key="edit" />} />
          <Route path="/leave" element={<Leave />} />
          <Route path="*" element={<p className="text-gray-600">Page not found.</p>} />
        </Routes>
      </main>
    </div>
  );
}
