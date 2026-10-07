import { type SentenceMood } from "./gemini";

export interface SentenceRecord {
  id: string;
  sentence: string;
  signs: string[];
  mood: SentenceMood;
  timestamp: string;
  sessionId?: string;
  source: "live" | "text-to-sign" | "session-reconstructed";
}

const STORAGE_KEY = "sb_sentence_history";

const INITIAL_SEED_SENTENCES: SentenceRecord[] = [
  {
    id: "sent_seed_1",
    sentence: "It is time for the family to eat food and drink together today.",
    signs: ["TODAY", "TIME", "FAMILY", "EAT", "DRINK"],
    mood: "happy",
    timestamp: "2026-10-07 17:43:38",
    sessionId: "sess_861fb795",
    source: "session-reconstructed",
  },
  {
    id: "sent_seed_2",
    sentence: "The child is resting at home and must take the medicine recommended by the doctor.",
    signs: ["CHILD", "HOUSE", "DOCTOR", "MEDICINE"],
    mood: "normal",
    timestamp: "2026-10-07 16:38:38",
    sessionId: "sess_861fb795",
    source: "session-reconstructed",
  },
  {
    id: "sent_seed_3",
    sentence: "He went to drink tea after taking the bus today.",
    signs: ["DAY", "TEA", "BUS", "HE"],
    mood: "normal",
    timestamp: "2026-10-07 16:36:28",
    sessionId: "sess_861fb795",
    source: "session-reconstructed",
  },
  {
    id: "sent_seed_4",
    sentence: "Hello doctor, please help me.",
    signs: ["HELLO", "DOCTOR", "PLEASE", "HELP"],
    mood: "sad",
    timestamp: "2026-10-07 15:45:10",
    sessionId: "sess_547cac99",
    source: "session-reconstructed",
  },
];

export function getSentenceHistory(): SentenceRecord[] {
  if (typeof window === "undefined" || !window.localStorage) {
    return INITIAL_SEED_SENTENCES;
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_SEED_SENTENCES));
      return INITIAL_SEED_SENTENCES;
    }
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed) && parsed.length > 0) {
      return parsed;
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(INITIAL_SEED_SENTENCES));
    return INITIAL_SEED_SENTENCES;
  } catch {
    return INITIAL_SEED_SENTENCES;
  }
}

export function saveSentenceRecord(
  record: Omit<SentenceRecord, "id">
): SentenceRecord {
  const newRecord: SentenceRecord = {
    ...record,
    id: `sent_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
  };

  if (typeof window === "undefined" || !window.localStorage) {
    return newRecord;
  }

  try {
    const current = getSentenceHistory();
    // Prepend new sentence to top of history
    const updated = [newRecord, ...current.filter((x) => x.sentence !== newRecord.sentence)];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated.slice(0, 200)));
    // Trigger custom storage event so other open tabs/views update instantly
    window.dispatchEvent(new Event("sentence_history_updated"));
  } catch {
    /* ignore storage error */
  }

  return newRecord;
}

export function deleteSentenceRecord(id: string): void {
  if (typeof window === "undefined" || !window.localStorage) return;
  try {
    const current = getSentenceHistory();
    const updated = current.filter((item) => item.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    window.dispatchEvent(new Event("sentence_history_updated"));
  } catch {
    /* ignore storage error */
  }
}

export function clearSentenceHistory(): void {
  if (typeof window === "undefined" || !window.localStorage) return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([]));
    window.dispatchEvent(new Event("sentence_history_updated"));
  } catch {
    /* ignore storage error */
  }
}
