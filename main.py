from __future__ import annotations

from collections import UserDict
from dataclasses import dataclass
from datetime import datetime, date, timedelta
import pickle
from typing import Optional, List, Tuple


# -----------------------------
# Core models
# -----------------------------

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value: str):
        value = value.strip()
        if not self._is_valid(value):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

    @staticmethod
    def _is_valid(value: str) -> bool:
        return value.isdigit() and len(value) == 10


class Birthday(Field):
    def __init__(self, value: str):
        value = value.strip()
        try:
            dt = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(dt)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None

    def add_phone(self, phone: str) -> None:
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        phone_obj = self.find_phone(phone)
        if not phone_obj:
            raise ValueError("Phone number not found.")
        self.phones.remove(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError("Old phone number not found.")
        phone_obj.value = Phone(new_phone).value

    def find_phone(self, phone: str) -> Optional[Phone]:
        phone = phone.strip()
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones) if self.phones else "—"
        bday_str = str(self.birthday) if self.birthday else "—"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {bday_str}"


class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(name)

    def delete(self, name: str) -> None:
        if name not in self.data:
            raise KeyError("Contact not found.")
        del self.data[name]

    # --- HW07 function: upcoming birthdays for next 7 days
    def get_upcoming_birthdays(self) -> List[dict]:
        """
        Returns list like:
        [{"name": "John", "congratulation_date": "05.03.2026"}, ...]
        If birthday falls on weekend -> moved to Monday.
        Handles 29.02 safely (non-leap years).
        """
        today = date.today()
        end_date = today + timedelta(days=7)

        result: List[dict] = []

        for record in self.data.values():
            if not record.birthday:
                continue

            bday = record.birthday.value  # date object

            # --- FIX for 29.02: try replace, if invalid -> fallback to 28.02
            try:
                bday_this_year = bday.replace(year=today.year)
            except ValueError:
                # happens for Feb 29 in non-leap year
                bday_this_year = date(today.year, 2, 28)

            # if already passed this year -> next year
            if bday_this_year < today:
                next_year = today.year + 1
                try:
                    bday_this_year = bday.replace(year=next_year)
                except ValueError:
                    bday_this_year = date(next_year, 2, 28)

            if today <= bday_this_year <= end_date:
                congratulation_date = bday_this_year

                # переносимо якщо субота/неділя
                if congratulation_date.weekday() == 5:  # Saturday
                    congratulation_date += timedelta(days=2)
                elif congratulation_date.weekday() == 6:  # Sunday
                    congratulation_date += timedelta(days=1)

                result.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": congratulation_date.strftime("%d.%m.%Y"),
                    }
                )

        return result


# -----------------------------
# Persistence (HW08)
# -----------------------------

DEFAULT_STORAGE = "addressbook.pkl"


def save_data(book: AddressBook, filename: str = DEFAULT_STORAGE) -> None:
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename: str = DEFAULT_STORAGE) -> AddressBook:
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
            # safety: if file contains something wrong, fallback
            return data if isinstance(data, AddressBook) else AddressBook()
    except FileNotFoundError:
        return AddressBook()
    except Exception:
        # if file is corrupted, return new book
        return AddressBook()


# -----------------------------
# CLI helpers
# -----------------------------

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Error: {e}"
        except KeyError as e:
            return f"Error: {e}"
        except IndexError:
            return "Error: Not enough arguments."
    return wrapper


def parse_input(user_input: str) -> Tuple[str, List[str]]:
    user_input = user_input.strip()
    if not user_input:
        return "", []
    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args


# -----------------------------
# Commands
# -----------------------------

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    msg = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        msg = "Contact added."
    if phone:
        record.add_phone(phone)
    return msg


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return "Error: Contact not found."
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Error: Contact not found."
    if not record.phones:
        return f"{name}: —"
    return f"{name}: " + "; ".join(p.value for p in record.phones)


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."
    lines = []
    for record in book.data.values():
        lines.append(str(record))
    return "\n".join(lines)


@input_error
def add_birthday_cmd(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return "Error: Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday_cmd(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Error: Contact not found."
    if not record.birthday:
        return "Birthday is not set."
    return f"{record.name.value}: {record.birthday}"


@input_error
def birthdays_cmd(book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    lines = ["Upcoming birthdays:"]
    for item in upcoming:
        lines.append(f"- {item['name']}: {item['congratulation_date']}")
    return "\n".join(lines)


# -----------------------------
# Main loop
# -----------------------------

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday_cmd(args, book))

        elif command == "show-birthday":
            print(show_birthday_cmd(args, book))

        elif command == "birthdays":
            print(birthdays_cmd(book))

        elif command == "":
            print("Please enter a command.")

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()