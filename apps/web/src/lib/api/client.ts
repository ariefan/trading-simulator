const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: any
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
  }
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, ...fetchOptions } = options;

  // Build URL with query params
  let url = `${API_BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, String(value));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  // Default headers
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  };

  const response = await fetch(url, {
    ...fetchOptions,
    headers,
    credentials: 'include',
  });

  if (!response.ok) {
    let data;
    try {
      data = await response.json();
    } catch {
      data = null;
    }
    throw new ApiError(response.status, response.statusText, data);
  }

  // Handle empty responses
  const text = await response.text();
  if (!text) return null as T;

  return JSON.parse(text) as T;
}

// API Methods
export const api = {
  // Auth
  auth: {
    verify: () => request<AuthVerifyResponse>('/api/v1/auth/verify'),
    demo: (name?: string) => request<TokenResponse>('/api/v1/auth/demo', {
      method: 'POST',
      body: JSON.stringify({ name: name || 'Demo Trader' }),
    }),
    google: (credential: string) => request<TokenResponse>('/api/v1/auth/google', {
      method: 'POST',
      body: JSON.stringify({ credential }),
    }),
    refresh: (token: string) => request<TokenResponse>('/api/v1/auth/refresh', {
      headers: { Authorization: `Bearer ${token}` },
      method: 'POST',
    }),
    logout: () => request('/api/v1/auth/logout', { method: 'POST' }),
  },

  // Market Data
  market: {
    getPairs: () => request<CurrencyPair[]>('/api/v1/market/pairs'),
    getCandles: (params: GetCandlesParams) =>
      request<Candle[]>('/api/v1/market/candles', { params: params as any }),
  },

  // Strategies
  strategies: {
    list: () => request<Strategy[]>('/api/v1/strategies'),
    get: (id: string) => request<Strategy>(`/api/v1/strategies/${id}`),
    create: (data: CreateStrategyRequest) =>
      request<Strategy>('/api/v1/strategies', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: UpdateStrategyRequest) =>
      request<Strategy>(`/api/v1/strategies/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request(`/api/v1/strategies/${id}`, { method: 'DELETE' }),
  },

  // Backtests
  backtests: {
    list: () => request<Backtest[]>('/api/v1/backtests'),
    get: (id: string) => request<Backtest>(`/api/v1/backtests/${id}`),
    create: (data: CreateBacktestRequest) =>
      request<any>('/api/v1/backtests', {
        method: 'POST',
        body: JSON.stringify({
          strategy_id: data.strategyId,
          symbol: data.symbol,
          timeframe: data.timeframe,
          start_date: data.startDate,
          end_date: data.endDate,
          initial_balance: data.initialBalance,
          leverage: data.leverage,
          parameters: {},
        }),
      }),
    getStatus: (id: string) =>
      request<BacktestStatus>(`/api/v1/backtests/${id}/status`),
    getResults: (id: string) =>
      request<BacktestResults>(`/api/v1/backtests/${id}/results`),
    delete: (id: string) =>
      request(`/api/v1/backtests/${id}`, { method: 'DELETE' }),
  },

  // Portfolio
  portfolio: {
    get: () => request<Portfolio>('/api/v1/portfolio'),
    getHistory: (params?: { days?: number }) =>
      request<PortfolioSnapshot[]>('/api/v1/portfolio/history', { params }),
  },

  // Trading
  trading: {
    getPositions: () => request<Position[]>('/api/v1/trading/positions'),
    getOrders: () => request<Order[]>('/api/v1/trading/orders'),
    placeOrder: (data: PlaceOrderRequest) =>
      request<Order>('/api/v1/trading/orders', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    cancelOrder: (id: string) =>
      request(`/api/v1/trading/orders/${id}`, { method: 'DELETE' }),
    closePosition: (id: string) =>
      request(`/api/v1/trading/positions/${id}/close`, { method: 'POST' }),
    reset: () => request('/api/v1/trading/reset', { method: 'POST' }),
  },

  // Users
  users: {
    getProfile: (token: string) => request<UserProfile>('/api/v1/users/me', {
      headers: { Authorization: `Bearer ${token}` },
    }),
    updateProfile: (token: string, data: UpdateProfileRequest) =>
      request<UserProfile>('/api/v1/users/me', {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      }),
    getSettings: (token: string) => request<UserSettings>('/api/v1/users/me/settings', {
      headers: { Authorization: `Bearer ${token}` },
    }),
    updateSettings: (token: string, data: UserSettings) =>
      request<UserSettings>('/api/v1/users/me/settings', {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      }),
  },
};

// Types
export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface AuthVerifyResponse {
  authenticated: boolean;
  user: User | null;
}

export interface CurrencyPair {
  id: string;
  symbol: string;
  baseCurrency: string;
  quoteCurrency: string;
  pipValue: number;
  minLotSize: number;
  maxLotSize: number;
}

export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface GetCandlesParams {
  symbol: string;
  timeframe: string;
  start?: string;
  end?: string;
  limit?: number;
}

export interface Strategy {
  id: string;
  name: string;
  description?: string;
  code: string;
  parameters: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface CreateStrategyRequest {
  name: string;
  description?: string;
  code: string;
  parameters?: Record<string, any>;
}

export interface UpdateStrategyRequest {
  name?: string;
  description?: string;
  code?: string;
  parameters?: Record<string, any>;
}

export interface Backtest {
  id: string;
  strategyId: string;
  symbol: string;
  timeframe: string;
  startDate: string;
  endDate: string;
  initialBalance: number;
  leverage: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: string;
}

export interface CreateBacktestRequest {
  strategyId: string;
  symbol: string;
  timeframe: string;
  startDate: string;
  endDate: string;
  initialBalance: number;
  leverage: number;
}

// Convert camelCase request to snake_case for backend
function toSnakeCase(obj: Record<string, any>): Record<string, any> {
  const result: Record<string, any> = {};
  for (const key in obj) {
    const snakeKey = key.replace(/([A-Z])/g, '_$1').toLowerCase();
    result[snakeKey] = obj[key];
  }
  return result;
}

export interface BacktestStatus {
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  message?: string;
}

export interface BacktestResults {
  metrics: {
    totalReturnPercent: number;
    sharpeRatio: number;
    maxDrawdown: number;
    winRate: number;
    profitFactor: number;
    totalTrades: number;
    winningTrades: number;
    losingTrades: number;
    averageWin: number;
    averageLoss: number;
    largestWin: number;
    largestLoss: number;
  };
  equityCurve: Array<{ date: string; equity: number }>;
  trades: Array<{
    id: string;
    side: 'long' | 'short';
    size: number;
    entryPrice: number;
    exitPrice: number;
    pnl: number;
    pnlPercent: number;
    entryTime: string;
    exitTime: string;
  }>;
}

export interface Portfolio {
  balance: number;
  equity: number;
  margin: number;
  freeMargin: number;
  marginLevel: number;
  unrealizedPnl: number;
}

export interface PortfolioSnapshot {
  timestamp: string;
  balance: number;
  equity: number;
}

export interface Position {
  id: string;
  symbol: string;
  side: 'long' | 'short';
  size: number;
  entryPrice: number;
  currentPrice: number;
  unrealizedPnl: number;
  stopLoss?: number;
  takeProfit?: number;
  openedAt: string;
}

export interface Order {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop';
  size: number;
  price?: number;
  stopLoss?: number;
  takeProfit?: number;
  status: 'pending' | 'filled' | 'cancelled';
  createdAt: string;
}

export interface PlaceOrderRequest {
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop';
  size: number;
  price?: number;
  stopLoss?: number;
  takeProfit?: number;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  picture?: string;
  initial_balance: number;
  created_at: string;
}

export interface UpdateProfileRequest {
  name?: string;
  picture?: string;
}

export interface UserSettings {
  default_leverage: number;
  default_lot_size: number;
  theme: string;
  notifications_enabled: boolean;
}

export { ApiError };
