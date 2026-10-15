import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { connectStream } from "./stream";
import type { StreamCallbacks } from "./stream";

const noop: StreamCallbacks = {
  onStatus: () => {},
  onPrediction: () => {},
  onError: () => {},
};

/** Minimal spec-faithful socket: send() while CONNECTING throws InvalidStateError. */
class FakeSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;
  readyState = FakeSocket.CONNECTING;
  sent: string[] = [];
  onopen: ((ev: unknown) => void) | null = null;
  onmessage: ((ev: { data: string }) => void) | null = null;
  onerror: (() => void) | null = null;
  onclose: ((ev: { code: number }) => void) | null = null;
  url: string;
  constructor(url: string) {
    this.url = url;
    instances.push(this);
  }
  send(data: string) {
    if (this.readyState !== FakeSocket.OPEN) throw new Error("InvalidStateError: Still in CONNECTING state");
    this.sent.push(data);
  }
  close() {
    this.readyState = FakeSocket.CLOSED;
  }
  open() {
    this.readyState = FakeSocket.OPEN;
    this.onopen?.({});
  }
}
const instances: FakeSocket[] = [];

afterEach(() => {
  instances.length = 0;
  vi.unstubAllGlobals();
});

const store: Record<string, string> = {};
beforeEach(() => {
  vi.stubGlobal("localStorage", {
    getItem: (k: string) => store[k] ?? null,
    setItem: (k: string, v: string) => void (store[k] = v),
    removeItem: (k: string) => void delete store[k],
  });
});

function installFake() {
  vi.stubGlobal("WebSocket", FakeSocket as unknown as typeof WebSocket);
}

describe("connectStream open-handshake", () => {
  test("sendFrame before open queues and flushes on open instead of throwing", () => {
    installFake();
    const handle = connectStream("http://x", "sess_1", noop);
    expect(() => {
      handle.sendFrame([0.1, 0.2]);
      handle.sendFrame([0.3, 0.4]);
    }).not.toThrow();
    expect(instances).toHaveLength(1);
    expect(instances[0].sent).toHaveLength(0);
    instances[0].open();
    const sent = instances[0].sent.map((s) => JSON.parse(s));
    expect(sent).toEqual([
      { type: "start" },
      { type: "frame", frame: [0.1, 0.2] },
      { type: "frame", frame: [0.3, 0.4] },
    ]);
  });

  test("ready resolves once the socket opens", async () => {
    installFake();
    const handle = connectStream("http://x", "sess_1", noop);
    let opened = false;
    const p = handle.ready!.then(() => (opened = true));
    expect(opened).toBe(false);
    instances[0].open();
    await p;
    expect(opened).toBe(true);
  });

  test("unknown-session close (4404) reports a specific note, not the generic error", () => {
    installFake();
    const errors: string[] = [];
    connectStream("http://x", "sess_1", { ...noop, onError: (m) => void errors.push(m) });
    instances[0].onclose?.({ code: 4404 });
    expect(errors).toEqual([expect.stringMatching(/session/i)]);
    expect(errors[0]).not.toMatch(/use REST fallback/);
  });
});
