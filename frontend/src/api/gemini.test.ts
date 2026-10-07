import { beforeEach, describe, expect, test, vi } from "vitest";
import {
  getGeminiApiKey,
  getGeminiModelName,
  interpretSignSequence,
  listAvailableGeminiModels,
  setGeminiApiKey,
  setGeminiModelName,
  sortModelsByPreference,
} from "./gemini";

const store = new Map<string, string>();
beforeEach(() => {
  store.clear();
  vi.stubGlobal("localStorage", {
    getItem: (k: string) => (store.has(k) ? store.get(k)! : null),
    setItem: (k: string, v: string) => void store.set(k, v),
    removeItem: (k: string) => void store.delete(k),
    clear: () => store.clear(),
  });
});

describe("Gemini API key & model storage", () => {
  test("getGeminiApiKey retrieves saved key from localStorage", () => {
    setGeminiApiKey("AIzaSyTestKey");
    expect(getGeminiApiKey()).toBe("AIzaSyTestKey");
  });

  test("getGeminiModelName returns auto by default or saved model", () => {
    expect(getGeminiModelName()).toBe("auto");
    setGeminiModelName("gemini-1.5-flash-latest");
    expect(getGeminiModelName()).toBe("gemini-1.5-flash-latest");
  });

  test("sortModelsByPreference puts high-quota flash models first", () => {
    const input = [
      "gemini-1.0-pro",
      "gemini-1.5-pro",
      "gemini-2.0-flash",
      "gemini-1.5-flash",
      "gemini-1.5-flash-8b",
    ];
    const sorted = sortModelsByPreference(input);
    expect(sorted[0]).toBe("gemini-1.5-flash-8b");
    expect(sorted[1]).toBe("gemini-1.5-flash");
    expect(sorted[2]).toBe("gemini-2.0-flash");
  });

  test("empty sequence throws validation error without making fetch call", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    await expect(interpretSignSequence([])).rejects.toThrow(
      "Cannot interpret an empty sign sequence."
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test("missing API key throws clear instruction error", async () => {
    store.clear();
    vi.stubEnv("VITE_GEMINI_API_KEY", "");
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    await expect(interpretSignSequence(["GO", "WATER"])).rejects.toThrow(
      /Gemini API key is missing/
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test("successful Gemini response returns cleaned English sentence", async () => {
    setGeminiApiKey("valid-key");
    const mockResponse = {
      candidates: [
        {
          content: {
            parts: [{ text: "I am going to drink water." }],
          },
        },
      ],
    };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      })
    );

    const result = await interpretSignSequence(["GO", "WATER", "DRINK"]);
    expect(result).toBe("I am going to drink water.");
  });

  test("interpretSignSequence supports emotional mood parameter", async () => {
    setGeminiApiKey("valid-key");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        candidates: [{ content: { parts: [{ text: "I am super excited to see you!" }] } }],
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await interpretSignSequence(["HAPPY", "SEE", "YOU"], "happy");
    expect(result).toBe("I am super excited to see you!");
    const postCall = fetchMock.mock.calls.find((c) => c[1]?.body);
    expect(postCall).toBeDefined();
    const calledBody = JSON.parse(postCall![1].body);
    expect(calledBody.contents[0].parts[1].text).toContain("Enthusiastic, joyful, cheerful");
  });

  test("recovers when first model returns 429 by falling over to the next candidate model", async () => {
    setGeminiApiKey("valid-key");
    setGeminiModelName("gemini-2.0-flash");

    const fetchMock = vi.fn();
    // First model v1beta returns 429
    fetchMock.mockResolvedValueOnce({
      ok: false,
      status: 429,
      statusText: "Too Many Requests",
      json: async () => ({ error: { message: "Resource exhausted" } }),
    });
    // First model v1 returns 429
    fetchMock.mockResolvedValueOnce({
      ok: false,
      status: 429,
      statusText: "Too Many Requests",
      json: async () => ({ error: { message: "Resource exhausted" } }),
    });
    // Second model succeeds!
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        candidates: [
          { content: { parts: [{ text: "Hello friend." }] } },
        ],
      }),
    });

    vi.stubGlobal("fetch", fetchMock);

    const result = await interpretSignSequence(["HELLO", "NEW_SIGN_1"]);
    expect(result).toBe("Hello friend.");
  });

  test("recovers from non-supported modality error by trying next text model", async () => {
    setGeminiApiKey("valid-key");
    setGeminiModelName("gemini-2.0-flash");

    const fetchMock = vi.fn();
    // First model returns 400 with modality error (like tts/audio)
    fetchMock.mockResolvedValueOnce({
      ok: false,
      status: 400,
      statusText: "Bad Request",
      json: async () => ({
        error: {
          message:
            "The requested combination of response modalities (TEXT) is not supported by the model.",
        },
      }),
    });
    // Second model (v1 or next candidate) returns valid text
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        candidates: [
          { content: { parts: [{ text: "I want water." }] } },
        ],
      }),
    });

    vi.stubGlobal("fetch", fetchMock);

    const result = await interpretSignSequence(["WANT", "WATER"]);
    expect(result).toBe("I want water.");
  });

  test("listAvailableGeminiModels filters out TTS and audio-only models", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          models: [
            { name: "models/gemini-2.0-flash", supportedGenerationMethods: ["generateContent"] },
            { name: "models/gemini-2.5-flash-preview-tts", supportedGenerationMethods: ["generateContent"] },
            { name: "models/embedding-001", supportedGenerationMethods: ["embedContent"] },
          ],
        }),
      })
    );

    const models = await listAvailableGeminiModels("test-key");
    expect(models).toContain("gemini-2.0-flash");
    expect(models).not.toContain("gemini-2.5-flash-preview-tts");
    expect(models).not.toContain("embedding-001");
  });

  test("Gemini API rate limit (429) across all models returns informative error", async () => {
    setGeminiApiKey("valid-key");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 429,
        statusText: "Too Many Requests",
        json: async () => ({ error: { message: "Resource exhausted" } }),
      })
    );

    await expect(interpretSignSequence(["GO", "ALL_429"])).rejects.toThrow(
      /rate limit reached/
    );
  });
});
