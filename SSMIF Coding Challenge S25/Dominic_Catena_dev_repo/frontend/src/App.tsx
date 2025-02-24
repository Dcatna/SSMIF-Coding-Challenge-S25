
import { Outlet } from 'react-router-dom'
import Navbar from './components/Navbar'

function App() {

  return (
    <>
      <Navbar/>

      <div className='overflow-x-auto'>
        <Outlet/>
      </div>
    </>
  )
}

export default App
