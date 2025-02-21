import { createClient} from '@supabase/supabase-js'
import { StoredUser } from './types'
import { useUserStore } from './userstore'


export const supabase = createClient(
    'https://dclfiuotoegyysbelntk.supabase.co', 
    import.meta.env.VITE_SUPABASE_API_KEY
)


export async function GetSignedInUser() {
    const { data: { session } } = await supabase.auth.getSession()
    
    console.log(session)
    if (session ) {
        useUserStore((state) => state.userData = {
            user : session.user,
            stored: {
                email : session.user.email, 
                user_id : session.user.id,
                username : session.user.email.split("@")[0]
            }
        })
        console.log("HI")

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

