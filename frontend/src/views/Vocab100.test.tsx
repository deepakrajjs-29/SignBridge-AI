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
  "Good", "Bad", "Why", "Which", "Stay", "Wait", "Open", "Close", "Give",
  "Walk", "Bread", "Pain", "Road", "City", "Shop", "Bank", "Month", "Year",
  "Yesterday", "Good Afternoon", "Good Evening", "You", "We", "They", "I",
  "Wife", "Husband", "Uncle", "Aunt", "Baby", "Pizza", "Mango", "Lunch",
  "Onion", "Lion", "Dog", "Cat", "Red", "Blue", "Green", "Saturday",
  "Sunday", "Hour", "Computer", "Movie", "Music", "Big", "Small", "Hot",
  "Cold",
];

const LABELS_NEW_9 = [
  "Library", "Meeting", "Holiday", "Pen", "Paper", "Chair", "Police",
  "Airport", "Manager",
];

const CLASSES_100: ClassItem[] = [...LABELS_50, ...LABELS_NEW_50, ...LABELS_NEW_9].map((label, i) => {
  const class_id = `ISL_${String(i + 1).padStart(3, "0")}`;
  return { class_id, label, sign_type: "Dynamic", asset_uri: `/assets/${class_id}.jpg` };
});

test("vocab shows 109 photos", async () => {
  vi.mocked(api.classes).mockResolvedValue({
    success: true,
    count: 109,
    classes: CLASSES_100,
    request_id: "t8",
  });
  render(<Vocab />);
  expect(await screen.findAllByRole("img")).toHaveLength(109);
});
