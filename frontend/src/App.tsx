import { Routes, Route, Link } from 'react-router-dom'
import { Home, FileText, TrendingUp, Archive, Settings } from 'lucide-react'
import HomePage from './pages/Home'
import ArticlesPage from './pages/Articles'
import AnalysisPage from './pages/Analysis'
import AnalysisList from './pages/AnalysisList'
import ArchivePage from './pages/Archive'
import SettingsPage from './pages/Settings'

function App() {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* 侧边栏 */}
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="flex flex-col h-full">
          <div className="p-6">
            <h1 className="text-2xl font-bold text-gray-900">NewsGap</h1>
            <p className="text-sm text-gray-500">信息差情报工具</p>
          </div>

          <nav className="flex-1 px-4 space-y-1">
            <NavLink to="/" icon={<Home size={20} />} label="首页" />
            <NavLink to="/articles" icon={<FileText size={20} />} label="文章列表" />
            <NavLink to="/analysis" icon={<TrendingUp size={20} />} label="分析结果" />
            <NavLink to="/archive" icon={<Archive size={20} />} label="归档管理" />
            <NavLink to="/settings" icon={<Settings size={20} />} label="设置" />
          </nav>

          <div className="p-4 border-t border-gray-200">
            <p className="text-xs text-gray-500">Version 0.1.0</p>
          </div>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/articles" element={<ArticlesPage />} />
          <Route path="/analysis" element={<AnalysisList />} />
          <Route path="/analysis/:id" element={<AnalysisPage />} />
          <Route path="/archive" element={<ArchivePage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  )
}

interface NavLinkProps {
  to: string
  icon: React.ReactNode
  label: string
}

function NavLink({ to, icon, label }: NavLinkProps) {
  return (
    <Link
      to={to}
      className="flex items-center gap-3 px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
    >
      {icon}
      <span className="font-medium">{label}</span>
    </Link>
  )
}

export default App
