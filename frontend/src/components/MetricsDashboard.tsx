import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';
import { Calendar, Clock, CheckCircle, AlertCircle, Users, ArrowUp, ArrowDown } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useMetricsSummary, useQueryVolume, useLatencyMetrics, useSuccessRate, useTopQueries, useTopDocuments } from '@/hooks/useMetrics';
import { useDocumentTypeDistribution } from '@/hooks/useDocuments';

// Badge component for the dashboard
const Badge = ({ className, children }: { className?: string; children: React.ReactNode }) => {
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${className}`}>
      {children}
    </span>
  );
};

const MetricsDashboard: React.FC = () => {
  const [timeframe, setTimeframe] = useState<number>(7);
  
  const { data: metricsSummary, isLoading: isSummaryLoading } = useMetricsSummary(timeframe);
  const { data: queryVolume, isLoading: isVolumeLoading } = useQueryVolume(timeframe);
  const { data: latencyMetrics, isLoading: isLatencyLoading } = useLatencyMetrics(timeframe);
  const { data: successRate, isLoading: isSuccessRateLoading } = useSuccessRate(timeframe);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Activity Chart */}
      <div className="dashboard-card">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-medium">Query Volume</h3>
          <div className="flex items-center gap-2">
            <div className="text-xs text-docflow-secondary flex items-center">
              <Calendar className="h-3.5 w-3.5 mr-1" />
              <span>Period:</span>
            </div>
            <Select value={String(timeframe)} onValueChange={(value) => setTimeframe(Number(value))}>
              <SelectTrigger className="h-8 w-24 text-xs">
                <SelectValue placeholder="Last 7 days" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7">Last 7 days</SelectItem>
                <SelectItem value="14">Last 14 days</SelectItem>
                <SelectItem value="30">Last 30 days</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        
        {isVolumeLoading ? (
          <Skeleton className="h-64 w-full" />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={queryVolume || []}
                margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis 
                  dataKey="date" 
                  tickLine={false}
                  tickFormatter={(date) => new Date(date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ 
                    borderRadius: '8px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    border: 'none'
                  }}
                  formatter={(value) => [`${value} queries`, 'Volume']}
                  labelFormatter={(date) => new Date(date).toLocaleDateString()}
                />
                <Line 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#0ea5e9" 
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Success Rate Chart */}
      <div className="dashboard-card col-span-2 md:col-span-1">
        <h3 className="font-medium mb-2">Success Rate</h3>
        <div className="flex items-center mb-4">
          <div className="p-3 bg-green-50 rounded-full mr-4">
            <CheckCircle className="h-6 w-6 text-docflow-success" />
          </div>
          <div>
            <p className="text-2xl font-bold text-docflow-primary">
              {isSuccessRateLoading ? (
                <Skeleton className="h-8 w-16 inline-block" />
              ) : (
                <>{successRate && successRate.length > 0 
                  ? (successRate[successRate.length - 1].success_rate * 100).toFixed(1)
                  : '0.0'}<span className="text-sm">%</span></>
              )}
            </p>
            <div className="flex items-center text-docflow-success text-xs">
              <ArrowUp className="h-3 w-3 mr-1" />
              <span>Query success rate</span>
            </div>
          </div>
        </div>
        <div className="h-36 mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart 
              data={successRate?.map(item => ({
                day: new Date(item.date).toLocaleDateString('en-US', { weekday: 'short' }).charAt(0),
                date: item.date,
                rate: (item.success_rate * 100).toFixed(1)
              })) || []}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
              <XAxis dataKey="day" axisLine={false} tickLine={false} />
              <YAxis axisLine={false} tickLine={false} domain={[0, 100]} />
              <Tooltip 
                formatter={(value) => [`${value}%`, 'Success rate']}
                labelFormatter={(_, payload) => payload[0]?.payload?.date ? new Date(payload[0].payload.date).toLocaleDateString() : ''}
                contentStyle={{ 
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  border: 'none'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="rate" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Processing Time Card */}
      <div className="dashboard-card">
        <h3 className="font-medium mb-2">Query Performance</h3>
        <div className="flex items-center mb-4">
          <div className="p-3 bg-blue-50 rounded-full mr-4">
            <Clock className="h-6 w-6 text-docflow-accent" />
          </div>
          <div>
            <p className="text-2xl font-bold text-docflow-primary">
              {isLatencyLoading ? (
                <Skeleton className="h-8 w-16 inline-block" />
              ) : (
                <>{latencyMetrics && latencyMetrics.length > 0 
                  ? (latencyMetrics.reduce((sum, item) => sum + item.avg_latency, 0) / latencyMetrics.length).toFixed(2)
                  : '0.00'} <span className="text-sm">seconds</span></>
              )}
            </p>
            <div className="flex items-center text-docflow-success text-xs">
              <ArrowUp className="h-3 w-3 mr-1 transform rotate-180" />
              <span>{latencyMetrics && latencyMetrics.length > 0 
                ? `${((latencyMetrics.reduce((sum, item) => sum + item.avg_latency, 0) / latencyMetrics.length) / 
                    (latencyMetrics.slice(-7).reduce((sum, item) => sum + item.avg_latency, 100) / Math.min(7, latencyMetrics.slice(-7).length)) * 100).toFixed(0)}% lower than last week`
                : '0% lower than last week'}</span>
            </div>
          </div>
        </div>
        <div className="h-36 mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart 
              data={latencyMetrics?.map(item => ({
                day: new Date(item.date).toLocaleDateString('en-US', { weekday: 'short' }).charAt(0),
                date: item.date,
                time: item.avg_latency.toFixed(2)
              })) || []}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
              <XAxis dataKey="day" axisLine={false} tickLine={false} />
              <YAxis axisLine={false} tickLine={false} />
              <Tooltip 
                formatter={(value) => [`${value}`, 'Avg. latency']}
                labelFormatter={(_, payload) => payload[0]?.payload?.date ? new Date(payload[0].payload.date).toLocaleDateString() : ''}
                contentStyle={{ 
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  border: 'none'
                }}
              />
              <Bar dataKey="time" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* System Status */}
      <div className="dashboard-card col-span-2 md:col-span-1">
        <h3 className="font-medium mb-4">System Status</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-md mr-3">
                <CheckCircle className="h-5 w-5 text-docflow-success" />
              </div>
              <span className="font-medium">Document Processing</span>
            </div>
            <Badge className="bg-green-100 text-green-800">Operational</Badge>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-md mr-3">
                <CheckCircle className="h-5 w-5 text-docflow-success" />
              </div>
              <span className="font-medium">Q&A Service</span>
            </div>
            <Badge className="bg-green-100 text-green-800">Operational</Badge>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-md mr-3">
                <Clock className="h-5 w-5 text-docflow-warning" />
              </div>
              <span className="font-medium">Analytics Engine</span>
            </div>
            <Badge className="bg-yellow-100 text-yellow-800">Minor Issues</Badge>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-md mr-3">
                <Users className="h-5 w-5 text-docflow-success" />
              </div>
              <span className="font-medium">User Management</span>
            </div>
            <Badge className="bg-green-100 text-green-800">Operational</Badge>
          </div>
        </div>
      </div>
      
    </div>
  );
};

export default MetricsDashboard;
