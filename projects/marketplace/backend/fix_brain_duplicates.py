#!/usr/bin/env python3
"""Fix duplicate verified lines in brain API."""

# Read the file
with open('api/brain.py', 'r') as f:
    content = f.read()

# Fix all the response objects to remove duplicates and fix field names
content = content.replace(
    '''upvotes=entry.helpful_votes,
        downvotes=entry.unhelpful_votes,
        verified=entry.verified,
        verified=entry.verified
    )''',
    '''helpful_votes=entry.helpful_votes,
        unhelpful_votes=entry.unhelpful_votes,
        verified=entry.verified
    )'''
)

# Also fix single line versions
content = content.replace('upvotes=entry.helpful_votes', 'helpful_votes=entry.helpful_votes')
content = content.replace('downvotes=entry.unhelpful_votes', 'unhelpful_votes=entry.unhelpful_votes')

# Remove duplicate verified lines
import re
# Pattern: verified=entry.verified,\n        verified=entry.verified
content = re.sub(
    r'verified=entry\.verified,\s*verified=entry\.verified',
    'verified=entry.verified',
    content
)

# Write back
with open('api/brain.py', 'w') as f:
    f.write(content)

print("Fixed duplicates and field names")
