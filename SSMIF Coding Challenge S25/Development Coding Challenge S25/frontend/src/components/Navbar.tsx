import { Link } from "react-router-dom"
import { supabase } from '../data/supabaseclient'


const Navbar = () => {
  return (
    <nav className="sticky top-0 z-50 bg-black shadow-sm">
        <div className="w-full flex items-center bg-transparent py-4">
            <div className="flex justify-center space-x-4 flex-grow">
                <Link to="/home">
                    <button className="bg-white py-2 px-3 rounded-md">Home</button>
                </Link>
                <Link to="/grouped">
                    <button className="bg-white py-2 px-3 rounded-md">Groups</button>
                </Link>
            </div>
            <Link to="/signin">
                <button className="bg-white py-2 px-3 rounded-md ml-auto mr-2" onClick={() => supabase.auth.signOut()}>Signout</button>
            </Link>
        </div>
    </nav>
  )
}

export default Navbar