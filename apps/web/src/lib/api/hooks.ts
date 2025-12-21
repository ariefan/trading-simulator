'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  api,
  CreateBacktestRequest,
  CreateStrategyRequest,
  GetCandlesParams,
  PlaceOrderRequest,
  UpdateStrategyRequest,
} from './client';

// Query Keys
export const queryKeys = {
  user: ['user'] as const,
  pairs: ['pairs'] as const,
  candles: (params: GetCandlesParams) => ['candles', params] as const,
  strategies: ['strategies'] as const,
  strategy: (id: string) => ['strategies', id] as const,
  backtests: ['backtests'] as const,
  backtest: (id: string) => ['backtests', id] as const,
  backtestStatus: (id: string) => ['backtests', id, 'status'] as const,
  backtestResults: (id: string) => ['backtests', id, 'results'] as const,
  portfolio: ['portfolio'] as const,
  portfolioHistory: (days?: number) => ['portfolio', 'history', days] as const,
  positions: ['positions'] as const,
  orders: ['orders'] as const,
};

// Auth Hooks
export function useUser() {
  return useQuery({
    queryKey: queryKeys.user,
    queryFn: api.auth.me,
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

// Market Data Hooks
export function useCurrencyPairs() {
  return useQuery({
    queryKey: queryKeys.pairs,
    queryFn: api.market.getPairs,
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}

export function useCandles(params: GetCandlesParams, enabled = true) {
  return useQuery({
    queryKey: queryKeys.candles(params),
    queryFn: () => api.market.getCandles(params),
    enabled,
    staleTime: 1000 * 60, // 1 minute
  });
}

// Strategy Hooks
export function useStrategies() {
  return useQuery({
    queryKey: queryKeys.strategies,
    queryFn: api.strategies.list,
  });
}

export function useStrategy(id: string) {
  return useQuery({
    queryKey: queryKeys.strategy(id),
    queryFn: () => api.strategies.get(id),
    enabled: !!id,
  });
}

export function useCreateStrategy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateStrategyRequest) => api.strategies.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.strategies });
    },
  });
}

export function useUpdateStrategy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateStrategyRequest }) =>
      api.strategies.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.strategies });
      queryClient.invalidateQueries({ queryKey: queryKeys.strategy(id) });
    },
  });
}

export function useDeleteStrategy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.strategies.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.strategies });
    },
  });
}

// Backtest Hooks
export function useBacktests() {
  return useQuery({
    queryKey: queryKeys.backtests,
    queryFn: api.backtests.list,
  });
}

export function useBacktest(id: string) {
  return useQuery({
    queryKey: queryKeys.backtest(id),
    queryFn: () => api.backtests.get(id),
    enabled: !!id,
  });
}

export function useBacktestStatus(id: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.backtestStatus(id),
    queryFn: () => api.backtests.getStatus(id),
    enabled: !!id && enabled,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.status === 'running' || data?.status === 'pending') {
        return 1000; // Poll every second while running
      }
      return false;
    },
  });
}

export function useBacktestResults(id: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.backtestResults(id),
    queryFn: () => api.backtests.getResults(id),
    enabled: !!id && enabled,
  });
}

export function useCreateBacktest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateBacktestRequest) => api.backtests.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.backtests });
    },
  });
}

export function useDeleteBacktest() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.backtests.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.backtests });
    },
  });
}

// Portfolio Hooks
export function usePortfolio() {
  return useQuery({
    queryKey: queryKeys.portfolio,
    queryFn: api.portfolio.get,
    refetchInterval: 5000, // Refresh every 5 seconds
  });
}

export function usePortfolioHistory(days?: number) {
  return useQuery({
    queryKey: queryKeys.portfolioHistory(days),
    queryFn: () => api.portfolio.getHistory({ days }),
  });
}

// Trading Hooks
export function usePositions() {
  return useQuery({
    queryKey: queryKeys.positions,
    queryFn: api.trading.getPositions,
    refetchInterval: 1000, // Refresh every second for live updates
  });
}

export function useOrders() {
  return useQuery({
    queryKey: queryKeys.orders,
    queryFn: api.trading.getOrders,
  });
}

export function usePlaceOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PlaceOrderRequest) => api.trading.placeOrder(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.orders });
      queryClient.invalidateQueries({ queryKey: queryKeys.positions });
      queryClient.invalidateQueries({ queryKey: queryKeys.portfolio });
    },
  });
}

export function useCancelOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.trading.cancelOrder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.orders });
    },
  });
}

export function useClosePosition() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.trading.closePosition(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.positions });
      queryClient.invalidateQueries({ queryKey: queryKeys.portfolio });
    },
  });
}
