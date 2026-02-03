import { useState } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import { Home, FileText, TrendingUp, Archive, Settings, Menu, X } from 'lucide-react'
import HomePage from './pages/Home'
import ArticlesPage from './pages/Articles'
import AnalysisPage from './pages/Analysis'
import AnalysisList from './pages/AnalysisList'
import ArchivePage from './pages/Archive'
import SettingsPage from './pages/Settings'

function App() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 移动端顶部栏 */}
      <div className="lg:hidden fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50">
        <div className="flex items-center justify-between p-4">
          <div>
            <h1 className="text-xl font-bold text-gray-900">NewsGap</h1>
            <p className="text-xs text-gray-500">信息差情报工具</p>
          </div>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* 侧边栏 - 桌面端始终显示，移动端根据菜单状态显示 */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-40
        w-64 bg-white border-r border-gray-200
        transform transition-transform duration-300 ease-in-out
        lg:transform-none
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* 桌面端头部 */}
          <div className="hidden lg:block p-6">
            <h1 className="text-2xl font-bold text-gray-900">NewsGap</h1>
            <p className="text-sm text-gray-500">信息差情报工具</p>
          </div>

          {/* 移动端添加顶部间距 */}
          <div className="lg:hidden h-20"></div>

          <nav className="flex-1 px-4 space-y-1">
            <NavLink 
              to="/" 
              icon={<Home size={20} />} 
              label="首页" 
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <NavLink 
              to="/articles" 
              icon={<FileText size={20} />} 
              label="文章列表" 
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <NavLink 
              to="/analysis" 
              icon={<TrendingUp size={20} />} 
              label="分析结果" 
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <NavLink 
              to="/archive" 
              icon={<Archive size={20} />} 
              label="归档管理" 
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <NavLink 
              to="/settings" 
              icon={<Settings size={20} />} 
              label="设置" 
              onClick={() => setIsMobileMenuOpen(false)}
            />
          </nav>

          <div className="p-4 border-t border-gray-200">
            <p className="text-xs text-gray-500">Version 0.1.0</p>
          </div>
        </div>
      </aside>

      {/* 移动端遮罩层 */}
      {isMobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setIsMobileMenuOpen(false)}
        ></div>
      )}

      {/* 主内容区 */}
      <main className="flex-1 overflow-auto pt-16 lg:pt-0">
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
  onClick?: () => void
}

function NavLink({ to, icon, label, onClick }: NavLinkProps) {
  return (
    <Link
      to={to}
      onClick={onClick}
      className="flex items-center gap-3 px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
    >
      {icon}
      <span className="font-medium">{label}</span>
    </Link>
  )
}

export default App
