
import Graph from './Graph'
import PortfolioValueGraph from './PortfolioValueGraph'
import StockTable from './StockTable'
import TradeTable from './TradeTable'

const Home = () => {
  return (
    <div>
        <Graph/>
        <PortfolioValueGraph/>
        <div className='flex'>
          <div className='w-[1500px] h-[700px] overflow-x-auto ml-2'>
            <StockTable/>
          </div>
          <div className='ml-8 w-[550px] h-[700px] overflow-x-auto'>
            <TradeTable/>
          </div>
        </div>
    </div>
  )
}

export default Home