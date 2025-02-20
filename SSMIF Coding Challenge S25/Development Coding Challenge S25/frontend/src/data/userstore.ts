import {create } from "zustand"
import { UserData } from "./types";
import { getUserById, supabase } from "./supabaseclient";
import { failureResult, Result, successResult } from "../lib/utils";



export interface UserStore {
    userData: UserData | undefined;
    signIn: (email: string, password: string) => Promise<boolean >;
    refreshUser: () => Promise<void>;
    signOut: () => Promise<void>;
    init: () => () => void;

}


function getInitialUserData() {
    try {
      // Fetch the stored data from localStorage
      const userString = localStorage.getItem("user");
      const storedString = localStorage.getItem("stored");
  
      // Parse the JSON strings into objects
      const user = userString ? JSON.parse(userString) : null;
      const stored = storedString ? JSON.parse(storedString) : null;  
      // Validate the data and return UserData if valid
      if (user && stored && user.user.id === stored.user_id) {
        return {
          user: user.user, // Access the nested user object
          stored: stored,
        };
      }
    } catch (error) {
      console.error("Error parsing localStorage data:", error);
    }
    return undefined;
  }



export const useUserStore = create<UserStore>((set, get) => ({
    userData: getInitialUserData(),
    init: () => {


      const { data } = supabase.auth.onAuthStateChange((event, session) => {
        console.log(event, session)

         if (event === "SIGNED_IN") {
          get()
            .refreshUser()
            
        } else if (event === "SIGNED_OUT") {
          localStorage.removeItem("user")
          localStorage.removeItem("stored")
          set({
            userData: undefined,
 
          });
        } else if (event === "PASSWORD_RECOVERY") {
          // handle password recovery event
        } else if (event === "TOKEN_REFRESHED") {
          // handle token refreshed event
        } else if (event === "USER_UPDATED") {
          // handle user updated event
          get().refreshUser();
        }
      })
      initializeUser().then((result) => {
        if (!result.ok) {
          localStorage.removeItem("user")
          localStorage.removeItem("stored")
          return
        }
        localStorage.setItem("user", JSON.stringify(result.data.user))
        localStorage.setItem("stored", JSON.stringify(result.data.stored))
        set({
          userData: result.data,
        });
  
        
      });
      return data.subscription.unsubscribe
    },
    signIn: async (email: string, password: string) => {
      const result = await supabase.auth.signInWithPassword({email, password});
      
      if(!result.error) {
        const stored = await getUserById(result.data.user.id)
        if (!stored) {
          console.warn("User ID not found in database");
          return false;
        }
        set({
          userData: {
            user: result.data.user,
            stored: stored,
          }
        })
       
        return true
      }
      return false
    },
  
    refreshUser: async () => {
      const { data, error } = await supabase.auth.getUser();
      if (error) {
        console.error("Error fetching user:", error.message);
        return;
      }
      const id = data.user?.id;
      if (!id) {
        console.warn("No user ID found");
        return;
      }
      const stored = await getUserById(id);
      if (!stored) {
        console.warn("User ID not found in database");
        return;
      }
      localStorage.setItem("user", JSON.stringify({ user: data.user }));
      localStorage.setItem("stored", JSON.stringify(stored));
      set({
        userData: {
          user: data.user,
          stored: stored,
        },
      });
    },
  
    signOut: async () => {
      const { error } = await supabase.auth.signOut();
      if (error) {
        console.error("Sign-out error:", error.message);
        return;
      }
      set({
        userData: undefined,
      });
    },
    
  }))

  async function initializeUser(): Promise<Result<UserData, unknown>> {
    const user = await supabase.auth.getUser();
    if (user.error) {
      return failureResult(user.error);
    }

    return successResult({
      user: user.data.user,
      stored: {
        email: user.data.user.email || "", 
        profile_image: "",
        user_id: user.data.user.id, 
        username: user.data.user.email?.split("@")[0] || "unknown",
      },
    });
  }