import { jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import { api } from "../api/client";
export default function Vocab() {
    const [classes, setClasses] = useState([]);
    const [q, setQ] = useState("");
    const [text, setText] = useState("");
    const [out, setOut] = useState(null);
    const [unsupported, setUnsupported] = useState([]);
    const [note, setNote] = useState("");
    useEffect(() => {
        api.classes().then((r) => setClasses(r.classes)).catch((e) => setNote(e.message));
    }, []);
    const shown = classes.filter((c) => c.label.toLowerCase().includes(q.toLowerCase()));
    async function convert() {
        setNote("");
        try {
            const r = await api.textToSign(text);
            setOut(r.items);
            setUnsupported(r.unsupported_words);
        }
        catch (e) {
            setNote(e instanceof Error ? e.message : "Conversion failed.");
        }
    }
    return (_jsxs("section", { "aria-label": "vocabulary", children: [_jsxs("h2", { children: ["Supported signs (", classes.length, ")"] }), _jsxs("label", { children: ["Search ", _jsx("input", { value: q, onChange: (e) => setQ(e.target.value), "aria-label": "vocab-search" })] }), _jsx("ul", { children: shown.slice(0, 50).map((c) => (_jsxs("li", { children: [c.label, " (", c.class_id, ", ", c.sign_type, ")"] }, c.class_id))) }), _jsx("h3", { children: "Text-to-sign" }), _jsxs("label", { children: ["Text ", _jsx("input", { value: text, onChange: (e) => setText(e.target.value), "aria-label": "t2s-input" })] }), " ", _jsx("button", { type: "button", onClick: convert, children: "Convert" }), note && _jsx("p", { role: "alert", children: note }), out && (_jsx("ul", { children: out.map((o) => (_jsxs("li", { children: [o.word, " \u2192 ", o.label, " (", o.supported ? "visual available" : "no visual yet", ")"] }, o.word))) })), unsupported.length > 0 && _jsxs("p", { children: ["Unsupported words: ", unsupported.join(", ")] })] }));
}
