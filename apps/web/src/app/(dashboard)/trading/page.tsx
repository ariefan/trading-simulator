'use client';

import { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { CandlestickChart } from '@/components/charts/candlestick-chart';
import { formatCurrency } from '@/lib/utils';

const CURRENCY_PAIRS = [
  { symbol: 'EURUSD', name: 'EUR/USD', price: 1.0876, change: 0.0012 },
  { symbol: 'GBPUSD', name: 'GBP/USD', price: 1.2654, change: -0.0008 },
  { symbol: 'USDJPY', name: 'USD/JPY', price: 149.32, change: 0.45 },
  { symbol: 'USDCHF', name: 'USD/CHF', price: 0.8823, change: -0.0015 },
  { symbol: 'AUDUSD', name: 'AUD/USD', price: 0.6578, change: 0.0023 },
];

interface Position {
  id: string;
  symbol: string;
  side: 'long' | 'short';
  size: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
}

const MOCK_POSITIONS: Position[] = [
  {
    id: '1',
    symbol: 'EURUSD',
    side: 'long',
    size: 0.5,
    entryPrice: 1.0850,
    currentPrice: 1.0876,
    pnl: 130,
    pnlPercent: 1.3,
  },
  {
    id: '2',
    symbol: 'GBPUSD',
    side: 'short',
    size: 0.3,
    entryPrice: 1.2680,
    currentPrice: 1.2654,
    pnl: 78,
    pnlPercent: 0.78,
  },
];

function generateMockCandles(symbol: string): Array<{
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}> {
  const candles = [];
  const basePrice = symbol === 'EURUSD' ? 1.08 : symbol === 'GBPUSD' ? 1.26 : 149;
  let price = basePrice;
  const now = new Date();

  for (let i = 100; i >= 0; i--) {
    const date = new Date(now);
    date.setHours(date.getHours() - i);

    const change = (Math.random() - 0.5) * 0.002 * basePrice;
    const open = price;
    const close = price + change;
    const high = Math.max(open, close) + Math.random() * 0.001 * basePrice;
    const low = Math.min(open, close) - Math.random() * 0.001 * basePrice;

    candles.push({
      time: date.toISOString().slice(0, 16).replace('T', ' '),
      open,
      high,
      low,
      close,
      volume: Math.floor(Math.random() * 10000) + 1000,
    });

    price = close;
  }

  return candles;
}

export default function TradingPage() {
  const [selectedPair, setSelectedPair] = useState(CURRENCY_PAIRS[0]);
  const [positions] = useState<Position[]>(MOCK_POSITIONS);
  const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [orderSize, setOrderSize] = useState('0.1');
  const [limitPrice, setLimitPrice] = useState('');
  const [stopLoss, setStopLoss] = useState('');
  const [takeProfit, setTakeProfit] = useState('');

  const chartData = useMemo(
    () => generateMockCandles(selectedPair.symbol),
    [selectedPair.symbol]
  );

  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(interval);
  }, []);

  const totalPnl = positions.reduce((sum, p) => sum + p.pnl, 0);

  const handlePlaceOrder = () => {
    console.log('Placing order:', {
      symbol: selectedPair.symbol,
      type: orderType,
      side: orderSide,
      size: parseFloat(orderSize),
      limitPrice: limitPrice ? parseFloat(limitPrice) : undefined,
      stopLoss: stopLoss ? parseFloat(stopLoss) : undefined,
      takeProfit: takeProfit ? parseFloat(takeProfit) : undefined,
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Paper Trading</h1>
          <p className="text-muted-foreground">
            Practice trading with virtual money
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-muted-foreground">Market Time (UTC)</p>
          <p className="text-lg font-mono">{currentTime.toUTCString().slice(17, 25)}</p>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        {/* Watchlist */}
        <Card className="lg:col-span-1">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Watchlist</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 p-2">
            {CURRENCY_PAIRS.map((pair) => (
              <button
                key={pair.symbol}
                onClick={() => setSelectedPair(pair)}
                className={`w-full flex items-center justify-between p-2 rounded-md transition-colors ${
                  selectedPair.symbol === pair.symbol
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted'
                }`}
              >
                <span className="font-medium">{pair.name}</span>
                <div className="text-right">
                  <p className="font-mono text-sm">{pair.price.toFixed(4)}</p>
                  <p
                    className={`text-xs ${
                      pair.change >= 0 ? 'text-green-500' : 'text-red-500'
                    }`}
                  >
                    {pair.change >= 0 ? '+' : ''}
                    {pair.change.toFixed(4)}
                  </p>
                </div>
              </button>
            ))}
          </CardContent>
        </Card>

        {/* Chart */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{selectedPair.name}</CardTitle>
                <CardDescription>1 Hour timeframe</CardDescription>
              </div>
              <div className="flex gap-1">
                {['1M', '5M', '15M', '1H', '4H', '1D'].map((tf) => (
                  <Button
                    key={tf}
                    variant={tf === '1H' ? 'secondary' : 'ghost'}
                    size="sm"
                    className="h-7 px-2 text-xs"
                  >
                    {tf}
                  </Button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-2">
            <CandlestickChart data={chartData} height={350} showVolume />
          </CardContent>
        </Card>

        {/* Order Panel */}
        <Card className="lg:col-span-1">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Place Order</CardTitle>
            <CardDescription>{selectedPair.name}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Order Type */}
            <div className="grid grid-cols-2 gap-1 p-1 bg-muted rounded-md">
              <Button
                variant={orderType === 'market' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setOrderType('market')}
              >
                Market
              </Button>
              <Button
                variant={orderType === 'limit' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setOrderType('limit')}
              >
                Limit
              </Button>
            </div>

            {/* Buy/Sell */}
            <div className="grid grid-cols-2 gap-2">
              <Button
                variant={orderSide === 'buy' ? 'default' : 'outline'}
                className={orderSide === 'buy' ? 'bg-green-600 hover:bg-green-700' : ''}
                onClick={() => setOrderSide('buy')}
              >
                Buy
              </Button>
              <Button
                variant={orderSide === 'sell' ? 'default' : 'outline'}
                className={orderSide === 'sell' ? 'bg-red-600 hover:bg-red-700' : ''}
                onClick={() => setOrderSide('sell')}
              >
                Sell
              </Button>
            </div>

            {/* Size */}
            <div className="space-y-2">
              <Label htmlFor="size">Size (Lots)</Label>
              <Input
                id="size"
                type="number"
                step="0.01"
                value={orderSize}
                onChange={(e) => setOrderSize(e.target.value)}
              />
            </div>

            {/* Limit Price */}
            {orderType === 'limit' && (
              <div className="space-y-2">
                <Label htmlFor="limitPrice">Limit Price</Label>
                <Input
                  id="limitPrice"
                  type="number"
                  step="0.0001"
                  placeholder={selectedPair.price.toFixed(4)}
                  value={limitPrice}
                  onChange={(e) => setLimitPrice(e.target.value)}
                />
              </div>
            )}

            <Separator />

            {/* Stop Loss */}
            <div className="space-y-2">
              <Label htmlFor="stopLoss">Stop Loss (Optional)</Label>
              <Input
                id="stopLoss"
                type="number"
                step="0.0001"
                placeholder="0.0000"
                value={stopLoss}
                onChange={(e) => setStopLoss(e.target.value)}
              />
            </div>

            {/* Take Profit */}
            <div className="space-y-2">
              <Label htmlFor="takeProfit">Take Profit (Optional)</Label>
              <Input
                id="takeProfit"
                type="number"
                step="0.0001"
                placeholder="0.0000"
                value={takeProfit}
                onChange={(e) => setTakeProfit(e.target.value)}
              />
            </div>

            <Button
              className={`w-full ${
                orderSide === 'buy'
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-red-600 hover:bg-red-700'
              }`}
              onClick={handlePlaceOrder}
            >
              {orderSide === 'buy' ? 'Buy' : 'Sell'} {selectedPair.name}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Open Positions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Open Positions</CardTitle>
              <CardDescription>{positions.length} active position(s)</CardDescription>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Total P&L</p>
              <p
                className={`text-xl font-bold ${
                  totalPnl >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {totalPnl >= 0 ? '+' : ''}
                {formatCurrency(totalPnl)}
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {positions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b text-left text-sm text-muted-foreground">
                    <th className="pb-2">Symbol</th>
                    <th className="pb-2">Side</th>
                    <th className="pb-2">Size</th>
                    <th className="pb-2">Entry</th>
                    <th className="pb-2">Current</th>
                    <th className="pb-2 text-right">P&L</th>
                    <th className="pb-2 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map((position) => (
                    <tr key={position.id} className="border-b last:border-0">
                      <td className="py-3 font-medium">{position.symbol}</td>
                      <td className="py-3">
                        <span
                          className={`px-2 py-0.5 text-xs rounded ${
                            position.side === 'long'
                              ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                              : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                          }`}
                        >
                          {position.side.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3">{position.size} lots</td>
                      <td className="py-3 font-mono">{position.entryPrice.toFixed(4)}</td>
                      <td className="py-3 font-mono">{position.currentPrice.toFixed(4)}</td>
                      <td
                        className={`py-3 text-right font-medium ${
                          position.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {position.pnl >= 0 ? '+' : ''}
                        {formatCurrency(position.pnl)}
                        <span className="text-xs ml-1">
                          ({position.pnlPercent >= 0 ? '+' : ''}
                          {position.pnlPercent.toFixed(2)}%)
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <Button variant="outline" size="sm">
                          Close
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No open positions. Place an order to start trading.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
