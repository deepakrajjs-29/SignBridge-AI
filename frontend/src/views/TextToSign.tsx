import React, { useState } from "react";
import { api } from "../api/client";
import { type SentenceMood } from "../api/gemini";
import { saveSentenceRecord } from "../api/sentenceHistory";
import {
  MicrophoneIcon,
  SparklesIcon,
  VolumeUpIcon,
  AlertCircleIcon,
  CheckCircleIcon,
} from "../components/Icons";

export interface MoodProfile {
  id: SentenceMood;
  label: string;
  emoji: string;
  pitch: number;
  rate: number;
  volume: number;
  activeClass: string;
  badgeClass: string;
  description: string;
}

export const MOODS: MoodProfile[] = [
  {
    id: "normal",
    label: "Normal",
    emoji: "😐",
    pitch: 1.0,
    rate: 1.0,
    volume: 1.0,
    activeClass: "bg-slate-700 text-white ring-2 ring-slate-400 shadow-md",
    badgeClass: "bg-slate-800 text-slate-300 border border-slate-700",
    description: "Neutral & natural conversational tone",
  },
  {
    id: "happy",
    label: "Happy",
    emoji: "😊",
    pitch: 1.35,
    rate: 1.15,
    volume: 1.0,
    activeClass: "bg-emerald-600 text-white ring-2 ring-emerald-400 shadow-emerald-500/30 shadow-lg",
    badgeClass: "bg-emerald-950/80 text-emerald-300 border border-emerald-800",
    description: "Energetic, bright & upbeat tone",
  },
  {
    id: "sad",
    label: "Sad",
    emoji: "😔",
    pitch: 0.72,
    rate: 0.82,
    volume: 0.85,
    activeClass: "bg-blue-600 text-white ring-2 ring-blue-400 shadow-blue-500/30 shadow-lg",
    badgeClass: "bg-blue-950/80 text-blue-300 border border-blue-800",
    description: "Soft, slower & somber tone",
  },
  {
    id: "angry",
    label: "Angry",
    emoji: "😠",
    pitch: 0.85,
    rate: 1.25,
    volume: 1.0,
    activeClass: "bg-rose-600 text-white ring-2 ring-rose-400 shadow-rose-500/30 shadow-lg",
    badgeClass: "bg-rose-950/80 text-rose-300 border border-rose-800",
    description: "Firm, urgent & emphatic tone",
  },
];

// Offline fallback & dictionary mapping for the 50 ISL vocabulary classes
export const ISL_VOCAB_DICTIONARY: Record<string, { class_id: string; label: string }> = {
  hello: { class_id: "ISL_001", label: "Hello" },
  hi: { class_id: "ISL_001", label: "Hello" },
  hey: { class_id: "ISL_001", label: "Hello" },
  "thank you": { class_id: "ISL_002", label: "Thank You" },
  thanks: { class_id: "ISL_002", label: "Thank You" },
  thank: { class_id: "ISL_002", label: "Thank You" },
  please: { class_id: "ISL_003", label: "Please" },
  pls: { class_id: "ISL_003", label: "Please" },
  market: { class_id: "ISL_004", label: "Market" },
  yes: { class_id: "ISL_005", label: "Yes" },
  yeah: { class_id: "ISL_005", label: "Yes" },
  yep: { class_id: "ISL_005", label: "Yes" },
  no: { class_id: "ISL_006", label: "No" },
  nope: { class_id: "ISL_006", label: "No" },
  morning: { class_id: "ISL_007", label: "Morning" },
  "good morning": { class_id: "ISL_008", label: "Good Morning" },
  "good night": { class_id: "ISL_009", label: "Good Night" },
  evening: { class_id: "ISL_010", label: "Evening" },
  "good evening": { class_id: "ISL_010", label: "Evening" },
  help: { class_id: "ISL_011", label: "Help" },
  water: { class_id: "ISL_012", label: "Water" },
  food: { class_id: "ISL_013", label: "Food" },
  man: { class_id: "ISL_014", label: "Man" },
  friend: { class_id: "ISL_015", label: "Friend" },
  friends: { class_id: "ISL_015", label: "Friend" },
  family: { class_id: "ISL_016", label: "Family" },
  doctor: { class_id: "ISL_017", label: "Doctor" },
  dr: { class_id: "ISL_017", label: "Doctor" },
  medicine: { class_id: "ISL_018", label: "Medicine" },
  medicines: { class_id: "ISL_018", label: "Medicine" },
  house: { class_id: "ISL_019", label: "House" },
  home: { class_id: "ISL_019", label: "House" },
  woman: { class_id: "ISL_020", label: "Woman" },
  mother: { class_id: "ISL_021", label: "Mother" },
  mom: { class_id: "ISL_021", label: "Mother" },
  happy: { class_id: "ISL_022", label: "Happy" },
  sad: { class_id: "ISL_023", label: "Sad" },
  day: { class_id: "ISL_024", label: "Day" },
  time: { class_id: "ISL_025", label: "Time" },
  today: { class_id: "ISL_026", label: "Today" },
  tomorrow: { class_id: "ISL_027", label: "Tomorrow" },
  school: { class_id: "ISL_028", label: "School" },
  work: { class_id: "ISL_029", label: "Work" },
  office: { class_id: "ISL_030", label: "Office" },
  night: { class_id: "ISL_031", label: "Night" },
  what: { class_id: "ISL_032", label: "What" },
  where: { class_id: "ISL_033", label: "Where" },
  she: { class_id: "ISL_034", label: "She" },
  go: { class_id: "ISL_035", label: "Go" },
  going: { class_id: "ISL_035", label: "Go" },
  he: { class_id: "ISL_036", label: "He" },
  sister: { class_id: "ISL_037", label: "Sister" },
  tea: { class_id: "ISL_038", label: "Tea" },
  student: { class_id: "ISL_039", label: "Student" },
  drink: { class_id: "ISL_040", label: "Drink" },
  drinking: { class_id: "ISL_040", label: "Drink" },
  father: { class_id: "ISL_041", label: "Father" },
  dad: { class_id: "ISL_041", label: "Father" },
  child: { class_id: "ISL_042", label: "Child" },
  children: { class_id: "ISL_042", label: "Child" },
  kid: { class_id: "ISL_042", label: "Child" },
  kids: { class_id: "ISL_042", label: "Child" },
  car: { class_id: "ISL_043", label: "Car" },
  cars: { class_id: "ISL_043", label: "Car" },
  eat: { class_id: "ISL_044", label: "Eat" },
  eating: { class_id: "ISL_044", label: "Eat" },
  teacher: { class_id: "ISL_045", label: "Teacher" },
  sit: { class_id: "ISL_046", label: "Sit" },
  girl: { class_id: "ISL_047", label: "Girl" },
  boy: { class_id: "ISL_048", label: "Boy" },
  book: { class_id: "ISL_049", label: "Book" },
  books: { class_id: "ISL_049", label: "Book" },
  bus: { class_id: "ISL_050", label: "Bus" },
};

const SAMPLE_PHRASES = [
  "Hello doctor please help",
  "Good morning teacher",
  "Thank you friend",
  "Where school bus",
  "Water food please",
  "Today happy day",
];

export default function TextToSign() {
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<
    { word: string; class_id: string; label: string; supported: boolean }[] | null
  >(null);
  const [unsupported, setUnsupported] = useState<string[]>([]);
  const [errorNote, setErrorNote] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [selectedMood, setSelectedMood] = useState<SentenceMood>("normal");

  const [speechSupported] = useState(
    typeof window !== "undefined" &&
      ("SpeechRecognition" in window || "webkitSpeechRecognition" in window)
  );

  function speakText(text: string, mood: SentenceMood = selectedMood) {
    if (typeof window === "undefined" || !("speechSynthesis" in window) || !text.trim()) {
      return;
    }
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-IN";

      const profile = MOODS.find((m) => m.id === mood) || MOODS[0];
      utterance.pitch = profile.pitch;
      utterance.rate = profile.rate;
      utterance.volume = profile.volume;

      setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
    } catch {
      setIsSpeaking(false);
    }
  }

  function handleMoodChange(newMood: SentenceMood) {
    setSelectedMood(newMood);
    const textToSpeak = items && items.length > 0 ? items.map((i) => i.label).join(" ") : inputText;
    if (textToSpeak.trim()) {
      speakText(textToSpeak, newMood);
    }
  }

  async function handleConvert(textToUse = inputText) {
    const raw = textToUse.trim();
    if (!raw) return;
    setErrorNote("");
    setLoading(true);

    // Sanitize punctuation: replace commas, exclamation marks, question marks, semicolons with spaces
    // so words match backend dictionary and client dictionary cleanly
    const cleanedText = raw
      .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()?"'<>]/g, " ")
      .replace(/\s+/g, " ")
      .trim();

    try {
      let resolvedItems: { word: string; class_id: string; label: string; supported: boolean }[] = [];
      let unresolvedWords: string[] = [];

      try {
        const res = await api.textToSign(cleanedText);
        if (res.items && res.items.length > 0) {
          resolvedItems = res.items.map((it) => ({
            ...it,
            // A sign is supported if backend mapped a valid ISL class id:
            supported: it.supported || (Boolean(it.class_id) && it.class_id !== "UNMAPPED"),
          }));
        }
        unresolvedWords = res.unsupported_words || [];
      } catch {
        // If backend fails or is unreachable, fallback to client-side ISL vocabulary mapper
      }

      // If backend missed words or client fallback is needed:
      if (resolvedItems.length === 0) {
        const tokens = cleanedText.toLowerCase().split(/\s+/).filter(Boolean);
        const mappedList: { word: string; class_id: string; label: string; supported: boolean }[] = [];
        const unmappedList: string[] = [];

        let i = 0;
        while (i < tokens.length) {
          // Check two-word signs first (e.g., "thank you", "good morning", "good night")
          if (i + 1 < tokens.length) {
            const bigram = `${tokens[i]} ${tokens[i + 1]}`;
            if (ISL_VOCAB_DICTIONARY[bigram]) {
              const entry = ISL_VOCAB_DICTIONARY[bigram];
              mappedList.push({
                word: bigram,
                class_id: entry.class_id,
                label: entry.label,
                supported: true,
              });
              i += 2;
              continue;
            }
          }

          const unigram = tokens[i];
          if (ISL_VOCAB_DICTIONARY[unigram]) {
            const entry = ISL_VOCAB_DICTIONARY[unigram];
            mappedList.push({
              word: unigram,
              class_id: entry.class_id,
              label: entry.label,
              supported: true,
            });
          } else {
            unmappedList.push(unigram);
          }
          i++;
        }

        resolvedItems = mappedList;
        unresolvedWords = unmappedList;
      }

      setItems(resolvedItems);
      setUnsupported(unresolvedWords);

      if (resolvedItems.length > 0) {
        try {
          saveSentenceRecord({
            sentence: raw,
            signs: resolvedItems.map((s) => s.label.toUpperCase()),
            mood: selectedMood,
            timestamp: new Date().toLocaleString(),
            source: "text-to-sign",
          });
        } catch {
          /* ignore */
        }
      }

      // Auto-speak translated phrase if enabled in settings
      const autoSpeakEnabled = localStorage.getItem("sb_autospeak") !== "false";
      if (autoSpeakEnabled && resolvedItems.length > 0) {
        const spokenPhrase = resolvedItems.map((s) => s.label).join(", ");
        speakText(spokenPhrase, selectedMood);
      }
    } catch (e) {
      setErrorNote(e instanceof Error ? e.message : "Translation failed.");
    } finally {
      setLoading(false);
    }
  }

  function startVoiceInput() {
    setErrorNote("");
    const SpeechRecognition =
      (window as unknown as { SpeechRecognition?: any }).SpeechRecognition ||
      (window as unknown as { webkitSpeechRecognition?: any }).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setErrorNote("Speech recognition is not supported in this browser. Please type your phrase.");
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = "en-IN";
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onstart = () => setIsListening(true);
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        handleConvert(transcript);
      };
      recognition.onerror = (event: any) => {
        setIsListening(false);
        setErrorNote(`Microphone error: ${event.error || "failed to capture speech"}.`);
      };
      recognition.onend = () => setIsListening(false);

      recognition.start();
    } catch {
      setIsListening(false);
      setErrorNote("Could not activate microphone. Check browser permissions.");
    }
  }

  const activeMoodProfile = MOODS.find((m) => m.id === selectedMood) || MOODS[0];

  return (
    <div className="space-y-6 max-w-4xl animate-in fade-in duration-200">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <SparklesIcon className="w-6 h-6 text-brand-600 dark:text-brand-400" />
          Text & Voice to Indian Sign Language (ISL)
        </h2>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Type or speak everyday phrases to translate them into structured ISL sign sequences against the 50-class vocabulary, with emotional voice synthesis.
        </p>
      </div>

      {/* Mood Selector Controls */}
      <div className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Voice Tone & Emotional Mood
          </span>
          <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${activeMoodProfile.badgeClass}`}>
            Active: {activeMoodProfile.emoji} {activeMoodProfile.label}
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
          {MOODS.map((m) => {
            const isSelected = selectedMood === m.id;
            return (
              <button
                key={m.id}
                type="button"
                onClick={() => handleMoodChange(m.id)}
                className={`p-3 rounded-lg border text-left transition flex flex-col gap-1 ${
                  isSelected
                    ? m.activeClass
                    : "bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700/80 hover:bg-slate-100 dark:hover:bg-slate-700/80 text-slate-700 dark:text-slate-200"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">{m.emoji}</span>
                  <span className="text-sm font-bold">{m.label}</span>
                </div>
                <span
                  className={`text-[11px] leading-snug line-clamp-1 ${
                    isSelected ? "text-white/90" : "text-slate-500 dark:text-slate-400"
                  }`}
                >
                  {m.description}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Input Box & Actions */}
      <div className="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
        <label htmlFor="phrase-input" className="block text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
          Enter Phrase or Question
        </label>
        <div className="flex gap-2">
          <input
            id="phrase-input"
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleConvert()}
            placeholder="e.g. Hello doctor, please help! Where is water?"
            className="flex-1 px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white text-base focus:ring-2 focus:ring-brand-500"
          />
          <button
            type="button"
            onClick={() => handleConvert()}
            disabled={loading || !inputText.trim()}
            className="px-6 py-3 rounded-lg bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-semibold transition flex items-center gap-2"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : (
              <SparklesIcon className="w-5 h-5" />
            )}
            Translate
          </button>
          {speechSupported && (
            <button
              type="button"
              onClick={startVoiceInput}
              disabled={isListening}
              className={`px-4 py-3 rounded-lg border font-medium transition flex items-center gap-2 ${
                isListening
                  ? "bg-rose-50 dark:bg-rose-950/80 border-rose-400 text-rose-600 animate-pulse"
                  : "bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700"
              }`}
              title="Speak into microphone"
              aria-label="Microphone input"
            >
              <MicrophoneIcon className="w-5 h-5" />
              {isListening ? "Listening…" : "Voice"}
            </button>
          )}
        </div>

        {/* Quick Sample Prompts */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-xs text-slate-400 font-medium">Quick examples:</span>
          {SAMPLE_PHRASES.map((sample) => (
            <button
              key={sample}
              type="button"
              onClick={() => {
                setInputText(sample);
                handleConvert(sample);
              }}
              className="text-xs px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-brand-950/40 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-400 transition"
            >
              {sample}
            </button>
          ))}
        </div>

        {errorNote && (
          <div role="alert" className="p-3 rounded-lg bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-sm flex items-center gap-2">
            <AlertCircleIcon className="w-4 h-4 shrink-0" />
            <span>{errorNote}</span>
          </div>
        )}
      </div>

      {/* Results Sequence Cards */}
      {items && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <span>ISL Sign Sequence</span>
              <span className="text-xs font-normal px-2.5 py-0.5 rounded-full bg-brand-100 dark:bg-brand-900/60 text-brand-700 dark:text-brand-300">
                {items.length} signs
              </span>
            </h3>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() =>
                  speakText(
                    items.length > 0 ? items.map((i) => i.label).join(", ") : inputText,
                    selectedMood
                  )
                }
                className={`text-xs font-medium px-3 py-1.5 rounded-lg border transition flex items-center gap-1.5 ${
                  isSpeaking
                    ? "bg-brand-500 text-white border-brand-500 animate-pulse"
                    : "bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700"
                }`}
              >
                <VolumeUpIcon className="w-4 h-4" />
                {isSpeaking ? `Speaking (${activeMoodProfile.emoji})…` : `Speak in ${activeMoodProfile.label} Tone`}
              </button>
            </div>
          </div>

          {items.length === 0 ? (
            <div className="p-8 text-center rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-dashed border-slate-300 dark:border-slate-700 text-slate-500">
              No matching ISL signs found for this phrase. Try words like &ldquo;hello&rdquo;, &ldquo;help&rdquo;, &ldquo;water&rdquo;, &ldquo;doctor&rdquo;, or &ldquo;thank you&rdquo;.
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              {items.map((it, idx) => (
                <div
                  key={`${it.word}-${idx}`}
                  className={`p-4 rounded-xl border transition shadow-sm space-y-2 group hover:border-brand-500 ${
                    it.supported
                      ? "bg-white dark:bg-slate-900 border-brand-200 dark:border-slate-700"
                      : "bg-amber-50/50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900/60"
                  }`}
                >
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span className="font-mono font-bold text-brand-600 dark:text-brand-400">#{idx + 1}</span>
                    <span className="font-mono">{it.class_id || "UNMAPPED"}</span>
                  </div>
                  <div className="text-center py-4 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-100 dark:border-slate-800 flex flex-col items-center justify-center relative">
                    <span className="text-xl font-extrabold text-slate-900 dark:text-white uppercase tracking-wide">
                      {it.label || it.word}
                    </span>
                    <button
                      type="button"
                      onClick={() => speakText(it.label || it.word, selectedMood)}
                      className="mt-2 text-xs text-slate-500 hover:text-brand-600 dark:hover:text-brand-400 flex items-center gap-1 opacity-80 group-hover:opacity-100 transition"
                      title="Speak sign"
                    >
                      <VolumeUpIcon className="w-3.5 h-3.5" />
                      <span>Listen</span>
                    </button>
                  </div>
                  <div className="flex items-center justify-between pt-1">
                    <span className="text-xs text-slate-500 dark:text-slate-400 truncate max-w-[90px]">
                      &ldquo;{it.word}&rdquo;
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                        it.supported
                          ? "bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300"
                          : "bg-amber-100 dark:bg-amber-950/80 text-amber-700 dark:text-amber-300"
                      }`}
                    >
                      {it.supported ? (
                        <>
                          <CheckCircleIcon className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                          Supported
                        </>
                      ) : (
                        "Unmapped"
                      )}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {unsupported.length > 0 && (
            <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-200 text-sm space-y-1">
              <p className="font-semibold flex items-center gap-2">
                <AlertCircleIcon className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                Vocabulary Notice:
              </p>
              <p className="text-xs text-amber-700 dark:text-amber-300">
                The words <strong>{unsupported.join(", ")}</strong> are auxiliary grammar words or outside the 50 Indian Sign Language classes. The core signs have been structured above.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
