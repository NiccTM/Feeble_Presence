import asyncio
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

async def debug_sessions():
    print("--- SCANNING FOR MEDIA SESSIONS ---")
    try:
        manager = await MediaManager.request_async()
        sessions = manager.get_sessions()
        
        if not sessions:
            print("NO SESSIONS FOUND. Windows is returning an empty list.")
            return

        print(f"Found {len(sessions)} active sessions:")
        for i, session in enumerate(sessions):
            # Get basic info
            try:
                app_id = session.source_app_user_model_id
                playback_info = session.get_playback_info()
                status = playback_info.playback_status
                
                # Try to get title
                props = await session.try_get_media_properties_async()
                title = props.title if props else "Unknown Title"
                
                print(f"\n[Session {i+1}]")
                print(f"  App ID: {app_id}")
                print(f"  Title:  {title}")
                print(f"  Status: {status} (4=Playing, 5=Paused, 3=Stopped)")
            except Exception as e:
                print(f"  Error reading session: {e}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(debug_sessions())