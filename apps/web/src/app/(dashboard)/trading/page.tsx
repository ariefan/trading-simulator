'use client';

import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { CandlestickChart } from '@/components/charts/candlestick-chart';
import { formatCurrency } from '@/lib/utils';
import { Wifi, WifiOff } from 'lucide-react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_BASE_URL = API_BASE_URL.replace('http', 'ws');

const CURRENCY_PAIRS = [
  { symbol: 'EURUSD', name: 'EUR/USD', basePrice: 1.0850 },
  { symbol: 'GBPUSD', name: 'GBP/USD', basePrice: 1.2650 },
  { symbol: 'USDJPY', name: 'USD/JPY', basePrice: 149.50 },
  { symbol: 'USDCHF', name: 'USD/CHF', basePrice: 0.8750 },
  { symbol: 'AUDUSD', name: 'AUD/USD', basePrice: 0.6550 },
  { symbol: 'USDCAD', name: 'USD/CAD', basePrice: 1.3600 },
  { symbol: 'NZDUSD', name: 'NZD/USD', basePrice: 0.6100 },
  { symbol: 'XAUUSD', name: 'XAU/USD (Gold)', basePrice: 2050.50 },
];

interface Position {
  id: string;
  symbol: string;
  side: 'long' | 'short';
  size: number;
  entry_price: number;
  current_price: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
  stop_loss?: number;
  take_profit?: number;
  margin_used: number;
  opened_at: string;
}

interface PriceData {
  bid: number;
  ask: number;
  mid: number;
  spread: number;
  change: number;
  changePercent: number;
  timestamp: string;
}

interface PairPrice {
  symbol: string;
  data: PriceData;
}

function generateMockCandles(symbol: string): Array<{
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}> {
  const candles = [];
  const pair = CURRENCY_PAIRS.find((p) => p.symbol === symbol);
  const basePrice = pair?.basePrice || 1.0;
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
  const [positions, setPositions] = useState<Position[]>([]);
  const [prices, setPrices] = useState<Map<string, PriceData>>(new Map());
  const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
  const [orderSide, setOrderSide] = useState<'buy' | 'sell'>('buy');
  const [orderSize, setOrderSize] = useState('0.1');
  const [limitPrice, setLimitPrice] = useState('');
  const [stopLoss, setStopLoss] = useState('');
  const [takeProfit, setTakeProfit] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wsConnected, setWsConnected] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const chartData = useMemo(
    () => generateMockCandles(selectedPair.symbol),
    [selectedPair.symbol]
  );

  const [currentTime, setCurrentTime] = useState(new Date());

  // WebSocket connection
  useEffect(() => {
    let mounted = true;

    const connect = () => {
      if (!mounted) return;

      const ws = new WebSocket(`${WS_BASE_URL}/api/v1/ws/prices`);
      wsRef.current = ws;

      ws.onopen = () => {
        if (!mounted) return;
        setWsConnected(true);
        // Subscribe to all currency pairs
        ws.send(JSON.stringify({
          action: 'subscribe',
          symbols: CURRENCY_PAIRS.map(p => p.symbol),
        }));
      };

      ws.onmessage = (event) => {
        if (!mounted) return;
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'price' && message.symbol && message.data) {
            setPrices(prev => {
              const newPrices = new Map(prev);
              newPrices.set(message.symbol, message.data);
              return newPrices;
            });
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = () => {
        if (!mounted) return;
        setWsConnected(false);
        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        if (!mounted) return;
        setWsConnected(false);
      };
    };

    connect();

    return () => {
      mounted = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Fetch positions
  const fetchPositions = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/trading/positions`);
      if (response.ok) {
        const data = await response.json();
        setPositions(data);
      }
    } catch (err) {
      console.error('Failed to fetch positions:', err);
    }
  }, []);

  useEffect(() => {
    fetchPositions();

    const positionInterval = setInterval(fetchPositions, 5000);
    const timeInterval = setInterval(() => setCurrentTime(new Date()), 1000);

    return () => {
      clearInterval(positionInterval);
      clearInterval(timeInterval);
    };
  }, [fetchPositions]);

  const totalPnl = positions.reduce((sum, p) => sum + p.unrealized_pnl, 0);

  const handlePlaceOrder = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/trading/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: selectedPair.symbol,
          side: orderSide,
          type: orderType,
          size: parseFloat(orderSize),
          price: limitPrice ? parseFloat(limitPrice) : undefined,
          stop_loss: stopLoss ? parseFloat(stopLoss) : undefined,
          take_profit: takeProfit ? parseFloat(takeProfit) : undefined,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to place order');
      }

      // Refresh positions
      await fetchPositions();

      // Reset form
      setOrderSize('0.1');
      setLimitPrice('');
      setStopLoss('');
      setTakeProfit('');
    } catch (err: any) {
      setError(err.message || 'Failed to place order');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClosePosition = async (positionId: string) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/v1/trading/positions/${positionId}/close`,
        { method: 'POST' }
      );

      if (response.ok) {
        await fetchPositions();
      }
    } catch (err) {
      console.error('Failed to close position:', err);
    }
  };

  const getCurrentPrice = (symbol: string) => {
    const priceData = prices.get(symbol);
    return priceData?.mid || CURRENCY_PAIRS.find((p) => p.symbol === symbol)?.basePrice || 0;
  };

  const getBidPrice = (symbol: string) => {
    const priceData = prices.get(symbol);
    return priceData?.bid || getCurrentPrice(symbol);
  };

  const getAskPrice = (symbol: string) => {
    const priceData = prices.get(symbol);
    return priceData?.ask || getCurrentPrice(symbol);
  };

  const getPriceChange = (symbol: string) => {
    const priceData = prices.get(symbol);
    return priceData?.change || 0;
  };

  const getSpread = (symbol: string) => {
    const priceData = prices.get(symbol);
    return priceData?.spread || 0;
  };

  const formatPrice = (symbol: string, price: number) => {
    const isJpy = symbol.includes('JPY');
    const isGold = symbol.includes('XAU');
    const decimals = (isJpy || isGold) ? 3 : 5;
    return price.toFixed(decimals);
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
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            {wsConnected ? (
              <Wifi className="w-4 h-4 text-green-500" />
            ) : (
              <WifiOff className="w-4 h-4 text-red-500" />
            )}
            <span className={`text-sm ${wsConnected ? 'text-green-500' : 'text-red-500'}`}>
              {wsConnected ? 'Live' : 'Offline'}
            </span>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Market Time (UTC)</p>
            <p className="text-lg font-mono">{currentTime.toUTCString().slice(17, 25)}</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md text-red-700 dark:text-red-300 text-sm">
          {error}
          <button className="ml-2 underline" onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-4">
        {/* Watchlist */}
        <Card className="lg:col-span-1">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Watchlist</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 p-2">
            {CURRENCY_PAIRS.map((pair) => {
              const bid = getBidPrice(pair.symbol);
              const ask = getAskPrice(pair.symbol);
              const change = getPriceChange(pair.symbol);
              const spread = getSpread(pair.symbol);
              return (
                <button
                  key={pair.symbol}
                  onClick={() => setSelectedPair(pair)}
                  className={`w-full flex items-center justify-between p-2 rounded-md transition-colors ${selectedPair.symbol === pair.symbol
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted'
                    }`}
                >
                  <div>
                    <span className="font-medium">{pair.name}</span>
                    <p className={`text-xs ${selectedPair.symbol === pair.symbol ? 'opacity-70' : 'text-muted-foreground'}`}>
                      Spread: {spread.toFixed(1)} pips
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="flex gap-2 text-xs font-mono">
                      <span className="text-red-500">{formatPrice(pair.symbol, bid)}</span>
                      <span className="text-green-500">{formatPrice(pair.symbol, ask)}</span>
                    </div>
                    <p
                      className={`text-xs ${change >= 0
                        ? selectedPair.symbol === pair.symbol ? 'text-green-200' : 'text-green-500'
                        : selectedPair.symbol === pair.symbol ? 'text-red-200' : 'text-red-500'
                        }`}
                    >
                      {change >= 0 ? '+' : ''}
                      {formatPrice(pair.symbol, change)}
                    </p>
                  </div>
                </button>
              );
            })}
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
            {/* Live Price Display */}
            <div className="grid grid-cols-2 gap-2 p-3 bg-muted rounded-md">
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Sell (Bid)</p>
                <p className="text-lg font-mono text-red-500">
                  {formatPrice(selectedPair.symbol, getBidPrice(selectedPair.symbol))}
                </p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground">Buy (Ask)</p>
                <p className="text-lg font-mono text-green-500">
                  {formatPrice(selectedPair.symbol, getAskPrice(selectedPair.symbol))}
                </p>
              </div>
            </div>

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
                  step={selectedPair.symbol.includes('JPY') || selectedPair.symbol.includes('XAU') ? "0.01" : "0.0001"}
                  placeholder={formatPrice(selectedPair.symbol, getCurrentPrice(selectedPair.symbol))}
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
                step={selectedPair.symbol.includes('JPY') || selectedPair.symbol.includes('XAU') ? "0.01" : "0.0001"}
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
                step={selectedPair.symbol.includes('JPY') || selectedPair.symbol.includes('XAU') ? "0.01" : "0.0001"}
                placeholder="0.0000"
                value={takeProfit}
                onChange={(e) => setTakeProfit(e.target.value)}
              />
            </div>

            <Button
              className={`w-full ${orderSide === 'buy'
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-red-600 hover:bg-red-700'
                }`}
              onClick={handlePlaceOrder}
              disabled={isLoading}
            >
              {isLoading
                ? 'Placing Order...'
                : `${orderSide === 'buy' ? 'Buy' : 'Sell'} ${selectedPair.name}`}
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
                className={`text-xl font-bold ${totalPnl >= 0 ? 'text-green-600' : 'text-red-600'
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
                          className={`px-2 py-0.5 text-xs rounded ${position.side === 'long'
                            ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                            : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                            }`}
                        >
                          {position.side.toUpperCase()}
                        </span>
                      </td>
                      <td className="py-3">{position.size} lots</td>
                      <td className="py-3 font-mono">{formatPrice(position.symbol, position.entry_price)}</td>
                      <td className="py-3 font-mono">{formatPrice(position.symbol, position.current_price)}</td>
                      <td
                        className={`py-3 text-right font-medium ${position.unrealized_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}
                      >
                        {position.unrealized_pnl >= 0 ? '+' : ''}
                        {formatCurrency(position.unrealized_pnl)}
                        <span className="text-xs ml-1">
                          ({position.unrealized_pnl_percent >= 0 ? '+' : ''}
                          {position.unrealized_pnl_percent.toFixed(2)}%)
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleClosePosition(position.id)}
                        >
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
