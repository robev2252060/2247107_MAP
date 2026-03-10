import { Outlet } from "react-router-dom";
import Navbar from "./Navbar.jsx";
import Sidebar from "./Sidebar.jsx";

export default function Layout() {
  return (
    <div className="layout">
      <Navbar />
      <div className="layout__body">
        <Sidebar />
        <main className="layout__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
