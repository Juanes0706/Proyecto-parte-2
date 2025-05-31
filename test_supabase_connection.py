from app.database import get_db

def test_supabase():
    supabase = get_db()
    try:
        data, error = supabase.table("buses").select("*").execute()
        if error:
            print(f"Error querying buses table: {error}")
        else:
            print("Buses table data:")
            print(data)
    except Exception as e:
        print(f"Exception during query: {e}")

if __name__ == "__main__":
    test_supabase()
