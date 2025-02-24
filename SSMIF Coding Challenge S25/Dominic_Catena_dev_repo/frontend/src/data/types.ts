import { User } from "@supabase/supabase-js";



export type StoredUser = {
    email: string;

    user_id: string;
    username: string;
}

export type UserData = {
    user: User;
    stored: StoredUser;
};

export type StockData = {
    Date : string,
    Symbol : string, 
    Shares : string
}