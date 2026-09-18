import { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Users, Database, Cpu, HardDrive } from 'lucide-react';

const generateMockData = () => {
  const data = [];
  let searches = 100;
  let indexing = 10;
  let memory = 40;
  for (let i = 20; i >= 0; i--) {
    data.push({
      time: new Date(Date.now() - i * 5000).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' }),
      searches: searches,
      indexing: indexing,
      memory: memory,
    });
    searches += Math.floor(Math.random() * 20) - 10;
    indexing += Math.floor(Math.random() * 5) - 2;
    memory += Math.floor(Math.random() * 4) - 2;
    if(searches < 10) searches = 10;
    if(indexing < 0) indexing = 0;
    if(memory > 100) memory = 100;
  }
  return data;
};

export default function App() {
  const [data, setData] = useState(generateMockData());

  useEffect(() => {
    const interval = setInterval(() => {
      setData((prevData) => {
        const newData = [...prevData.slice(1)];
        const last = newData[newData.length - 1];
        
        let newSearches = last.searches + Math.floor(Math.random() * 20) - 10;
        let newIndexing = last.indexing + Math.floor(Math.random() * 5) - 2;
        let newMemory = last.memory + Math.floor(Math.random() * 4) - 2;
        
        if(newSearches < 10) newSearches = 10;
        if(newIndexing < 0) newIndexing = 0;
        if(newMemory > 100) newMemory = 100;
        if(newMemory < 10) newMemory = 10;

        newData.push({
          time: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' }),
          searches: newSearches,
          indexing: newIndexing,
          memory: newMemory,
        });
        return newData;
      });
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const currentStats = data[data.length - 1];

  return (
    <div className="min-h-screen bg-[#0d1117] text-white font-sans selection:bg-blue-500/30">
      <div className="max-w-7xl mx-auto px-6 py-10 lg:py-16">
        
        {/* Header */}
        <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-gray-800 pb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-2 text-gray-100 flex items-center gap-3">
              <Activity className="text-blue-500" />
              Bot Monitoring Dashboard
            </h1>
            <p className="text-gray-400">Real-time statistics for Telegram Movie & TV Series Auto-Filter Bot</p>
          </div>
          <div className="text-sm font-medium text-gray-500 bg-[#161b22] px-4 py-2 rounded-full border border-gray-800">
            Developer: <a href="https://t.me/Spidey2189" target="_blank" rel="noreferrer" className="text-blue-400 hover:text-blue-300">@Spidey2189</a>
          </div>
        </header>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <MetricCard icon={<Users className="text-emerald-400" />} title="Active Users" value="12,458" trend="+12%" />
          <MetricCard icon={<Database className="text-blue-400" />} title="Files Indexed" value="84,092" trend="+340/hr" />
          <MetricCard icon={<Activity className="text-pink-400" />} title="Searches/min" value={currentStats.searches.toString()} trend="Live" />
          <MetricCard icon={<Cpu className="text-yellow-400" />} title="Memory Usage" value={`${currentStats.memory}%`} trend="Live" />
        </div>

        {/* Charts Grid */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Active Searches & Indexing Chart */}
          <div className="p-6 rounded-2xl bg-[#161b22] border border-gray-800">
            <h3 className="text-lg font-semibold text-gray-200 mb-6 flex items-center gap-2">
              <Activity size={18} className="text-blue-400" />
              Active Searches & Indexing Rate
            </h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" vertical={false} />
                  <XAxis dataKey="time" stroke="#718096" fontSize={12} tickMargin={10} />
                  <YAxis stroke="#718096" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0d1117', borderColor: '#2d3748', borderRadius: '8px' }}
                    itemStyle={{ color: '#e2e8f0' }}
                  />
                  <Line type="monotone" dataKey="searches" name="Searches" stroke="#3b82f6" strokeWidth={2} dot={false} activeDot={{ r: 6 }} />
                  <Line type="monotone" dataKey="indexing" name="Files Indexed" stroke="#10b981" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Memory Usage Chart */}
          <div className="p-6 rounded-2xl bg-[#161b22] border border-gray-800">
            <h3 className="text-lg font-semibold text-gray-200 mb-6 flex items-center gap-2">
              <HardDrive size={18} className="text-yellow-400" />
              Memory & CPU Usage
            </h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <defs>
                    <linearGradient id="colorMemory" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#eab308" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#eab308" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" vertical={false} />
                  <XAxis dataKey="time" stroke="#718096" fontSize={12} tickMargin={10} />
                  <YAxis stroke="#718096" fontSize={12} domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0d1117', borderColor: '#2d3748', borderRadius: '8px' }}
                    itemStyle={{ color: '#e2e8f0' }}
                  />
                  <Area type="monotone" dataKey="memory" name="Memory (%)" stroke="#eab308" fillOpacity={1} fill="url(#colorMemory)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

function MetricCard({ icon, title, value, trend }: { icon: React.ReactNode, title: string, value: string, trend: string }) {
  return (
    <div className="p-5 rounded-2xl bg-[#161b22] border border-gray-800 flex items-start justify-between">
      <div>
        <p className="text-gray-400 text-sm font-medium mb-1">{title}</p>
        <h4 className="text-2xl font-bold text-gray-100">{value}</h4>
      </div>
      <div className="flex flex-col items-end gap-2">
        <div className="w-10 h-10 rounded-lg bg-[#0d1117] border border-gray-800 flex items-center justify-center">
          {icon}
        </div>
        <span className="text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded">
          {trend}
        </span>
      </div>
    </div>
  );
}
