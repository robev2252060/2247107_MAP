import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/dashboard",  label: "Dashboard",  icon: "📊" },
  { to: "/rules",      label: "Rules",      icon: "⚙️" },
  { to: "/actuators",  label: "Actuators",  icon: "🔧" },
];

export default function Sidebar() {
  return (
    <nav className="sidebar">
      {NAV_ITEMS.map(({ to, label, icon }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            `sidebar__link${isActive ? " sidebar__link--active" : ""}`
          }
        >
          <span className="sidebar__icon">{icon}</span>
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
