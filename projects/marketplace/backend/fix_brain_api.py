#!/usr/bin/env python3
"""Fix brain API field names to match BrainEntry model."""

# Read the file
with open('api/brain.py', 'r') as f:
    lines = f.readlines()

# Process each line
fixed_lines = []
for line in lines:
    # Fix response objects
    line = line.replace('entry_type=entry.type', 'type=entry.type')
    line = line.replace('entry_type=entry.entry_type', 'type=entry.type')
    line = line.replace('is_public=entry.is_public', 'verified=entry.verified')
    line = line.replace('is_public=entry.status', 'verified=entry.verified')
    line = line.replace('is_verified=entry.verified', 'verified=entry.verified')
    line = line.replace('upvotes=entry.upvotes', 'helpful_votes=entry.helpful_votes')
    line = line.replace('downvotes=entry.downvotes', 'unhelpful_votes=entry.unhelpful_votes')

    # Fix field references that weren't caught
    line = line.replace('entry.entry_type', 'entry.type')
    line = line.replace('entry.is_public', 'entry.status')
    line = line.replace('entry.is_verified', 'entry.verified')
    line = line.replace('entry.upvotes', 'entry.helpful_votes')
    line = line.replace('entry.downvotes', 'entry.unhelpful_votes')

    fixed_lines.append(line)

# Write back
with open('api/brain.py', 'w') as f:
    f.writelines(fixed_lines)

print("Fixed all field references")
