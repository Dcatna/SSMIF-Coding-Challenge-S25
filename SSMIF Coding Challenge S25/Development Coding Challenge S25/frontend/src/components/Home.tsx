import Graph from './Graph'
import PortfolioValueGraph from './PortfolioValueGraph'
import SP500VSPortfolioGraph from './SP500VSPortfolioGraph'
import StockTable from './StockTable'
import TradeTable from './TradeTable'

const Home = () => {
  return (
    <div className="container mx-auto p-4 space-y-8">
      <div className="space-y-8">
        <Graph />
        <PortfolioValueGraph />
        <SP500VSPortfolioGraph />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div className="w-full max-w-7xl max-h-[700px] overflow-x-auto overflow-y-auto border-b border-black pb-4">
        <StockTable />
      </div>

        <div className="w-full max-w-7xl max-h-[700px] overflow-x-auto overflow-y-auto border-b border-black pb-4">
          <TradeTable />
        </div>
      </div>
    </div>
  )
}

export default Home
