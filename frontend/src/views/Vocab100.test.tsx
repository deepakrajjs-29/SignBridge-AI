// @vitest-environment jsdom
import { expect, test, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import Vocab from "./Vocab";
import { api, type ClassItem } from "../api/client";

vi.mock("../api/client", async (importOriginal) => {
  const mod = await importOriginal<typeof import("../api/client")>();
  return { ...mod, api: { ...mod.api, classes: vi.fn() } };
});

const LABELS_50 = [
  "Hello", "Thank You", "Please", "Market", "Yes", "No", "Morning",
  "Good Morning", "Good Night", "Evening", "Help", "Water", "Food", "Man",
  "Friend", "Family", "Doctor", "Medicine", "House", "Woman", "Mother",
  "Happy", "Sad", "Day", "Time", "Today", "Tomorrow", "School", "Work",
  "Office", "Night", "What", "Where", "She", "Go", "He", "Sister", "Tea",
  "Student", "Drink", "Father", "Child", "Car", "Eat", "Teacher", "Sit",
  "Girl", "Boy", "Book", "Bus",
];

const LABELS_NEW_50 = [
  "Sorry", "Welcome", "Bye", "Love", "Good", "Bad", "Name", "How", "When",
  "Why", "Who", "Which", "Want", "Need", "Like", "Come", "Stay", "Wait",
  "Stop", "Start", "Open", "Close", "Take", "Give", "Buy", "Pay", "Walk",
  "Speak", "Listen", "Look", "Read", "Write", "Milk", "Rice", "Bread",
  "Fruit", "Hospital", "Pain", "Road", "Train", "Station", "City", "Village",
  "Shop", "Bank", "Park", "Week", "Month", "Year", "Yesterday",
];

const CLASSES_100: ClassItem[] = [...LABELS_50, ...LABELS_NEW_50].map((label, i) => {
  const class_id = `ISL_${String(i + 1).padStart(3, "0")}`;
  return { class_id, label, sign_type: "Dynamic", asset_uri: `/assets/${class_id}.jpg` };
});

test("vocab shows 100 photos", async () => {
  vi.mocked(api.classes).mockResolvedValue({
    success: true,
    count: 100,
    classes: CLASSES_100,
    request_id: "t8",
  });
  render(<Vocab />);
  expect(await screen.findAllByRole("img")).toHaveLength(100);
});
