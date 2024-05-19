import keyboard

events = keyboard.read_event()

key = events.name
print(key)