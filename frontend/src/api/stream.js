export function connectStream(base, sessionId, cb) {
    const url = `${base.replace(/^http/, "ws")}/api/v1/stream?session_id=${sessionId}`;
    const socket = new WebSocket(url);
    socket.onopen = () => socket.send(JSON.stringify({ type: "start" }));
    socket.onmessage = (ev) => {
        const m = JSON.parse(ev.data);
        if (m.type === "prediction" && m.prediction)
            cb.onPrediction(m.prediction, m.state ?? "Uncertain");
        else if (m.type === "status")
            cb.onStatus(m.state ?? "", m.session_id ?? "");
        else if (m.type === "error")
            cb.onError(m.message ?? "stream error");
    };
    socket.onerror = () => cb.onError("WebSocket error — use REST fallback.");
    return {
        sendFrame: (frame) => socket.send(JSON.stringify({ type: "frame", frame })),
        heartbeat: () => socket.send(JSON.stringify({ type: "heartbeat" })),
        stop: () => {
            try {
                socket.send(JSON.stringify({ type: "stop" }));
            }
            finally {
                socket.close();
            }
        },
        socket,
    };
}
