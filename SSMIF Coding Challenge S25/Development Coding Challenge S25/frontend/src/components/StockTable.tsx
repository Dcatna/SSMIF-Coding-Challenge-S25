import { useEffect, useState } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';

export interface Holding {
    CurrentMarketValue: number;
    CurrentPrice: number;
    CurrentPriceDate: string;
    PurchaseDate: string;
    PurchaseMarketValue: number;
    PurchasePrice: number;
    Symbol: string;
    TotalShares: number;
    TotalChange: number;
    DailyChange: number;
  }

const StockTable = () => {
    const [holdings, setHoldings] = useState<Holding[]>([]);
    //const [currentDate, setCurrentDate] = useState<string>("")

  useEffect(() => {
    fetch("http://127.0.0.1:5000/holdings")
    .then(response => response.json())
    .then(data => setHoldings(data))
    .catch(error => console.error("Error fetching holdings:", error));
  }, []);

  holdings.forEach(holding => (
    holding.TotalChange = holding.CurrentMarketValue - holding.PurchaseMarketValue
  ))
  //console.log(holdings)
  return (
    <div className='border-2 border-black'>
    <h2 className="text-lg font-bold">Stock Holdings</h2>
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Ticker</TableHead>
          <TableHead>Quantity</TableHead>
          <TableHead>Day Change</TableHead>
          <TableHead>Total Change</TableHead>
          <TableHead>Market Value</TableHead>
          <TableHead>Unit Cost</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {holdings.map((holding, index) => (
          <TableRow key={index}>
            <TableCell>{holding.Symbol}</TableCell>
            <TableCell>{holding.TotalShares}</TableCell>
            <TableCell className={holding.DailyChange! < 0 ? "text-red-500" : "text-green-500"}>
              {holding.DailyChange?.toFixed(2)}
            </TableCell>
            <TableCell className={holding.TotalChange! < 0 ? "text-red-500" : "text-green-500"}>
              {holding.TotalChange?.toFixed(2)}
            </TableCell>
            <TableCell>${holding.CurrentMarketValue?.toFixed(2)}</TableCell>
            <TableCell>{holding.CurrentPrice}</TableCell>
  
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </div>
  );
};

export default StockTable;
