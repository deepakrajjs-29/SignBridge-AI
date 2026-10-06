import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import { api } from "../api/client";
export default function History() {
    const [sessions, setSessions] = useState([]);
    const [sid, setSid] = useState("");
    const [items, setItems] = useState([]);
    const [note, setNote] = useState("");
    async function refresh() {
        setNote("");
        try {
            const s = await api.sessions();
            setSessions(s.sessions);
            if (s.sessions.length && !sid)
                setSid(s.sessions[0].session_id);
        }
        catch (e) {
            setNote(e instanceof Error ? e.message : "Load failed.");
        }
    }
    useEffect(() => {
        refresh();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);
    useEffect(() => {
        if (!sid)
            return;
        api
            .sessionPredictions(sid)
            .then((r) => setItems(r.predictions))
            .catch((e) => setNote(e.message));
    }, [sid, sessions]);
    async function remove(pid) {
        if (!pid)
            return;
        await api.deletePrediction(pid);
        setItems((xs) => xs.filter((x) => x.prediction_id !== pid));
    }
    return (_jsxs("section", { "aria-label": "history", children: [_jsx("h2", { children: "Recognition history" }), _jsx("p", { children: "Stored predictions per session. Delete any entry or clear the session. Raw video is never stored." }), _jsxs("label", { children: ["Session", " ", _jsx("select", { value: sid, onChange: (e) => setSid(e.target.value), "aria-label": "session-select", children: sessions.map((s) => (_jsx("option", { value: s.session_id, children: s.session_id }, s.session_id))) })] }), " ", _jsx("button", { type: "button", onClick: refresh, children: "Refresh" }), note && _jsx("p", { role: "alert", children: note }), _jsx("ul", { children: items.map((p) => (_jsxs("li", { children: [p.label, " (", p.class_id, ", ", p.confidence, ") \u2014 ", p.status, " ", _jsx("button", { type: "button", onClick: () => remove(p.prediction_id), "aria-label": `delete-${p.prediction_id}`, children: "Delete" })] }, p.prediction_id ?? `${p.class_id}-${p.confidence}`))) }), items.length === 0 && _jsx("p", { children: "No predictions in this session yet." })] }));
}
