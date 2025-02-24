import { Link } from "react-router-dom"

import stevensLogo from "../icons/StevensLogo.jpg"
import { useUserStore } from "@/data/userstore"

const Navbar = () => {
    const signoutFunction = useUserStore((state) => state.signOut)
  return (
        <nav className="sticky top-0 z-50 shadow-sm ">
            <div className="w-full flex items-center bg-transparent py-4 px-4">
                <img src={stevensLogo} alt="" className="h-[75px]" />
                <div className="flex-grow"></div> {/* Spacer to push button right */}
                <Link to="/signin">
                    <button className="bg-red-500 hover:bg-red-600 py-4 px-3 rounded-md" onClick={() => signoutFunction()}>
                        Signout
                    </button>
                </Link>
            </div>
        </nav>

  )
}

export default Navbar