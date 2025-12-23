#!/usr/bin/env python3
import json
from collections import Counter

non_move_count = 0
move_count = 0
actions = []

with open('mac_firefox_bookmark_shortcuts_guide/events.jsonl', 'r') as f:
    for line in f:
        if line.strip():
            event = json.loads(line)
            action = event.get('action')
            if action == 'move':
                move_count += 1
            else:
                non_move_count += 1
                actions.append(action)

print(f'Total events: {non_move_count + move_count}')
print(f'Move actions: {move_count}')
print(f'Non-move actions: {non_move_count}')
print(f'\nNon-move action breakdown:')
action_counts = Counter(actions)
for action, count in sorted(action_counts.items()):
    print(f'  {action}: {count}')

