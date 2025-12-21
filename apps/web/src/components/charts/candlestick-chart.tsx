'use client';

import { useEffect, useRef, useState } from 'react';
import {
  createChart,
  ColorType,
  IChartApi,
  ISeriesApi,
  CandlestickData,
  Time,
  CrosshairMode,
} from 'lightweight-charts';

interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

interface CandlestickChartProps {
  data: CandleData[];
  trades?: Array<{
    time: string;
    side: 'long' | 'short';
    price: number;
    type: 'entry' | 'exit';
  }>;
  height?: number;
  showVolume?: boolean;
  theme?: 'light' | 'dark';
  onCrosshairMove?: (price: number | null, time: string | null) => void;
}

export function CandlestickChart({
  data,
  trades = [],
  height = 400,
  showVolume = true,
  theme = 'dark',
  onCrosshairMove,
}: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const [currentPrice, setCurrentPrice] = useState<number | null>(null);

  const colors = {
    dark: {
      backgroundColor: 'transparent',
      textColor: '#d1d5db',
      gridColor: '#374151',
      upColor: '#22c55e',
      downColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
      volumeUpColor: 'rgba(34, 197, 94, 0.3)',
      volumeDownColor: 'rgba(239, 68, 68, 0.3)',
    },
    light: {
      backgroundColor: 'transparent',
      textColor: '#374151',
      gridColor: '#e5e7eb',
      upColor: '#16a34a',
      downColor: '#dc2626',
      wickUpColor: '#16a34a',
      wickDownColor: '#dc2626',
      volumeUpColor: 'rgba(22, 163, 74, 0.3)',
      volumeDownColor: 'rgba(220, 38, 38, 0.3)',
    },
  };

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const currentColors = colors[theme];

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: currentColors.backgroundColor },
        textColor: currentColors.textColor,
      },
      grid: {
        vertLines: { color: currentColors.gridColor },
        horzLines: { color: currentColors.gridColor },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          width: 1,
          color: 'rgba(156, 163, 175, 0.5)',
          style: 2,
        },
        horzLine: {
          width: 1,
          color: 'rgba(156, 163, 175, 0.5)',
          style: 2,
        },
      },
      rightPriceScale: {
        borderColor: currentColors.gridColor,
      },
      timeScale: {
        borderColor: currentColors.gridColor,
        timeVisible: true,
        secondsVisible: false,
      },
      width: chartContainerRef.current.clientWidth,
      height: height,
    });

    chartRef.current = chart;

    // Create candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: currentColors.upColor,
      downColor: currentColors.downColor,
      wickUpColor: currentColors.wickUpColor,
      wickDownColor: currentColors.wickDownColor,
      borderVisible: false,
    });

    candlestickSeriesRef.current = candlestickSeries;

    // Create volume series if enabled
    if (showVolume) {
      const volumeSeries = chart.addHistogramSeries({
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
      });

      volumeSeries.priceScale().applyOptions({
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });

      volumeSeriesRef.current = volumeSeries;
    }

    // Handle crosshair move
    chart.subscribeCrosshairMove((param) => {
      if (param.time && param.seriesData.size > 0) {
        const data = param.seriesData.get(candlestickSeries);
        if (data && 'close' in data) {
          setCurrentPrice(data.close as number);
          onCrosshairMove?.(data.close as number, param.time as string);
        }
      } else {
        setCurrentPrice(null);
        onCrosshairMove?.(null, null);
      }
    });

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [height, theme, showVolume, onCrosshairMove]);

  // Update data when it changes
  useEffect(() => {
    if (!candlestickSeriesRef.current || !data.length) return;

    const formattedData: CandlestickData[] = data.map((d) => ({
      time: d.time as Time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    candlestickSeriesRef.current.setData(formattedData);

    // Update volume data if available
    if (volumeSeriesRef.current && showVolume) {
      const volumeData = data.map((d) => ({
        time: d.time as Time,
        value: d.volume || 0,
        color: d.close >= d.open
          ? colors[theme].volumeUpColor
          : colors[theme].volumeDownColor,
      }));

      volumeSeriesRef.current.setData(volumeData);
    }

    // Fit content to view
    chartRef.current?.timeScale().fitContent();
  }, [data, showVolume, theme]);

  // Add trade markers
  useEffect(() => {
    if (!candlestickSeriesRef.current || !trades.length) return;

    const markers = trades.map((trade) => ({
      time: trade.time as Time,
      position: trade.side === 'long' ? 'belowBar' : 'aboveBar',
      color: trade.type === 'entry'
        ? (trade.side === 'long' ? '#22c55e' : '#ef4444')
        : '#6b7280',
      shape: trade.type === 'entry'
        ? (trade.side === 'long' ? 'arrowUp' : 'arrowDown')
        : 'circle',
      text: trade.type === 'entry'
        ? (trade.side === 'long' ? 'BUY' : 'SELL')
        : 'EXIT',
      size: 1,
    }));

    candlestickSeriesRef.current.setMarkers(markers as any);
  }, [trades]);

  return (
    <div className="relative w-full">
      {currentPrice && (
        <div className="absolute top-2 left-2 z-10 px-2 py-1 bg-background/80 rounded text-sm font-mono">
          {currentPrice.toFixed(5)}
        </div>
      )}
      <div ref={chartContainerRef} className="w-full" />
    </div>
  );
}

// Mini chart for dashboard widgets
interface MiniChartProps {
  data: CandleData[];
  height?: number;
  isPositive?: boolean;
}

export function MiniChart({ data, height = 60, isPositive = true }: MiniChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !data.length) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: 'transparent',
      },
      grid: {
        vertLines: { visible: false },
        horzLines: { visible: false },
      },
      rightPriceScale: { visible: false },
      timeScale: { visible: false },
      handleScale: false,
      handleScroll: false,
      crosshair: {
        vertLine: { visible: false },
        horzLine: { visible: false },
      },
      width: chartContainerRef.current.clientWidth,
      height: height,
    });

    const lineSeries = chart.addAreaSeries({
      topColor: isPositive ? 'rgba(34, 197, 94, 0.4)' : 'rgba(239, 68, 68, 0.4)',
      bottomColor: isPositive ? 'rgba(34, 197, 94, 0)' : 'rgba(239, 68, 68, 0)',
      lineColor: isPositive ? '#22c55e' : '#ef4444',
      lineWidth: 2,
    });

    const lineData = data.map((d) => ({
      time: d.time as Time,
      value: d.close,
    }));

    lineSeries.setData(lineData);
    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, height, isPositive]);

  return <div ref={chartContainerRef} className="w-full" />;
}
