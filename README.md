# goit-pycore-hw-08

Homework 08 — Serialization (pickle)

## Features

- AddressBook based on OOP models: Field, Name, Phone, Birthday, Record, AddressBook
- Phone validation: exactly 10 digits
- Birthday validation: DD.MM.YYYY
- Upcoming birthdays for the next 7 days (weekend -> Monday)
- Persistence: save/load AddressBook using pickle (`addressbook.pkl`)

## Commands

1. `add [name] [phone]` — add contact or add phone to existing contact
2. `change [name] [old_phone] [new_phone]` — change phone
3. `phone [name]` — show phones
4. `all` — show all contacts
5. `add-birthday [name] [DD.MM.YYYY]` — add birthday
6. `show-birthday [name]` — show birthday
7. `birthdays` — list birthdays for next 7 days
8. `hello` — greeting
9. `close` or `exit` — exit and save data

## Run

```bash
python main.py

## Notes

Data is saved automatically when the program exits using `exit` or `close`.

All contacts are serialized using the **pickle** module and stored in the file:

`addressbook.pkl`

When the application starts again, the address book is automatically restored from this file.
```
