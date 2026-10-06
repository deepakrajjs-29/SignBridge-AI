import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import Admin from "./views/Admin";
import History from "./views/History";
import Live from "./views/Live";
import Settings from "./views/Settings";
import Vocab from "./views/Vocab";
export default function App() {
    const [tab, setTab] = useState("live");
    const [last, setLast] = useState(null);
    return (_jsxs("main", { style: { fontFamily: "system-ui", padding: 24, maxWidth: 860 }, children: [_jsx("h1", { children: "SignBridge AI" }), _jsx("nav", { "aria-label": "primary", style: { display: "flex", gap: 8, marginBottom: 16 }, children: ["live", "history", "vocab", "admin", "settings"].map((t) => (_jsx("button", { type: "button", onClick: () => setTab(t), "aria-current": tab === t ? "page" : undefined, style: { fontWeight: tab === t ? "bold" : "normal" }, children: t[0].toUpperCase() + t.slice(1) }, t))) }), tab === "live" && _jsx(Live, { onResult: setLast }), tab === "history" && _jsx(History, {}), tab === "vocab" && _jsx(Vocab, {}), tab === "admin" && _jsx(Admin, {}), tab === "settings" && _jsx(Settings, {}), last && tab === "live" && (_jsxs("p", { "aria-live": "polite", children: ["Last result: ", last.label, " (", last.confidence, ")"] })), _jsx("footer", { style: { marginTop: 24, fontSize: 12 }, children: _jsx("p", { children: "Camera-active indicator shown in Live tab. No video stored by default." }) })] }));
}
