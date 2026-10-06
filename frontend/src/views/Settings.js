import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
export default function Settings() {
    const [tok, setTok] = useState(localStorage.getItem("sb_token") ?? "");
    const [saved, setSaved] = useState(false);
    return (_jsxs("section", { "aria-label": "settings-help", children: [_jsx("h2", { children: "Settings" }), _jsxs("label", { children: ["API token (Bearer for predict/session/admin; open endpoints need none)", " ", _jsx("input", { value: tok, onChange: (e) => setTok(e.target.value), "aria-label": "api-token", autoComplete: "off" })] }), " ", _jsx("button", { type: "button", onClick: () => {
                    localStorage.setItem("sb_token", tok);
                    setSaved(true);
                }, children: "Save" }), saved && _jsx("p", { role: "status", children: "Token saved locally." }), _jsx("h3", { children: "Help" }), _jsxs("ul", { children: [_jsx("li", { children: "Allow camera \u2192 Start recognition \u2192 review result \u2192 Speak/repeat \u2192 Clear." }), _jsx("li", { children: "Uncertain means low confidence \u2014 never treated as definitive." }), _jsx("li", { children: "History entries can be deleted anytime; raw video is never stored." }), _jsx("li", { children: "Verify high-stakes outputs with a human." })] })] }));
}
