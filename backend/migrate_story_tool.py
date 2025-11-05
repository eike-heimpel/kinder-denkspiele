#!/usr/bin/env python3
"""
Generic tool to find and migrate old Märchenweber stories.
Searches by username and optionally by content snippet.
"""
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from bson import ObjectId
from datetime import datetime

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')


async def find_user(username: str):
    """Find user by username across all databases."""
    uri = os.getenv('MONGODB_URI')
    client = AsyncIOMotorClient(uri)

    # Check common databases
    databases = ['humanbenchmark', 'myFirstDatabase', 'test']

    for db_name in databases:
        db = client[db_name]
        if 'users' not in await db.list_collection_names():
            continue

        # Try different field names
        for field in ['username', 'name']:
            user = await db.users.find_one({field: username})
            if user:
                print(f'✅ Found user "{username}" in {db_name}.users')
                print(f'   User ID: {user["_id"]}')
                client.close()
                return str(user['_id']), db_name

    client.close()
    return None, None


async def find_sessions(user_id: str, search_text: str = None):
    """Find game sessions for a user."""
    uri = os.getenv('MONGODB_URI')
    client = AsyncIOMotorClient(uri)
    db = client['humanbenchmark']

    query = {
        'gameType': 'maerchenweber',
        'userId': user_id
    }

    sessions = await db.gamesessions.find(query).to_list(None)

    print(f'\n📚 Found {len(sessions)} Märchenweber session(s) for this user:\n')

    matching = []

    for idx, session in enumerate(sessions, 1):
        session_id = str(session.get('_id'))
        char = session.get('character_name', 'N/A')
        theme = session.get('story_theme', 'N/A')
        history = session.get('history', [])
        has_turns = 'turns' in session and len(session.get('turns', [])) > 0

        # Check if already migrated
        if has_turns:
            print(f'--- Session {idx} (⚠️ ALREADY MIGRATED) ---')
        else:
            print(f'--- Session {idx} ---')

        print(f'ID: {session_id}')
        print(f'Character: {char}')
        print(f'Theme: {theme}')
        print(f'History entries: {len(history)}')
        print(f'Has turns: {has_turns}')

        # Search in history text
        if search_text and history:
            found = False
            for entry in history:
                if isinstance(entry, str) and search_text.lower() in entry.lower():
                    found = True
                    break
            if found:
                print(f'✅ Contains "{search_text}"')
            else:
                print(f'❌ Does not contain "{search_text}"')
                continue  # Skip if searching and not found

        if history and not has_turns:
            # Preview first story text
            first_text = history[0] if history else ''
            preview = first_text[:100] + '...' if len(first_text) > 100 else first_text
            print(f'Preview: {preview}')

        matching.append(session)
        print()

    client.close()
    return matching


async def migrate_session(session_id: str, dry_run: bool = True):
    """Migrate a session from history to turns format."""
    uri = os.getenv('MONGODB_URI')
    client = AsyncIOMotorClient(uri)
    db = client['humanbenchmark']

    session = await db.gamesessions.find_one({'_id': ObjectId(session_id)})

    if not session:
        print(f'❌ Session {session_id} not found')
        client.close()
        return False

    print(f'\n📖 Migrating session: {session_id}')
    print(f'   Character: {session.get("character_name", "N/A")}')
    print(f'   Theme: {session.get("story_theme", "N/A")}')

    # Check if already migrated
    if 'turns' in session and len(session.get('turns', [])) > 0:
        print('⚠️  This session already has turns!')
        overwrite = input('   Overwrite existing turns? (yes/no): ').strip().lower()
        if overwrite != 'yes':
            print('❌ Migration cancelled')
            client.close()
            return False

    history = session.get('history', [])

    if not history:
        print('❌ No history to migrate')
        client.close()
        return False

    print(f'\n🔄 Converting {len(history)} history entries to turns...')

    turns = []
    turn_number = 0

    # History format: alternating story text and user choices
    # Story text, "[Wahl]: choice text", story text, "[Wahl]: choice text", ...
    i = 0
    while i < len(history):
        entry = history[i]

        # Skip if this is a choice (shouldn't happen as first entry)
        if isinstance(entry, str) and entry.startswith('[Wahl]:'):
            i += 1
            continue

        story_text = entry if isinstance(entry, str) else str(entry)

        # Look for user choice in next entry
        user_choice = None
        if i + 1 < len(history):
            next_entry = history[i + 1]
            if isinstance(next_entry, str) and next_entry.startswith('[Wahl]:'):
                user_choice = next_entry.replace('[Wahl]:', '').strip()
                i += 2  # Skip both story and choice
            else:
                i += 1  # Only story, no choice yet
        else:
            i += 1

        # Generate placeholder choices (3 required)
        placeholder_choices = [
            "Geschichte fortsetzen...",
            "Geschichte fortsetzen...",
            "Geschichte fortsetzen..."
        ]

        turn_data = {
            'round': turn_number,  # Backend expects 'round', not 'turn_number'
            'choice_made': user_choice,  # Backend expects 'choice_made', not 'user_choice'
            'story_text': story_text,
            'choices': placeholder_choices,  # Frontend needs 3 choices
            'image_url': None,
            'fun_nugget': "",  # Backend requires this field
            'started_at': session.get('createdAt', datetime.utcnow()),
            'completed_at': session.get('createdAt', datetime.utcnow())
        }

        turns.append(turn_data)

        # Show preview
        preview = story_text[:80] + '...' if len(story_text) > 80 else story_text
        print(f'  Turn {turn_number}: {preview}')
        if user_choice:
            print(f'    → Choice: {user_choice}')

        turn_number += 1

    print(f'\n✅ Created {len(turns)} turns')

    if dry_run:
        print('\n🔍 DRY RUN - No changes made')
        return True

    # Apply migration
    result = await db.gamesessions.update_one(
        {'_id': ObjectId(session_id)},
        {
            '$set': {
                'turns': turns,
                'migrated_at': datetime.utcnow(),
                'migration_note': 'Migrated from old string history format'
            }
        }
    )

    if result.modified_count > 0:
        print('\n✅ Migration successful!')
        client.close()
        return True
    else:
        print('\n❌ Migration failed')
        client.close()
        return False


async def main():
    print('🔍 Märchenweber Story Migration Tool\n')

    # Step 1: Get username
    username = input('Enter username: ').strip()
    if not username:
        print('❌ Username required')
        return

    # Step 2: Find user
    print(f'\n🔎 Searching for user "{username}"...')
    user_id, db_name = await find_user(username)

    if not user_id:
        print(f'\n❌ User "{username}" not found in any database')
        return

    # Step 3: Optional content search
    search_text = input('\nSearch for specific content (or press Enter to skip): ').strip()

    # Step 4: Find sessions
    print(f'\n🔎 Searching for sessions...')
    sessions = await find_sessions(user_id, search_text if search_text else None)

    if not sessions:
        print('\n❌ No matching sessions found')
        return

    # Filter out already migrated sessions
    unmigrated = [s for s in sessions if 'turns' not in s or not s.get('turns')]

    if not unmigrated:
        print('\n⚠️  All sessions are already migrated!')
        return

    print(f'\n✅ Found {len(unmigrated)} session(s) that need migration')

    # Step 5: Select session
    if len(unmigrated) == 1:
        selected = unmigrated[0]
        print(f'\n🎯 Automatically selected the only session: {selected["_id"]}')
    else:
        print('\n📋 Which session do you want to migrate?')
        for idx, s in enumerate(unmigrated, 1):
            char = s.get('character_name', 'N/A')
            theme = s.get('story_theme', 'N/A')
            print(f'  {idx}. Character: {char}, Theme: {theme}')

        choice = input(f'\nEnter number (1-{len(unmigrated)}) or "all": ').strip()

        if choice.lower() == 'all':
            selected = unmigrated
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(unmigrated):
                    selected = [unmigrated[idx]]
                else:
                    print('❌ Invalid selection')
                    return
            except ValueError:
                print('❌ Invalid input')
                return

    # Step 6: Migrate
    if not isinstance(selected, list):
        selected = [selected]

    for session in selected:
        session_id = str(session['_id'])

        # First dry run
        await migrate_session(session_id, dry_run=True)

        # Confirm
        confirm = input('\n❓ Apply migration? (yes/no): ').strip().lower()
        if confirm == 'yes':
            await migrate_session(session_id, dry_run=False)
        else:
            print('❌ Migration cancelled')

        if len(selected) > 1:
            print('\n' + '='*60 + '\n')


if __name__ == '__main__':
    asyncio.run(main())
