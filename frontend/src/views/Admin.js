import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import { api } from "../api/client";
export default function Admin() {
    const [models, setModels] = useState([]);
    const [note, setNote] = useState("");
    const [denied, setDenied] = useState(false);
    async function load() {
        setNote("");
        setDenied(false);
        try {
            const r = await api.adminModels();
            setModels(r.models);
        }
        catch (e) {
            if (e instanceof Error && (e.message.includes("401") || e.message.includes("Bearer"))) {
                setDenied(true);
                setNote("Admin requires a token: set it in Settings → API token.");
            }
            else
                setNote(e instanceof Error ? e.message : "Load failed.");
        }
    }
    useEffect(() => {
        load();
    }, []);
    async function act(kind, model_id) {
        setNote("");
        try {
            if (kind === "promote")
                await api.promote(model_id, "production");
            else
                await api.rollback(model_id, "production");
            setNote(`${kind} recorded for ${model_id} (audit-logged).`);
            await load();
        }
        catch (e) {
            setNote(e instanceof Error ? e.message : "Action failed.");
        }
    }
    return (_jsxs("section", { "aria-label": "admin", children: [_jsx("h2", { children: "Model administration" }), denied && _jsx("p", { role: "alert", children: "Not authorized \u2014 admin is RBAC-gated." }), note && _jsx("p", { role: "status", children: note }), _jsx("button", { type: "button", onClick: load, children: "Refresh" }), _jsx("ul", { children: models.map((m) => (_jsxs("li", { children: [m.model_id, " (", m.version, ", ", m.status, ")", " ", _jsx("button", { type: "button", onClick: () => act("promote", m.model_id), children: "Promote" }), " ", _jsx("button", { type: "button", onClick: () => act("rollback", m.model_id), children: "Rollback" })] }, m.model_id))) })] }));
}
