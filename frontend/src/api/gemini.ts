/**
 * Universal Gemini Natural Language Interpretation Layer for SignBridge AI.
 * Compatible with ANY Gemini API key and ANY supported model (1.5-flash, 1.5-flash-8b, 2.0-flash, Pro, etc.).
 * Includes model-to-model rate-limit fallback, text modality filtering, and smart caching.
 */

export function getGeminiApiKey(): string {
  try {
    if (typeof localStorage !== "undefined") {
      const fromStorage = localStorage.getItem("sb_gemini_api_key");
      if (fromStorage && fromStorage.trim()) return fromStorage.trim();
    }
  } catch {
    /* ignore storage access error */
  }
  return import.meta.env.VITE_GEMINI_API_KEY || "";
}

export function setGeminiApiKey(key: string): void {
  try {
    if (typeof localStorage !== "undefined") {
      const trimmed = key.trim().replace(/^['"]|['"]$/g, "");
      localStorage.setItem("sb_gemini_api_key", trimmed);
      // Reset active resolved model when key changes so it rediscovers for the new key
      activeResolvedModel = null;
      translationCache.clear();
    }
  } catch {
    /* ignore storage access error */
  }
}

export function getGeminiModelName(): string {
  try {
    if (typeof localStorage !== "undefined") {
      const custom = localStorage.getItem("sb_gemini_model");
      if (custom && custom.trim()) {
        return custom.trim();
      }
    }
  } catch {
    /* ignore storage access error */
  }
  return "auto";
}

export function setGeminiModelName(model: string): void {
  try {
    if (typeof localStorage !== "undefined") {
      localStorage.setItem("sb_gemini_model", model.trim());
      activeResolvedModel = model.trim() === "auto" ? null : model.trim();
    }
  } catch {
    /* ignore storage access error */
  }
}

const SYSTEM_PROMPT = `You are the natural-language interpretation layer for SignBridge AI (Indian Sign Language bidirectional translator).
You receive a sequence of already-recognized Indian Sign Language (ISL) vocabulary labels.
Convert the sequence into exactly ONE natural English sentence.

Rules:
1. Preserve the meaning of the recognized signs.
2. Do not invent unrelated events, entities, times, or stories.
3. The vocabulary lacks pronouns and auxiliary verbs; add natural grammatical words (e.g., "I", "am", "to", "the", "want") only as necessary to form natural English.
4. Keep the output concise and grammatically correct.
5. Return ONLY the final English sentence.
6. Do NOT return explanations, prefixes, quotes, markdown formatting, or JSON.`;

// Generous free-tier quota models first
export const DEFAULT_CANDIDATE_MODELS = [
  "gemini-1.5-flash",
  "gemini-1.5-flash-8b",
  "gemini-2.0-flash",
  "gemini-2.0-flash-lite",
  "gemini-1.5-flash-latest",
  "gemini-1.5-flash-002",
  "gemini-1.5-flash-001",
  "gemini-2.5-flash",
  "gemini-1.5-pro",
  "gemini-pro",
];

export const CANDIDATE_MODELS = DEFAULT_CANDIDATE_MODELS;

let activeResolvedModel: string | null = null;
let activeApiVersion = "v1beta";

// In-memory cache to prevent redundant API calls for duplicate sign sequences
const translationCache = new Map<string, string>();

/**
 * Checks if a model name represents a specialized non-text or audio/tts model.
 */
function isNonTextModel(name: string): boolean {
  const lower = name.toLowerCase();
  return (
    lower.includes("tts") ||
    lower.includes("audio") ||
    lower.includes("realtime") ||
    lower.includes("embedding") ||
    lower.includes("aqa") ||
    lower.includes("imagen") ||
    lower.includes("image-generation") ||
    lower.includes("whisper") ||
    lower.includes("robotics")
  );
}

/**
 * Sorts discovered models by preference for real-time text translation
 * (fast high-quota text flash models first).
 */
export function sortModelsByPreference(models: string[]): string[] {
  return [...models].sort((a, b) => {
    const score = (m: string) => {
      let s = 0;
      // High-quota flash models prioritized
      if (m.includes("1.5-flash-8b")) s += 85;
      else if (m.includes("1.5-flash")) s += 80;
      else if (m.includes("2.0-flash") && !m.includes("lite")) s += 75;
      else if (m.includes("2.0-flash-lite")) s += 70;
      else if (m.includes("2.5-flash")) s += 60;
      else if (m.includes("flash")) s += 50;
      else if (m.includes("pro")) s += 30;

      // Deprioritize preview / experimental / thinking
      if (m.includes("thinking")) s -= 20;
      if (m.includes("preview")) s -= 15;
      if (m.includes("exp") || m.includes("experimental")) s -= 10;
      return s;
    };
    return score(b) - score(a);
  });
}

/**
 * Universal model discovery: Queries Google's ListModels API (both v1beta and v1)
 * to find every model enabled for this specific API key that supports text generateContent.
 */
export async function listAvailableGeminiModels(
  apiKey?: string,
  signal?: AbortSignal
): Promise<string[]> {
  const key = (apiKey || getGeminiApiKey()).trim().replace(/^['"]|['"]$/g, "");
  if (!key) return [];

  const endpoints = [
    `https://generativelanguage.googleapis.com/v1beta/models?key=${key}`,
    `https://generativelanguage.googleapis.com/v1/models?key=${key}`,
  ];

  for (const listUrl of endpoints) {
    try {
      const res = await fetch(listUrl, { signal });
      if (res.ok) {
        const data = await res.json();
        const models: {
          name: string;
          supportedGenerationMethods?: string[];
          responseModalities?: string[];
        }[] = data?.models || [];

        const usable = models
          .filter((m) => {
            // Must support generateContent
            if (
              m.supportedGenerationMethods &&
              !m.supportedGenerationMethods.includes("generateContent")
            ) {
              return false;
            }
            // If response modalities are explicitly declared, must include TEXT
            if (
              m.responseModalities &&
              !m.responseModalities.some((mod) => mod.toUpperCase().includes("TEXT"))
            ) {
              return false;
            }
            // Must not be a TTS, audio-only, or embedding model
            const cleanName = m.name.replace(/^models\//, "");
            return !isNonTextModel(cleanName);
          })
          .map((m) => m.name.replace(/^models\//, ""));

        if (usable.length > 0) {
          return sortModelsByPreference(usable);
        }
      }
    } catch {
      /* continue to next endpoint */
    }
  }

  return [];
}

/**
 * Automatically discovers the optimal supported model for this API key.
 */
export async function discoverSupportedModel(
  apiKey: string,
  signal?: AbortSignal
): Promise<string> {
  const usable = await listAvailableGeminiModels(apiKey, signal);
  if (usable.length > 0) {
    return usable[0];
  }
  return "gemini-1.5-flash";
}

export type SentenceMood = "normal" | "happy" | "sad" | "angry";

/**
 * Interprets a sequence of recognized ISL signs into natural English.
 * Works universally with ANY Gemini API key and ANY supported model.
 * Supports emotional mood modulation (normal, happy, sad, angry).
 */
export async function interpretSignSequence(
  sequence: string[],
  moodOrSignal?: SentenceMood | AbortSignal,
  maybeSignal?: AbortSignal
): Promise<string> {
  if (!sequence || sequence.length === 0) {
    throw new Error("Cannot interpret an empty sign sequence.");
  }

  const mood: SentenceMood =
    typeof moodOrSignal === "string" ? moodOrSignal : "normal";
  const signal: AbortSignal | undefined =
    moodOrSignal instanceof AbortSignal ? moodOrSignal : maybeSignal;

  const rawSigns = sequence.join(" ");
  const cacheKey = `${mood}:${rawSigns.toLowerCase().trim()}`;

  // Return cached result if already interpreted to prevent wasting quota
  if (translationCache.has(cacheKey)) {
    return translationCache.get(cacheKey)!;
  }

  const apiKey = getGeminiApiKey().trim().replace(/^['"]|['"]$/g, "");
  if (!apiKey) {
    throw new Error(
      "Gemini API key is missing. Please add your key in Settings or VITE_GEMINI_API_KEY."
    );
  }

  let moodDirective = "";
  if (mood === "happy") {
    moodDirective = "\nTone: Enthusiastic, joyful, cheerful.";
  } else if (mood === "sad") {
    moodDirective = "\nTone: Somber, sorrowful, melancholic.";
  } else if (mood === "angry") {
    moodDirective = "\nTone: Frustrated, assertive, urgent or stern.";
  }

  const userPrompt = `Recognized ISL sequence: ${rawSigns}${moodDirective}\nNatural English sentence:`;

  const payload = {
    contents: [
      {
        parts: [
          { text: SYSTEM_PROMPT },
          { text: userPrompt },
        ],
      },
    ],
    generationConfig: {
      temperature: 0.2,
      maxOutputTokens: 64,
    },
  };

  // Determine model list to attempt
  const savedModel = getGeminiModelName();
  let candidateList: string[] = [];

  // If user selected a specific non-auto model, put it first (unless it's non-text)
  if (savedModel && savedModel !== "auto" && !isNonTextModel(savedModel)) {
    candidateList.push(savedModel);
  }

  if (activeResolvedModel && !candidateList.includes(activeResolvedModel)) {
    candidateList.push(activeResolvedModel);
  }

  // Auto-discover models for this key if we haven't resolved one yet
  if (candidateList.length === 0) {
    const discovered = await listAvailableGeminiModels(apiKey, signal);
    if (discovered.length > 0) {
      candidateList.push(...discovered);
    }
  }

  // Always append comprehensive default candidates as safety fallbacks
  for (const m of DEFAULT_CANDIDATE_MODELS) {
    if (!candidateList.includes(m) && !isNonTextModel(m)) {
      candidateList.push(m);
    }
  }

  const apiVersions = ["v1beta", "v1"];
  let lastErrorDetail = "";
  let hitRateLimit = false;

  for (const model of candidateList) {
    for (const version of apiVersions) {
      const url = `https://generativelanguage.googleapis.com/${version}/models/${model}:generateContent?key=${apiKey}`;

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          signal,
        });

        if (response.ok) {
          activeResolvedModel = model;
          activeApiVersion = version;

          const data = await response.json();
          const text =
            data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || "";

          if (!text) {
            throw new Error("Gemini returned an empty interpretation.");
          }

          const cleaned = text.replace(/^["']|["']$/g, "").trim();
          translationCache.set(cacheKey, cleaned);
          return cleaned;
        }

        // If 404, this specific model or version isn't supported; silently proceed to next
        if (response.status === 404) {
          continue;
        }

        let errorDetail = "";
        try {
          const errJson = await response.json();
          errorDetail = errJson?.error?.message || response.statusText;
        } catch {
          errorDetail = response.statusText;
        }

        lastErrorDetail = errorDetail;

        // If rate limit (429) on this model, DO NOT throw!
        // Another model (e.g. 1.5-flash vs 2.0-flash vs 1.5-flash-8b) has a separate quota pool.
        if (response.status === 429) {
          hitRateLimit = true;
          continue;
        }

        // If error is about modality or model feature incompatibility (e.g. TTS / audio model),
        // silently continue to the next model in the list.
        const isModalityOrModelError =
          /modalit|not supported by the model|unsupported model|invalid model/i.test(
            errorDetail
          );
        if (isModalityOrModelError) {
          continue;
        }

        // Only genuine API key authentication failures should abort
        const isAuthError =
          /API_KEY_INVALID|API key not valid|CREDENTIALS_INVALID|UNAUTHENTICATED/i.test(
            errorDetail
          );
        if (isAuthError) {
          throw new Error(`Gemini API authorization error: ${errorDetail}`);
        }
      } catch (err: unknown) {
        if (
          err instanceof Error &&
          (err.name === "AbortError" || /authorization/i.test(err.message))
        ) {
          throw err;
        }
        lastErrorDetail = err instanceof Error ? err.message : String(err);
      }
    }
  }

  if (hitRateLimit) {
    throw new Error(
      "Gemini API rate limit reached across available models. Google AI Studio free tier limits requests per minute. Please wait 15–30 seconds and try again."
    );
  }

  throw new Error(
    `Gemini API could not generate content with the provided key. ${
      lastErrorDetail || "Please verify that the API key is active in Google AI Studio."
    }`
  );
}
