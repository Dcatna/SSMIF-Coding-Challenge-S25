import { createClient} from '@supabase/supabase-js'
import { StoredUser } from './types'


export const supabase = createClient(
    'https://dclfiuotoegyysbelntk.supabase.co', 
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjbGZpdW90b2VneXlzYmVsbnRrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk5MTI4MzYsImV4cCI6MjA1NTQ4ODgzNn0.P2ta7cgjT2J71LJ_uSIKmGV4AiQQINv8aE0K5KYVm6c"
)


export async function GetSignedInUser() {
    const { data: { session } } = await supabase.auth.getSession()
    
    console.log(session)
    if (session ) {

        return true
    }
    return false
}

export async function getUserById(id: string): Promise<StoredUser | null> {

    const { data, error } = await supabase.from("users").select("*").eq("user_id", id)
  
    if (error) {
        console.error("Error fetching user by ID:", error.message);
        return null;
    }
    if(data.length <= 0 || !data) {
        console.error("No user found");
        return null
    }
    console.log("Fetched user from Users table:", data[0])

    return {
        user_id: data[0].user_id,
        email: data[0].email,
        username: data[0].username,
    } satisfies StoredUser

}

